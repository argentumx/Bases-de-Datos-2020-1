import cx_Oracle
import pandas
from tabulate import tabulate
import time
from simple_term_menu import TerminalMenu
from random import choice, randint

'''TO DO:
generar la fecha random al poblar la tabla
ahora no es posible ver el estado None y no puedo buscar por el None

en update tengo que re-calcular la prioridad (llamar a la funcion calcular prioridad)
quiza agregar casos de que estado debe estar en lista de estados para pillar errores?
falta read
falta delete - ver que hago en caso de multiples repeticiones de mismo pokemon
1 trigger
1 view
insert para legendarios - no puede haber mas que un legendario de mismo nombre
comentar todo todillo
'''

def print_table(hdrs, fmt='psql'):
	res = cur.fetchall()
	print(tabulate(res, headers=hdrs, tablefmt=fmt))

def print_poyo():
	poyo = "SELECT * FROM poyo"
	cur.execute(poyo)
	print_table(hdrs_poyo)

def print_sansanito():
	ssn = "SELECT * FROM sansanito"
	cur.execute(ssn)
	print_table(hdrs_sansanito)

#CRUD
#CREATE - hace insercion de registro
def create():
	print("hola")

#READ - lee registros con PK u otro parametro
def read():
	# leer todo
	# leer que columnas
	# leer de que tabla
	# ordenar por cual valor
	# de que modo ordeno
	print("hola")
	
#UPDATE - cambia el registro usando su PK con un WHERE
def update():
	# solo modifica hpactual, estado
	# se recacula la prioridad
	print("hola")

#DELETE - borra la fila con WHERE especifico
def delete(nombre):
	print("SE BORRARA EL REGISTRO DE", nombre)
	del_query = """
				DELETE FROM sansanito
				WHERE nombre= :1"""
	cur.execute(hptot_query, [nombre])

#Query

def insert_aux(n, actual, e, f, prio):
	poyo_datos = """
				SELECT pokedex, type1, type2, hptotal, legendary 
				FROM poyos
				WHERE nombre = :1"""
	cur.execute(poyo_datos, [n])
	data_poyo = cur.fetchall() #lista con tupla [(pokedex, tipo1, tipo2, hptotal, legendary)]
	#saco la primera tupla
	data_poyo = data_poyo[0]
	#desempaqueto la tupla
	pokedex, t1, t2, total, l = data_poyo
	ins_query = """
				INSERT INTO sansanito (pokedex, nombre, type1, type2, hpactual, hpmax, legendary, estado, ingreso, prioridad)
				VALUES (:1, :2, :3, :4, :5, :6, :7, :8, to_date(:9, 'DD/MM/YY HH:MI'), :10)""" 
				
	cur.execute(ins_query, [pokedex, n, t1, t2, actual, total, l, e, f, prio])
				


#hdrs_poyo = ['pokedex', 'nombre', 'type1', 'type2', 'hptotal', 'legendary']
#hdrs_sansanito = ['id', 'pokedex', 'nombre', 'type1','type2', 'hpactual', 'hptotal','legendary', 'estado', 'ingreso', 'prioridad']

def calculate_priority(n, hpactual, estado):
	hptotal_query =  """SELECT hptotal FROM poyo WHERE nombre = :1""" 
	cur.execute(hptotal_query, [n])
	hptotal = cur.fetchall()
	# a pesar de que se dice que datos que ingresaran seran los correctos
	# agrego el condicional...
	if hptotal[0][0] < hpactual:
		print("Datos de hp actual inconsistentes con el hp maximo. Intente de nuevo.")
		print("Devolviendo al menu principal...")
		time.sleep(3)
		return
	prioridad = hptotal[0][0] - hpactual + bool(estado) * 10
	return prioridad

