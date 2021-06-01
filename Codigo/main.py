"""
Autores: Sebastian Aristondo, Daniel Gonzalez, Juan Carlos Bajan.
Modificacion: 31/05/2021
Descripcion: Programa que permite realizar una recomendacion de perros.
"""

from neo4j import GraphDatabase
from connection import *
import random


añesartnoc="Computologo"

"""
--------------------Terminos Y Condiciones--------------------
Para que el proceso de recomendacion se pueda llevar a cabo,
el usuario debe estar de acuerdo con ello y aceptar los
terminos y condiciones de la misma. Para ello se inicia
preguntandole al usuario si las acepta o no
--------------------------------------------------------------
"""
def TerminosYCondiciones():
    respuesta=""
    while respuesta=="":
        print("""----------------Terminos y Condicioness--------------- \n
        Este sistema de recomendación, requiere de información porporcionada por usted,
        esta sirve unicamente con el proposito de brindarle una recomendación acertada. Los datos
        que se obtiene son totalmente privados. El sistema de recomendación desea pedirle permiso 
        para utilizar el resultado del perro que se le recomienda para agregarlo a un ranking y asi 
        mejorar las recomendaciones \n ¿Acepta?        
        """)
        respuesta=input("Si/No \n")
        if respuesta.lower()=="si" or respuesta.lower()=="no":
            if respuesta.lower()=="si":
                return True
            elif respuesta.lower()=="si":
                return False
        else:
            respuesta=""



"""
---------------------    agregar     -------------------------
Con el fin de mejorar el sistema de recomendacion, se diseno
una opcion para agregar mas componentes al grafo. En esta opcion
el usuario ingresa (raza, comportamiento, espacio, tipo de pelo,
tamano, complexion corporal, actividad fisica, expectativa de vida,
hocico y orejas)
--------------------------------------------------------------
"""
def agregar(connection, db):
    #Se le solicita al usuario que ingrese una contrasena
    palabra=input("Por favor ingrese la palabra clave \n")
    if palabra == añesartnoc:
        # Se le solicita al usuario que ingrese la raza y las caracteristicas del nuevo perro
        raza=input("Ingrese el nombre de la raza del perro a agregar a la base de datos \n >")
        datos = {"Comportamiento":"", "Espacio":"","TipoPelo":"", "Tamano": "", "ComplexionCorporal":"","ActividadFisica":"","ExpectativaDeVida":"", "Hocico": "","Orejas":""}
        # El ciclo FOR recorre el diccionario datos y guarda la informacion que el usuario ingrese.
        for keys in datos:
            print("Seleccione la opcion con la que se siente más identificado según "+keys )
            dictionary = elementos(connection, db, keys)
            elec = eleccion(dictionary)
            datos[keys] = elec
        # Se le asigna un ranking de 0 porque al ser un dato nuevo, no se le ha recomendado a nadie
        datos["Ranking"]=0
        # Se envia el primer query para crear un perro
        query = '''
            CREATE (p:Perro{raza:"%s", ranking:'0'})
        '''%(raza)
        connection.query(query, db)
        # Se envia otro query uniendo al perro con sus caracteristicas. Se envia en estructura del codigo de cypher para que la plataforma entienda el query.
        query='''MATCH (p:Perro) WHERE p.raza = '%s'
                MATCH (p1:Comportamiento) WHERE p1.comportamiento = '%s' 
                MERGE (p) -[:Comportamiento]-> (p1) WITH p
                MATCH (p2:Espacio) WHERE p2.espacio = '%s'
                MERGE (p) -[:Espacio]->(p2) WITH p
                MATCH (p3:TipoPelo) WHERE p3.tipoPelo = '%s' 
                MERGE (p) -[:Espacio]->(p3) WITH p
                MATCH (p4:Tamano) WHERE p4.tamano = '%s' 
                MERGE (p) -[:Tamano]->(p4) WITH p
                MATCH (p5:ComplexionCorporal) WHERE p5.complexionCorporal = '%s' 
                MERGE (p) -[:ComplexionCorporal]->(p5) WITH p
                MATCH (p6:ActividadFisica) WHERE p6.actividadFisica = '%s'
                MERGE (p)-[:ActividadFisica]-> (p6) WITH p
                MATCH (p7:ExpectativaDeVida) WHERE p7.expectativaDeVida = '%s'
                MERGE (p)-[:ExpectativaDeVida]-> (p7) WITH p
                MATCH (p8:ExpectativaDeVida) WHERE p8.expectativaDeVida = '%s' 
                MERGE (p)-[:Hocico]-> (p8) WITH p
                MATCH (p9:Orejas) WHERE p9.orejas = '%s'
                MERGE (p)-[:Orejas]-> (p9) return p
            '''%(raza,datos['Comportamiento'],datos['Espacio'],datos['TipoPelo'],datos['Tamano'],datos['ComplexionCorporal'],datos['ActividadFisica'],datos['ExpectativaDeVida'],datos['Hocico'], datos['Orejas'])
        connection.query(query, db)
    else:
        #Si la contrasena es incorrecta se le indica al usuario
        print("Palabra clave incorrecta, Esta opción es unicamente para personal calificado")


