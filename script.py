from flask import Flask, jsonify, request
import pandas as pd
from pulp import *
import os

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

cwd = os.getcwd()
solverdir = './Cbc-2.7.5-win64-intel11.1/bin/cbc.exe'
solverdir = os.path.join(cwd, solverdir)
solver = COIN_CMD(path=solverdir)


# API 1: Minimización de Contrataciones
@app.route('/minimizar_contratacion', methods=['GET', 'POST'])
def problema_1():

	# The class has been initialize, and x, hours and objective fuction defined
	model = LpProblem("Minimize_Staffing", LpMinimize)

	hours = list(range(10))

	# Define Decision Variables
	x = LpVariable.dicts('saws_', hours, lowBound=0, cat="Integer")

	# Define Objective
	model += lpSum([x[i] for i in x])

	# JSON de Ejemplo para enviar por POSTMAN
	'''
	{
	"0":7,
	"1":7,
	"2":7,
	"3":6,
	"4":5,
	"5":6,
	"6":6,
	"7":7,
	"8":7,
	"9":6
	}
	'''

	#Recibir el JSON de postman
	demanda = request.get_json()
	print(demanda['0'])

	# Define Constraints
	model += x[0] + x[2] + x[3] + x[4] + x[5] + x[7] + x[8] + x[9] >= demanda['0']
	model += x[0] + x[1] + x[3] + x[4] + x[5] + x[6] + x[8] + x[9] >= demanda['1']
	model += x[0] + x[1] + x[2] + x[4] + x[5] + x[6] + x[7] + x[9] >= demanda['2']
	model += x[0] + x[1] + x[2] + x[3] + x[5] + x[6] + x[7] + x[8] >= demanda['3']
	model += x[1] + x[2] + x[3] + x[4] + x[6] + x[7] + x[8] + x[9] >= demanda['4']
	model += x[0] + x[2] + x[3] + x[4] + x[5] + x[7] + x[8] + x[9] >= demanda['5']
	model += x[0] + x[1] + x[3] + x[4] + x[5] + x[6] + x[8] + x[9] >= demanda['6']
	model += x[0] + x[1] + x[2] + x[4] + x[5] + x[6] + x[7] + x[9] >= demanda['7']
	model += x[0] + x[1] + x[2] + x[3] + x[5] + x[6] + x[7] + x[8] >= demanda['8']
	model += x[1] + x[2] + x[3] + x[4] + x[6] + x[7] + x[8] + x[9] >= demanda['9']

	model.solve(solver)


	for i in list(x.keys()):
		print("Activar {} máquinas el día {}".format(x[i].varValue,i))

	respuesta_json = {
				'Lunes': int(x[0].varValue),
				'Martes': int(x[1].varValue),
				'Miercoles': int(x[2].varValue),
				'Jueves': int(x[3].varValue),
				'Viernes': int(x[4].varValue),
				'Sabado': int(x[5].varValue),
				'Domingo': int(x[6].varValue)
	}


	# return str(x[0].varValue)
	return jsonify(respuesta_json)