def insertar_pokemon(n, hpactual, estado, fecha):
	leg_query  = """SELECT legendary FROM poyo WHERE nombre = :1"""
	cur.execute(leg_query, [n])
	tipo = cur.fetchall()
	if tipo == []: #no se encontro que es legenadario, ergo el pkm no existe
		print("Revise su pokedex - el pokemon ingresado no existe.")
		print("Devolviendo al menu principal...")
		time.sleep(3)
		return
	lowest = """SELECT nombre, prioridad
			FROM sansanito
			WHERE legendary=%d AND ROWNUM = 1 
			ORDER BY prioridad ASC """ % (tipo[0][0])

	cur.execute("""SELECT COUNT(*) FROM sansanito WHERE legendary=0""")
	normales = cur.fetchall()
	cur.execute("""SELECT COUNT(*) FROM sansanito WHERE legendary=1""")
	legendarios = cur.fetchall()
	total_registros =  normales[0][0] + 5 * legendarios[0][0]
	prioridad = calculate_priority(n, hpactual, estado)
	#legenadrio
	if tipo[0][0]:
		#caso 1 - quepa 
		if total_registros + 5 <= 50:
			insert_aux(n, hpactual, estado, fecha, prioridad)
			print_sansanito()		
		else:
			#no quepa
			cur.execute(lowest)
			res = cur.fetchall()
			prio_lowest = res[0][1]
			nom_lowest = res[0][0]
			# en caso de que sea igual, ignorar y dejar el que estaba
			if prioridad > prio_lowest:
				delete(nom_lowest)
	else:
		#caso 1 - quepa 
		if total_registros + 1 <= 50:
			insert_aux(n, hpactual, estado, fecha, prioridad)
			print_sansanito()	
		else:
			# no quepa
			cur.execute(lowest)
			res = cur.fetchall()
			prio_lowest = res[0][1]
			nom_lowest = res[0][0]
			# en caso de que sea igual, ignorar y dejar el que estaba
			if prioridad > prio_lowest:
				delete(nom_lowest)

#==================================================QUERIES================================================================
#LIMIT X no funciona en 11g, asi que se uso WHERE ROWNUM <=  / = X
# Los 10 pokemon con mayor prioridad
def maxprio_sansanito():
	cur.execute("""
				SELECT * FROM
				(SELECT nombre, prioridad
				FROM sansanito
				ORDER BY prioridad DESC)
				WHERE ROWNUM <= 10
				"""
				)

	print_table([hdrs_sansanito[2],hdrs_sansanito[-1]])

# Los 10 pokemon con menor prioridad
def minprio_sansanito():
	cur.execute("""
				SELECT * FROM
				(SELECT nombre, prioridad
				FROM sansanito
				ORDER BY prioridad ASC)
				WHERE ROWNUM <= 10
				""")
	print_table([hdrs_sansanito[2],hdrs_sansanito[-1]])

#los de estado especifico, incluyendo los None 
def estado_sansanito(estado):
	cur.execute("""SELECT nombre
				FROM sansanito
				WHERE estado = '%s'""" % (estado)
				)
	print_table([hdrs_sansanito[2],hdrs_sansanito[8]])

#los legendarios
def legendarios_sansanito():
	cur.execute("""
				SELECT nombre
				FROM sansanito
				WHERE legendary = 1
				""")
	print_table([hdrs_sansanito[2],hdrs_sansanito[-4]])

#el mas antiguo
def antiguedad_sansanito():
	cur.execute("""
				SELECT * FROM
				(SELECT nombre
				FROM sansanito
				ORDER BY ingreso ASC)
				WHERE ROWNUM <= 1
				""")
	print_table([hdrs_sansanito[2], hdrs_sansanito[-2]])

#el mas repetido
def repetido_sansanito():
	cur.execute("""
				SELECT * FROM
				(SELECT nombre
				FROM sansanito
				GROUP BY nombre
				ORDER BY COUNT(*) DESC)
				WHERE ROWNUM <= 1
				""")
	print_table(hdrs_sansanito)