"""
---------------------    quitar     --------------------------
Asi como se puede anadir un componente tambien se puede eliminar,
para esto se diseno una herramienta para eliminar comparando el nombre
que se ingreso con las razas almacenadas.
--------------------------------------------------------------
"""
def quitar(connection, db):
    #Se le solicita al usuario que ingrese una contrasena
    palabra=input("Por favor ingrese la palabra clave\n")
    if palabra == añesartnoc:
        condicion=True
        query = 'MATCH (n:Perro) return n.raza'
        temp = connection.query(query, db)
        i = 1
        dictionary = {}
        # Se hace un ciclo while para imprimir todos los perros del grafo y luego devolver el perro que el usuario haya ingresado
        while condicion:
            for elements in temp:
                dictionary[i] = elements['n.raza']
                print(f"{i}) {dictionary[i]}")
                i = i+1
            perro= input("Ingrese el numero del perro que desea eliminar")
            try:
                perro = int(perro)
                if perro<len(dictionary)+1:
                    query= 'MATCH (p:Perro{raza:"%s"}) detach delete p'%(dictionary[perro])
                    temp = connection.query(query, db)
                    condicion=False
                else:
                    #En caso que no se encuentre la raza, se le notifica al usuario
                    print("La opcion ingresada no existe")
            except:
                #En caso que no haya ingresado un numero, se le notifica al usuario
                print("Ingresar unicamente números")
    else:
        # En caso que haya ingresado una contrasena incorrecta se le notifica al usuario
        print("Palabra clave incorrecta, Esta opción es unicamente para personal calificado")
        

"""
-----------------    query ranking     -----------------------
Esta Funcion devuelve el perro con mayor ranking del grafo.
--------------------------------------------------------------
"""
def query_ranking(connection, query_result):
    perros = {}
    #Se almacena en un diccionario cada raza encontrada con su ranking
    for element in query_result:
        perros[element['p.raza']] = int(element['p.ranking'])

    #Se hace un sort para encontrar el ranking mas grande y su raza. Esto servira para hacer la recomendacion y actualizar el ranking del perro con un query.
    #El primer elemento de sort_dic es la raza con mayor ranking.
    sort_dict = dict(sorted(perros.items(), key=lambda item: item[1], reverse=True))
    first_key = list(sort_dict.keys())[0]
    first_value = list(sort_dict.values())[0]
    if TYC:
        first_value = first_value + 1
    query = '''
        MATCH (p:Perro {raza: '%s'}) SET p.ranking = '%s' RETURN p
    '''%(first_key, str(first_value))
    connection.query(query, db)
    return first_key


"""
-------------------    elementos     -------------------------
Esta Funcion devuelve un diccionario con los elementos segun
el tipo y el diferenciador que el usuario ingrese
--------------------------------------------------------------
"""
def elementos(connection, db, tipo):
    diferenciador = tipo[0:1].lower() + "" + tipo[1:len(tipo)]
    # Se envia el query a neo4j con los datos que ingreso el usuario
    query = f'MATCH (p:{tipo}) return p.{diferenciador}'
    temp = connection.query(query, db)
    i = 1
    dictionary = {}
    # Por cada elemento recibido, se agrega un valor al diccionario.
    for elements in temp:
        dictionary[i] = elements[f'p.{diferenciador}']
        i = i+1
    return dictionary


"""
-------------------    eleccion     --------------------------
Esta Funcion imprime el nodo con el que el usuario indico que
se identifico.
--------------------------------------------------------------
"""
def eleccion(dic):
    bandera=True
    while bandera:
        i = 1
        for keys in dic:
            print(str(i) + " " + dic[keys])
            i = i + 1
        elecop=input("\nLa opcion con la que mas me identifico es la numero:\n>")
        try:
            elecop= int(elecop)
            if elecop > len(dic):
                print(f"La opcion {elecop} no se encuentra entre las opciones")   
            else:
                return dic[elecop]
                bandera=False
        except ValueError:
            print("Porfavor ingrese la opción en formato de numero")



"""
---------------    aumentar ranking     ----------------------
Esta Funcion aumenta el ranking del perro recomendado cada vez
que se muestra al usuario.
--------------------------------------------------------------
"""
def aumentar_ranking(raza):
    query ='''
            MATCH (p:Perro{raza:"%s"}) return p.ranking'''%(raza)
    #result = 


"""
-------------------    resultado     -------------------------
Esta Funcion muestra al usuario el resultado obtenido por
la busqueda.
--------------------------------------------------------------
"""
def resultado(query):
    perros = []
    for elements in query:
        perros.append(elements['p.raza'])

    i = random.randint(0,len(perros)-1)
    return perros[i]
    

