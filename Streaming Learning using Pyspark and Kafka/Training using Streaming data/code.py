from pyspark.sql import SparkSession
from pyspark.sql import functions as f
from pyspark.sql.types import *
import os
import time
from pyspark.ml.feature import StringIndexer
from pyspark.ml.feature import OneHotEncoder
from pyspark.ml.feature import VectorAssembler, SQLTransformer
from pyspark.ml import Pipeline
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# saving current time for profiling
t0 = time.time()

# Configuring spark connection and streaming
SCHEMA = StructType([StructField("Arrival_Time", LongType(), True),
                     StructField("Creation_Time", LongType(), True),
                     StructField("Device", StringType(), True),
                     StructField("Index", LongType(), True),
                     StructField("Model", StringType(), True),
                     StructField("User", StringType(), True),
                     StructField("gt", StringType(), True),
                     StructField("x", DoubleType(), True),
                     StructField("y", DoubleType(), True),
                     StructField("z", DoubleType(), True)])

spark = SparkSession.builder.appName('demo_app') \
    .config("spark.kryoserializer.buffer.max", "512m") \
    .config("spark.driver.memory",'9g')\
    .getOrCreate()


os.environ['PYSPARK_SUBMIT_ARGS'] = \
    "--packages=org.apache.spark:spark-sql-kafka-0-10_2.12:2.4.8,com.microsoft.azure:spark-mssql-connector:1.0.1"
kafka_server = 'dds2020s-kafka.eastus.cloudapp.azure.com:9092'

# Importing initial static dataset
topic = "static"
static_df = spark.read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_server) \
    .option("subscribe", topic) \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", False) \
    .option("maxOffsetsPerTrigger", 1000) \
    .load() \
    .select(f.from_json(f.decode("value", "US-ASCII"), schema=SCHEMA).alias("value")).select("value.*").sample(0.5)

# Pipeline transforms data sets by indexing the activities and users.
# Next we do One Hot Encoding to disregard order of users. We then assemble into a vector to be used in model,
# and drop the rest of the columns using SELECT projection.
transformer_pipeline = Pipeline(stages=[
    StringIndexer(inputCol="gt", outputCol="gt_idx", handleInvalid='keep'),
    StringIndexer(inputCol="User", outputCol="User_idx", handleInvalid='keep'),
    OneHotEncoder(inputCol="User_idx", outputCol="User_vec"),
    VectorAssembler(inputCols=[ "Index", 'User_vec', 'x', 'y', 'z'], outputCol="features"),
    SQLTransformer(statement="SELECT features, gt_idx FROM __THIS__")
])

# Droping unused columns in the static dataframe. Training the RandomForest Model for the first time, and fitting the
# pipeline we configured.
static_new = static_df.select("Index", 'User', 'x', 'y', 'z', 'gt').sample(0.5)
model_dt = RandomForestClassifier(labelCol="gt_idx", featuresCol="features", numTrees=10, maxDepth=30, minInstancesPerNode=1000)

print('importing static_df and creating model, time: %.2f' % (time.time() - t0))
transformer = transformer_pipeline.fit(static_df)
model_dt_fitted = model_dt.fit(transformer.transform(static_df))
evaluator = MulticlassClassificationEvaluator(labelCol='gt_idx', predictionCol="prediction", metricName="accuracy")

# The function activates the trained pipeline and model on the dataframe received. we will use it on the incoming
# streaming data.
def evaluate_batch(df):
    return model_dt_fitted.transform(transformer.transform(df)).select('prediction', 'gt_idx')

# Initializing the streaming data.
topic = "activities"
streaming = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_server) \
    .option("subscribe", topic) \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", False) \
    .option("maxOffsetsPerTrigger", 4000) \
    .option("minOffsetsPerTrigger", 2000) \
    .load() \
    .select(f.from_json(f.decode("value", "US-ASCII"), schema=SCHEMA).alias("value")).select("value.*")

# Streaming query - we use select to omit unused columns.
stream_df = streaming \
    .select("Index", 'User', 'x', 'y', 'z', 'gt')\
    .writeStream \
    .queryName("stream_df") \
    .format("memory") \
    .outputMode("append")\
    .start()

# new_data df is a sink to be inserted into the function.
print('waiting for steaming to appear, time: %.2f' % (time.time() - t0))
new_data = spark.sql("SELECT * FROM stream_df")
time.sleep(5)

# If sink is empty, wait.
if new_data.count() < 10000:
    time.sleep(5)
print("STREAM IS NOT EMPTY, time: %.2f" % (time.time() - t0))

# For loop will predict on any incoming data. every 5 iterations we will merge some of the data we received by streaming
# with the old data by random, and then from that union we will sample again to minimize space complexity,
# and generalize the model by using random data.
for i in range(11):
    print("iter: %d, accuracy: %.3f, time: %.2f" % (i, evaluator.evaluate(evaluate_batch(new_data)), time.time() - t0))

    # Checking if we predicted enough rows.
    if (i+1)%11 == 0:
        test_count = new_data.count()
        print("streaming data count until now: %d" % test_count)
        if test_count>576000:
            break
    # update the data used to train the model. train the model and the pipeline using the new data.
    if (i+1) % 5 == 0:
        data_to_add = new_data.sample(1/i)
        static_new = static_new.union(data_to_add).distinct().sample(0.7)
        transformer = transformer_pipeline.fit(static_df)
        model_dt_fitted = model_dt.fit(transformer.transform(static_df))
    # waiting to let more data accumulate in the sink.
    time.sleep(3)