def ordenado_sansanito(orden):
	cur.execute("""
				SELECT nombre, hpactual, hpmax, prioridad
				FROM sansanito
				ORDER BY prioridad %s""" % (orden)
				)
	print_table(hdrs_sansanito)

#==================================================QUERIES================================================================

#===================================================CREAR TABLA POYO======================================================
def ctable_poyos(archive="pokemon."):
	#quito espacios y no agrego _ por convencion (_ para relaciones y no atributos)
	cur.execute("DROP TABLE poyo")
	cur.execute("CREATE TABLE poyo (\
			pokedex INT,\
			nombre VARCHAR(40) NOT NULL PRIMARY KEY,\
			type1 VARCHAR(20),\
			type2 VARCHAR(20),\
			hptotal INT,\
			legendary NUMBER(1))"
			)
	connection.commit()
	# uso NUMBER(1) en vez de BOOLEAN para representar los booleanos
	# uso usecols que guarda solo algunas columnas
	pkmn = pandas.read_csv('pokemon.csv',sep=",",usecols=(0, 1, 2, 3 , 4, 12))
	# leer fila por fila para pillar True/False y NaN
	add_row_pkmn = ("INSERT INTO poyo "
		   "(pokedex, nombre, type1, type2, hptotal, legendary) "
		   "VALUES (:1,:2,:3,:4,:5,:6)")
	for d in pkmn.values:
		t2 = d[3]
		bln = 0
		if not isinstance(t2, str):
			#caso nan
			t2 = ""
		if d[-1] == True:
			bln = 1
		row_pkmn = [int(d[0]), d[1], d[2], t2, int(d[4]), bln]
		cur.execute(add_row_pkmn, row_pkmn)
		connection.commit()

#===================================================CREAR TABLA POYO======================================================


#===================================================CREAR TABLA SANSANITO=================================================
def ctable_sansanito():
	cur.execute("DROP TABLE sansanito")
	cur.execute("""
				CREATE TABLE sansanito(
				id NUMBER NOT NULL PRIMARY KEY,
				pokedex INT,
				nombre VARCHAR(40),
				type1 VARCHAR(20),
				type2 VARCHAR(20),
				hpactual INT,
				hpmax INT,
				legendary  NUMBER(1),
				estado VARCHAR(30),
				ingreso DATE,
				prioridad INT)"""
				)
	
	# Como Oracle 11g no posee valor autoincrementable (existe desde 12C)
	# El trigger se encarga de ello.
	cur.execute("""	
				CREATE SEQUENCE SANS_SEQ
				START WITH 1""")

	cur.execute("""CREATE OR REPLACE TRIGGER SANS_TRG
				BEFORE INSERT ON sansanito
				FOR EACH ROW
				BEGIN
				SELECT SANS_SEQ.NEXTVAL
				INTO :new.id
				FROM dual;
				END;
				"""
				)
	
	connection.commit()


#===================================================CREAR TABLA SANSANITO=================================================
def poblar_sansanito(n):
	cur.execute("""
				SELECT nombre
				FROM poyo""")
	nombres = cur.fetchall() #una lista de nombres, super grande
	for i in range(n):
		nombre_elegido = choice(nombres)[0] #elige nombre random de pokemon, pero existente
		print(nombre_elegido)
		estado = choice(estados_permitidos) #elige estado incluyendo el None
		hptot_query = """
					SELECT hptotal
					FROM poyo
					WHERE nombre = :1"""
		cur.execute(hptot_query, [nombre_elegido])
		hpmax = cur.fetchall()
		print(hpmax)
		hpactual = randint(0, hpmax[0][0]) #genera hpactual que no sea mayor que hpmax
		insertar_pokemon(nombre_elegido,hpactual, estado, "06/09/20 4:20")
		print("Ingrese X seguir")
		condicion = input()
		while(condicion != "X" and condicion != "x"):
			condicion = input()




# MENU
#=========================================================================