"""
----------------    ConsultaUsuario     ----------------------
Esta Funcion solicita al usuario las caracteristicas que 
desea que el su perro tenga, en base a esto se hace un query a
la base de datos de Neo4J y se le da una respuesta.
--------------------------------------------------------------
"""
def ConsultaUsuario(connection, db):
    datos = {"Comportamiento":"", "Espacio":"","TipoPelo":"", "Tamano": "", "ComplexionCorporal":"","ActividadFisica":"","ExpectativaDeVida":"", "Hocico": "","Orejas":""}
    # Se solicita al usuario la opcion que desee segun la caracteristica
    for keys in datos:
        print("Seleccione la opcion con la que se siente más identificado según "+keys)
        dictionary = elementos(connection, db, keys)
        elec = eleccion(dictionary)
        datos[keys] = elec
    recomendacion = ""
    # Se le envia a la base de datos el query con las caracteristicas que selecciono el usuario
    query ='''
            MATCH (p:Perro)-[:Comportamiento]->(p1:Comportamiento{comportamiento:"%s"}),
            (p)-[:Espacio]-> (p4:Espacio{espacio:"%s"}),
            (p)-[:TipoPelo]-> (p5:TipoPelo{tipoPelo:"%s"}),
            (p)-[:Tamano]-> (p6:Tamano{tamano:"%s"}),
            (p)-[:ComplexionCorporal]-> (p7:ComplexionCorporal{complexionCorporal:"%s"}),
            (p)-[:ActividadFisica]-> (p8:ActividadFisica{actividadFisica:"%s"}),
            (p)-[:ExpectativaDeVida]-> (p9:ExpectativaDeVida{expectativaDeVida:"%s"}),
            (p)-[:Hocico]-> (p10:Hocico{hocico:"%s"}),
            (p)-[:Orejas]-> (p11:Orejas{orejas:"%s"}) return p.raza, p.ranking
           '''%(datos['Comportamiento'],datos['Espacio'],datos['TipoPelo'],datos['Tamano'],datos['ComplexionCorporal'],datos['ActividadFisica'],datos['ExpectativaDeVida'],datos['Hocico'], datos['Orejas'])
    query_result = connection.query(query, db)
    #Si se encuentra entonces se muestra al usuario.
    if query_result:
        recomendacion = query_ranking(connection, query_result)
    #En caso que no se encuentren, entonces se realiza un query con menos opciones
    elif not query_result:
        query ='''MATCH (p:Perro)-[:Comportamiento]->(p5:Comportamiento{comportamiento:"%s"}),
            (p)-[:Espacio]-> (p2:Espacio{espacio:"%s"}),
            (p)-[:Tamano]-> (p3:Tamano{tamano:"%s"}) return p.raza, p.ranking
            '''%(datos['Comportamiento'],datos['Espacio'],datos['Tamano'])
        query_result = connection.query(query, db)
        if query_result:
            recomendacion = query_ranking(connection, query_result)
        #En caso que no se encuentre de nuevo, se vuelve a hacer un query solo con el comportamiento.
        elif not query_result:
            query ='''MATCH (p:Perro)-[:Comportamiento]->(p5:Comportamiento{comportamiento:"%s"})  return p.raza, p.ranking
                '''%(datos['Comportamiento'])
            query_result = connection.query(query, db)
            recomendacion = query_ranking(connection, query_result)
    
    return recomendacion



#Conexiones a base de datos.
conn = Neo4jConnection(uri="bolt://localhost:####", user="neo4j", pwd="1234")
db = 'neo4j'
#temp = elementos(conn, db, "Personalidad", "Personalidad")
#print(temp)

#-----------------------Inicio del menu--------------------------------
print("¡Bienvenidos al sistema de recomendación de perros!")
perro = '''
░░░░░░▄█▄█░░░░░▄░░░░░░
░░░░██████░░░░░░█░░░░░
░░░░░░███████████░░░░░
▒▒▒▒▒▒█▀▀█▀▀██▀██▒▒▒▒▒
▒▒▒▒▒▄█▒▄█▒▒▄█▒▄█▒▒▒▒▒
'''
print(perro)

perro = '''
    ___
 __/_  `.  .-"""-.
 \_,` | \-'  /   )`-')
  "") `"`    \  ((`"`
 ___Y  ,    .'7 /|
(_,___/...-` (_/_/ 
'''

continuar=True
TYC=TerminosYCondiciones()
while(continuar):
    print("\n1)Realizar recomendación")
    print("2)Agregar a la base de datos")
    print("3)Eliminar de la base de datos")
    print("4)Salir\n")
    op1=input("¿Que opción desea realizar?\n>")
    try:
        op1=int (op1)
        
    except ValueError:
        print("Opcion no valida")

    if op1==1:
        RecomendacionExitosa=ConsultaUsuario(conn, db)
        print(f"Se le recomienda conseguir un perro de raza: {RecomendacionExitosa}")
        print(perro)
    elif op1==2:#Agregar a la base de datos
        agregar(conn,db)
    elif op1==3:#Quitar de la base de datos
        quitar(conn,db)
    elif op1==4:
        continuar=False
        print("Muchas gracias por utilizar el sistema de recomendacion") 

