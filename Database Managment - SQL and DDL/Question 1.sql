CREATE TABLE Country(
    cName VARCHAR(50) PRIMARY KEY,
    cCapital VARCHAR(50) UNIQUE,
    cLanguage VARCHAR(50),
    );


CREATE TABLE Instructors(
    iID INT PRIMARY KEY
        CHECK (iID > 0),
    iName VARCHAR(50),
    dateOfBirth DATE
        CHECK (dateofBirth < '01/01/2000'),
    iMail VARCHAR(50)
        CHECK (iMail LIKE '%@%'),
    iExperience VARCHAR(50) NOT NULL
        CHECK ((iExperience = 'beginner') or (iExperience = 'experienced')),
    iLovedCountry VARCHAR(50) NOT NULL,
    FOREIGN KEY (iLovedCountry) REFERENCES Country(cName)
        ON DELETE CASCADE,
    );


CREATE TABLE Attractions(
    aName VARCHAR(50),
    aCountry VARCHAR(50),
    aRating FLOAT NOT NULL
        CHECK (aRating >= 1 and aRating <= 5),
    aPrice FLOAT
        CHECK (aPrice >= 0),
    PRIMARY KEY (aName, aCountry),
        FOREIGN KEY (aCountry) REFERENCES Country(cName)
            ON DELETE CASCADE,
    );


CREATE TABLE Tours(
    tName VARCHAR(50) PRIMARY KEY,
    tDescription VARCHAR(50),
    tDays INT NOT NULL
        CHECK (tDays > 3),
    tMax INT NOT NULL
        CHECK (tMax >= 0),
    tourInstructorsID INT NOT NULL
        CHECK (tourInstructorsID > 0),
        FOREIGN KEY (tourInstructorsID) REFERENCES Instructors(iID)
                  ON DELETE CASCADE,
);

--Its not possible to check at the DDL level that each guide documented in the DB
-- is responsible for at least two trips


CREATE TABLE ToursDescriptionByDay(
    tName VARCHAR(50),
    aName VARCHAR(50),
    inDay INT,
        CHECK (inDay > 0),
    PRIMARY KEY (tName, aName,inDay),
        FOREIGN KEY (tName) REFERENCES Tours(tName)
            ON DELETE CASCADE,
);

--1.Its not possible to check at the DDL level that the inDay(the day number in the tour)
--is bigger then the max days of the tour.

--2.We cant reference aName(Attraction name in the tour) to the Attractions table,
-- because aName in Attractions is not UNIQUE