#Headers globales
hdrs_poyo = ['pokedex', 'nombre', 'type1', 'type2', 'hptotal', 'legendary']
hdrs_sansanito = ['id', 'pokedex', 'nombre', 'type1',\
				'type2', 'hpactual', 'hpmax',\
				'legendary', 'estado', 'ingreso', 'prioridad']
estados_permitidos = ['Envenenado', 'Paralizado', 'Quemado', 'Dormido', 'Congelado', None]

def main():
	main_menu_title = "  BIENVENIDO AL SANSANITO POKEMON. QUE DESEA HACER?\n"
	main_menu_items = ["Crear un registro", "Ingresar un pokemon", "Buscar en tabla (read)", "Opciones especiales de busqueda",\
						"Cambiar datos de pokemon ingresado (update)",\
						"Ver la tabla Poyo", "Ver la tabla Sansanito Pokemon","Salir"]
	main_menu_cursor = "> "
	main_menu_cursor_style = ("fg_red", "bold")
	main_menu_style = ("bg_purple", "fg_yellow")
	main_menu_exit = False

	main_menu = TerminalMenu(menu_entries=main_menu_items,
							 title=main_menu_title,
							 menu_cursor=main_menu_cursor,
							 menu_cursor_style=main_menu_cursor_style,
							 menu_highlight_style=main_menu_style,
							 cycle_cursor=True,
							 clear_screen=True)

	while not main_menu_exit:
		main_sel = main_menu.show()
		submenu_flag = True
		if main_sel == 0 or main_sel == 1:
			nombre = input("Ingrese el nombre de pokemon: ")
			hp_actual = int(input("Ingrese HP actual de pokemon: "))
			estado = input("Ingrese el estado. Si el pokemon no tiene estado, ingrese X: ")
			if estado.upper() == "X":
				estado = None
			fecha = input("Ingrese la fecha en formato DD/MM/YY HH:MM (ej 06/09/20 4:20): ")
			submenu_flag = False
			insertar_pokemon(nombre, hp_actual, estado, fecha)

		elif main_sel == 2:
			menu1_title = "BUSQUEDA EN SANSANITO POKEMON. ELIGA UNA OPCION.\n"
			menu1_items = ["Busqueda por un campo", "Salir"]
			menu1 = TerminalMenu(menu_entries=menu1_items,
							 title=menu1_title,
							 menu_cursor=main_menu_cursor,
							 menu_cursor_style=main_menu_cursor_style,
							 menu_highlight_style=main_menu_style,
							 cycle_cursor=True,
							 clear_screen=True)

			time.sleep(5)
		elif main_sel == 3:
			#total de opciones: 8
			menu2_title = "BUSQUEDA ESPECIAL EN SANSANITO POKEMON. ELIGA UNA OPCION.\n"
			menu2_items = ["10 pokemon con mayor prioridad", "10 pokemon con menor prioridad",\
			"Pokemon con estado especifico", "Pokemon legendarios ingresados",\
			"Pokemon que lleva mas tiempo ingresado", "Pokemon mas repetido",\
			"Pokemon ingresados, ordenados por su prioridad", "Salir"]
			menu2 = TerminalMenu(menu_entries=menu2_items,
								title=menu2_title,
								menu_cursor=main_menu_cursor,
								menu_cursor_style=main_menu_cursor_style,
								menu_highlight_style=main_menu_style,
								cycle_cursor=True,
								clear_screen=True)
			while submenu_flag:
				menu2_sel = menu2.show()
				if menu2_sel == 0:
					maxprio_sansanito()
					print("Ingrese X para volver al MENU PRINCIPAL.")
					condicion = input()
					while(condicion != "X" and condicion != "x"):
						condicion = input()
				# 10 con menor prioidad
				elif menu2_sel == 1:
					minprio_sansanito()
					print("Ingrese X para volver al MENU PRINCIPAL.")
					condicion = input()
					while(condicion != "X" and condicion != "x"):
						condicion = input()
				# filtrado por estado
				elif menu2_sel == 2:
					print("NOTA: Estados disponibles son: Envenenado, Paralizado, Quemado, Dormido, Congelado")
					print("Para ver pokemons sin estado, ingrese X.\n")
					estado = input("Ingrese un estado para filtrar los datos: ")
					if estado.upper() == "X":
						estado = None
					estado_sansanito(estado)
					print("Ingrese X para volver al MENU PRINCIPAL.")
					condicion = input()
					while(condicion != "X" and condicion != "x"):
						condicion = input()
				# los legendarios ingresados
				elif menu2_sel == 3:
					legendarios_sansanito()
					print("Ingrese X para volver al MENU PRINCIPAL.")
					condicion = input()
					while(condicion != "X" and condicion != "x"):
						condicion = input()
				# el mas antiguo
				elif menu2_sel == 4:
					antiguedad_sansanito()
					print("Ingrese X para volver al MENU PRINCIPAL.")
					condicion = input()
					while(condicion != "X" and condicion != "x"):
						condicion = input()
				# pokemon mas repetido
				elif menu2_sel == 5:
					repetido_sansanito()
					print("Ingrese X para volver al MENU PRINCIPAL.")
					condicion = input()
					while(condicion != "X" and condicion != "x"):
						condicion = input()
				# ordenados por prioidad
				elif menu2_sel == 6:
					orden = int(input("Ingrese 1 si desea el orden DESCENDIENTE, 0 en caso contrario: "))
					if orden:
						ordenado_sansanito("DESC")
						print("Ingrese X para volver al MENU PRINCIPAL.")
						condicion = input()
						while(condicion != "X" and condicion != "x"):
							condicion = input()
					else:
						ordenado_sansanito("ASC")
						print("Ingrese X para volver al MENU PRINCIPAL.")
						condicion = input()
						while(condicion != "X" and condicion != "x"):
							condicion = input()
				elif menu2_sel == 7:
					submenu_flag = False
		elif main_sel == 4:
			menu3_title = "CAMBIAR DATOS DE UN POKEMON INGRESADO. ELIGA UNA OPCION.\n"
			menu3_items = ["Cambiar un solo campo", "Cambiar varios campos", "Salir"]
			menu3 = TerminalMenu(menu_entries=menu3_items,
							title=menu3_title,
							menu_cursor=main_menu_cursor,
							menu_cursor_style=main_menu_cursor_style,
							menu_highlight_style=main_menu_style,
							cycle_cursor=True,
							clear_screen=True)
		#muestra la tabla de poyo, tanto tiempo como lo quiere el usuario
		elif main_sel == 5:
			print_poyo()
			print("Ingrese X para volver al MENU PRINCIPAL.")
			condicion = input()
			while(condicion.upper() != "X"):
				condicion = input()
		#muestra la tabla de sansanito, tanto tiempo como lo quiere el usuario	
		elif main_sel == 6:
			print_sansanito()
			print("Ingrese X para volver al MENU PRINCIPAL.")
			condicion = input()
			while(condicion.upper() != "X"):
				condicion = input()
		#saliendo, quiero dropear todas las secuencias
		elif main_sel == 7:
			cur.execute("DROP SEQUENCE SANS_SEQ")
			main_menu_exit = True


if __name__ == "__main__":
	print("Conectando al Oracle...")
	connection = cx_Oracle.connect("argentum", "1234", "XE")
	cur = connection.cursor()
	print(">>>OK")
	print("Rellenando la Base de Datos...")
	ctable_poyos()
	print(">>>OK")
	print("Montando el edificio de Sansanito Pokemon...")
	print(">>>OK")
	cantidad =int(input("Cuantos pokemons desea generar en el Sansanito?: "))
	ctable_sansanito()
	poblar_sansanito(cantidad)
	print("Poblando Sansanito Pokemon...")
	print(">>>OK")
	print("Entrando al Sansanito Pokemon...")
	print_sansanito()
	time.sleep(3)
	print(">>>OK")
	main()

connection.close()