# API 2: Plan de capacidades
@app.route('/capacitated_plan', methods=["GET","POST"])
def solve_capacitated_plant():
	'''
	You are given four Pandas data frames demand, var_cost, fix_cost, and cap containing the regional demand (thous. of cars), variable production costs (thous. $US), 
	fixed production costs (thous. $US), and production capacity (thous. of cars).
	'''

	# JSON de Ejemplo para enviar por POSTMAN
	'''
	{
	    "Country": ["USA","Germany","Japan","Brazil","India"],
	    "Dmd":[2719.6, 84.1, 1676.8, 145.4, 156.4],
	    "Var_Cost": {
	        "USA":[6,13,20,12,22], 
	        "Germany":[13,6,14,14,13], 
	        "Japan":[20,14,3,21,10], 
	        "Brazil":[12,14,21,8,23], 
	        "India":[17,13,9,21,8]
	    },
	    "Fix_Cost":{
	        "Low_Cap":[6500,4980,6230,3230,2110], 
	        "High_Cap":[9500,7270,9100,4730,3080]
	    },
	    "Cap": {
	        "Low_Cap":[500,500,500,500,500], 
	        "High_Cap":[1500,1500,1500,1500,1500]
	    }
	}
	'''

	#Recibir el JSON de postman
	data_json = request.get_json()

	demand = pd.DataFrame(data_json['Dmd'], index=data_json['Country'], columns=["Dmd"])

	var_cost = pd.DataFrame(data_json['Var_Cost'], index=data_json['Country'])

	fix_cost = pd.DataFrame(data_json['Fix_Cost'], index=data_json['Country'])

	cap = pd.DataFrame(data_json['Cap'], index=data_json['Country'])

	# Initialize Class
	model = LpProblem("Capacitated Plant Location Model", LpMinimize)

	# Define Decision Variables
	loc = ['USA', 'Germany', 'Japan', 'Brazil', 'India']
	size = ['Low_Cap','High_Cap']

	x = LpVariable.dicts("production_", [(i,j) for i in loc for j in loc], lowBound=0, upBound=None, cat='Continuous')
	y = LpVariable.dicts("plant_", [(i,s) for s in size for i in loc], cat='Binary')

	# Define objective function
	model += (lpSum([fix_cost.loc[i,s] * y[(i,s)] for s in size for i in loc]) + lpSum([var_cost.loc[i,j] * x[(i,j)] for i in loc for j in loc]))

	# Define the constraints
	# Define the constraint that sets total production shipped to a particular region equal to the total demand of that region.
	for j in loc:
		model += lpSum([x[(i, j)] for i in loc]) == demand.loc[j,'Dmd']
    # Define constraint that sets total production of a particular region is less than or equal to the total production capacity of that region.
	for i in loc:
		model += lpSum([x[(i, j)] for j in loc]) <= lpSum([cap.loc[i,s] * y[(i,s)] for s in size])
	# Define logical constraint so that if the high capacity plant in USA is open, then a low capacity plant in Germany is also opened.
	model += y[('USA','High_Cap')] - y[('Germany','Low_Cap')] <= 0

	# Resolver el modelo
	model.solve(solver)

	# Imprimir valores óptimos de las variables en la consola
	for v in model.variables():
		print(v.name, "=", v.varValue)

	# Imprimir el tipo de solución en la consola
	print("Status:", LpStatus[model.status])

	# Imprimir el resultado de la función objetivo en la consola
	print("Objective =", value(model.objective))

	#Preparar JSON
	respuesta_json = {
				'Status Code': 200,
				'Estado': "Modelo procesado",
				'Solucion': LpStatus[model.status],
				'Función objetivo (minimizar costes)': str(model.objective),
				'Resultado de la función objetivo (Coste minimo)': value(model.objective),
				'Localización de Plantas': {
					"plant__('Brazil',_'High_Cap')" : int(model.variables()[0].varValue),
					"plant__('Brazil',_'Low_Cap')" : int(model.variables()[1].varValue),
					"plant__('Germany',_'High_Cap')" : int(model.variables()[2].varValue),
					"plant__('Germany',_'Low_Cap')" : int(model.variables()[3].varValue),
					"plant__('India',_'High_Cap')" : int(model.variables()[4].varValue),
					"plant__('India',_'Low_Cap')" : int(model.variables()[5].varValue),
					"plant__('Japan',_'High_Cap')" : int(model.variables()[6].varValue),
					"plant__('Japan',_'Low_Cap')" : int(model.variables()[7].varValue),
					"plant__('USA',_'High_Cap')" : int(model.variables()[8].varValue),
					"plant__('USA',_'Low_Cap')" : int(model.variables()[9].varValue)
					},
				'Envío de producción (Origen, Destino)': {
					"production__('Brazil',_'Brazil')": int(model.variables()[10].varValue),
					"production__('Brazil',_'Germany')" : int(model.variables()[11].varValue),
					"production__('Brazil',_'India')" : int(model.variables()[12].varValue),
					"production__('Brazil',_'Japan')" : int(model.variables()[13].varValue),
					"production__('Brazil',_'USA')" : int(model.variables()[14].varValue),
					"production__('Germany',_'Brazil')" : int(model.variables()[15].varValue),
					"production__('Germany',_'Germany')" : int(model.variables()[16].varValue),
					"production__('Germany',_'India')" : int(model.variables()[17].varValue),
					"production__('Germany',_'Japan')" : int(model.variables()[18].varValue),
					"production__('Germany',_'USA')" : int(model.variables()[19].varValue),
					"production__('India',_'Brazil')" : int(model.variables()[20].varValue),
					"production__('India',_'Germany')" : int(model.variables()[21].varValue),
					"production__('India',_'India')" : int(model.variables()[22].varValue),
					"production__('India',_'Japan')" : int(model.variables()[23].varValue),
					"production__('India',_'USA')" : int(model.variables()[24].varValue),
					"production__('Japan',_'Brazil')" : int(model.variables()[25].varValue),
					"production__('Japan',_'Germany')" : int(model.variables()[26].varValue),
					"production__('Japan',_'India')" : int(model.variables()[27].varValue),
					"production__('Japan',_'Japan')" : int(model.variables()[28].varValue),
					"production__('Japan',_'USA')" : int(model.variables()[29].varValue),
					"production__('USA',_'Brazil')" : int(model.variables()[30].varValue),
					"production__('USA',_'Germany')" : int(model.variables()[31].varValue),
					"production__('USA',_'India')" : int(model.variables()[32].varValue),
					"production__('USA',_'Japan')" : int(model.variables()[33].varValue),
					"production__('USA',_'USA')" : int(model.variables()[34].varValue)
					}
	}

	return jsonify(respuesta_json)


