from django.shortcuts import render
from django.db import connection
from .models import Pokemons

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def index(request):
    return render(request, 'index.html')


def add_pokemon(request):
    if request.method == 'POST' and request.POST:
        new_name = request.POST["name"]
        new_type = request.POST["type"]
        new_generation = request.POST["generation"]
        new_legendary = request.POST["legendary"]
        new_hp = request.POST["hp"]
        new_attack = request.POST["attack"]
        new_defense = request.POST["defense"]
        new_pokemon = Pokemons(name=new_name, type=new_type, generation=new_generation,
                               legendary=new_legendary, hp=new_hp, attack=new_attack,
                               defense=new_defense)
        new_pokemon.save()
    return render(request, 'add_pokemon.html')


def query_results(request):
    with connection.cursor() as cursor:
        # 1
        cursor.execute("""Select P.Generation as generation, P.Name as pokemon
                        FROM Pokemons as P
                        WHERE p.Legendary = 'true' AND HP + Defense + Attack = (
                            Select MAX(p1.HP + p1.Defense + p1.Attack)
                            from Pokemons as p1
                            WHERE p1.Generation = p.Generation
                            group by P1.Generation
                        )
                        ORDER BY p.Generation
                        """)
        sql_res1 = dictfetchall(cursor)
        # 2
        cursor.execute("""SELECT p.Name as pokemon, p.Type as type
                            from Pokemons as p
                            EXCEPT (SELECT p1.Name, P1.Type
                                    from Pokemons as P1, Pokemons as P2
                                    where P1.Type = p2.Type and p1.Name != p2.Name and (P1.Attack <= P2.Attack or P1.Defense <= P2.Defense or P1.HP <= P2.HP))
                                                    """)
        sql_res2 = dictfetchall(cursor)

        # 4
        cursor.execute("""
                        SELECT TOP 1 Type as type, ROUND(AVG(insta),2) average
                            FROM (SELECT Type, CAST(ABS(Defense - Attack) AS FLOAT) AS insta
                                    FROM Pokemons) InstaType
                            GROUP BY Type
                            ORDER BY average DESC""")
        sql_res4 = dictfetchall(cursor)
        # 3
        if request.method == 'POST' and request.POST:
            new_attack = int(request.POST["attack"])
            new_count = int(request.POST["count"])
            cursor.execute("""SELECT DISTINCT t.Type as type
                                from (
                                                    Select Type, MAX(Attack) as max, count(type) as size
                                                    from Pokemons
                                                    GROUP BY Type
                                    ) as t
                                WHERE t.max > %s AND t.size > %s
                                ORDER BY t.Type
                            """, [new_attack, new_count])
            sql_res3 = dictfetchall(cursor)
        else:
            cursor.execute("""SELECT DISTINCT Type as type
                                from Pokemons
                                WHERE Type = '#'
                            """)
            sql_res3 = dictfetchall(cursor)
    return render(request, 'query_results.html', {'sql_res1':sql_res1, 'sql_res2':sql_res2, 'sql_res3':sql_res3, 'sql_res4':sql_res4})