# API 3: Logística de camiones
@app.route('/logical_constraint_1', methods=["GET","POST"])
def solve_logical_constraint_1():
	'''
	Un cliente ha pedido que se le entreguen seis productos durante el próximo mes.
	Se deberán enviar varias cargas de camiones para entregar todos los productos.
	Hay un límite de peso en los camiones de 25,000 lbs.
	Por razones de flujo de efectivo, se desea enviar la combinación más rentable de
	productos que puedan caber en el primer camión.
	'''
	#Definimos 2 diccionarios. El peso de cada producto y su rentabilidad
	peso = {'A': 12583, 'B': 9204, 'C': 12611, 'D': 12131, 'E': 12889, 'F': 11529}
	rentabilidad = {'A': 102564, 'B': 130043, 'C': 127648, 'D': 155058, 'E': 238846, 'F': 197030}
	#Definimos la lista de productos
	prod = ['A', 'B', 'C', 'D', 'E', 'F']

	#Iniciar el modelo, variables de decisión  y funcion objetivo
	model = LpProblem("Loading Truck Problem", LpMaximize)
	x = LpVariable.dicts('Enviar', prod, cat='Binary') #Una variable por cada producto
	model += lpSum([rentabilidad[i] * x[i] for i in prod]) #Funcion Objetivo, maximizar Rentabilidad x Unidades

	#Definir restricciones
	#Agregar una restricción para asegurar que el peso total del camión sea menor o igual a 25,000 lbs.
	model += lpSum([peso[i] * x[i] for i in prod]) <= 25000
	#Agreguar una restricción para que el modelo, como máximo, seleccione solo uno de los productos entre D, E y F.
	model += x['D'] + x['E'] + x['F'] <= 1

	#Resolver el modelo
	model.solve(solver)

	#Imprimir los resultados en la consola
	for i in model.variables():
	    print(i.name, "=", i.varValue)

	#Preparar JSON
	respuesta_json = {
				'Estado': "Modelo resuelto con exito!",
				'Enviar_A': int(model.variables()[0].varValue),
				'Enviar_B': int(model.variables()[1].varValue),
				'Enviar_C': int(model.variables()[2].varValue),
				'Enviar_D': int(model.variables()[3].varValue),
				'Enviar_E': int(model.variables()[4].varValue),
				'Enviar_F': int(model.variables()[5].varValue),
				'Status Code': 200
	}

	return jsonify(respuesta_json)


# API 4: Logística de camiones 2
@app.route('/logical_constraint_2', methods=["GET","POST"])
def solve_logical_constraint_2():
	'''
	Usted trabaja en un centro de distribución de camiones y debe decidir a cuál de las 6 ubicaciones de clientes enviará 
	un camión. Su objetivo es minimizar la distancia que recorre un camión.

	Actualice las restricciones para que el modelo seleccione al menos una ubicación
	Agregue la restricción de modo que si se selecciona la ubicación A, también se seleccione la ubicación D.
	Agregue la restricción de modo que si se selecciona la ubicación B, también se seleccione la ubicación E.

	'''
	#Definimos las distancias a cada ubicación
	dist = {'A': 86, 'B': 95, 'C': 205, 'D': 229, 'E': 101, 'F': 209}
	#Definimos la lista de ubicaciones
	cust = ['A', 'B', 'C', 'D', 'E', 'F']

	#Iniciar el modelo, variables de decisión  y funcion objetivo
	model = LpProblem("Loading Truck Problem", LpMinimize)
	x = LpVariable.dicts('Enviar', cust, cat='Binary') #Una variable por cada ubicación
	model += lpSum([dist[i] * x[i] for i in cust]) #Funcion Objetivo, maximizar distancia para cada camión

	#Definir restricciones
	#Actualice las restricciones para que el modelo seleccione al menos una ubicación
	model += x['A'] + x['B'] + x['C'] + x['D'] + x['E'] + x['F'] >= 1
	#Agregue la restricción de modo que si se selecciona la ubicación A, también se seleccione la ubicación D.
	model += x['A'] - x['D'] <= 0
	#Agregue la restricción de modo que si se selecciona la ubicación B, también se seleccione la ubicación E.
	model += x['B'] - x['E'] <= 0

	#Resolver el modelo
	model.solve(solver)

	#Imprimir los resultados en la consola
	for i in model.variables():
	    print(i.name, "=", i.varValue)

	#Preparar JSON
	respuesta_json = {
				'Estado': "Modelo resuelto con exito!",
				'Enviar_A': int(model.variables()[0].varValue),
				'Enviar_B': int(model.variables()[1].varValue),
				'Enviar_C': int(model.variables()[2].varValue),
				'Enviar_D': int(model.variables()[3].varValue),
				'Enviar_E': int(model.variables()[4].varValue),
				'Enviar_F': int(model.variables()[5].varValue),
				'Status Code': 200
	}

	return jsonify(respuesta_json)













if __name__ == '__main__':
	app.run(debug=True)
