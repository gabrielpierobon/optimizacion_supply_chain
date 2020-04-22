from flask import Flask, jsonify, request
import pandas as pd
from pulp import *
import os

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

cwd = os.getcwd()
# solverdir = 'cbc-2.7.5-win64\\bin\\cbc.exe'  # extracted and renamed CBC solver binary
solverdir = 'Cbc-2.7.5-win64-intel11.1\\bin\\cbc.exe'
solverdir = os.path.join(cwd, solverdir)
solver = COIN_CMD(path=solverdir)

@app.route('/minimizar_contratacion', methods=['GET', 'POST'])
def problema_1():

	# The class has been initialize, and x, hours and objective fuction defined
	model = LpProblem("Minimize_Staffing", LpMinimize)

	hours = list(range(10))

	# Define Decision Variables
	x = LpVariable.dicts('saws_', hours, lowBound=0, cat="Integer")

	# Define Objective
	model += lpSum([x[i] for i in x])

	# En postman, enviar este json:
	# {
	# "0":7,
	# "1":7,
	# "2":7,
	# "3":6,
	# "4":5,
	# "5":6,
	# "6":6,
	# "7":7,
	# "8":7,
	# "9":6
	# }

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


# @app.route('/capacitated_plan', methods=["GET","POST"])
# def solve_capacitated_plant():
#
# 	demand = pd.DataFrame({'Dmd':[2719.6, 84.1, 1676.8, 145.4, 156.4]},
#                       		index=["USA","Germany","Japan","Brazil","India"])
#
# 	var_cost = pd.DataFrame({'USA':[6,13,20,12,22], 'Germany':[13,6,14,14,13], 'Japan':[20,14,3,21,10], 'Brazil':[12,14,21,8,23], 'India':[17,13,9,21,8]},
# 							 index=["USA","Germany","Japan","Brazil","India"])
#
# 	fix_cost = pd.DataFrame({'Low_Cap':[6500,4980,6230,3230,2110], 'High_Cap':[9500,7270,9100,4730,3080]},
# 							 index=["USA","Germany","Japan","Brazil","India"])
#
# 	cap = pd.DataFrame({'Low_Cap':[500,500,500,500,500], 'High_Cap':[1500,1500,1500,1500,1500]},
# 					    index=["USA","Germany","Japan","Brazil","India"])
#
# 	# Initialize Class
# 	model = LpProblem("Capacitated Plant Location Model", LpMinimize)
#
# 	# Define Decision Variables
# 	loc = ['USA', 'Germany', 'Japan', 'Brazil', 'India']
# 	size = ['Low_Cap','High_Cap']
#
# 	x = LpVariable.dicts("production_", [(i,j) for i in loc for j in loc], lowBound=0, upBound=None, cat='Continuous')
# 	y = LpVariable.dicts("plant_", [(i,s) for s in size for i in loc], cat='Binary')
#
# 	# Define objective function
# 	model += (lpSum([fix_cost.loc[i,s] * y[(i,s)] for s in size for i in loc]) + lpSum([var_cost.loc[i,j] * x[(i,j)] for i in loc for j in loc]))
#
# 	model.solve()
# 	# El resultado es 0 por que no se puso la demanda!!!!!!!!!!!
#
# 	for v in model.variables():
# 		print(v.name, "=", v.varValue)
#
# 	return str("Ejecutado con éxito!")
#
# @app.route('/logical_constraint', methods=["GET","POST"])
# def solve_logical_constraint():
# 	'''
# 	Un cliente ha pedido que se le entreguen seis productos durante el próximo mes.
# 	Se deberán enviar varias cargas de camiones para entregar todos los productos.
# 	Hay un límite de peso en los camiones de 25,000 lbs.
# 	Por razones de flujo de efectivo, se desea enviar la combinación más rentable de
# 	productos que puedan caber en el primer camión.
# 	'''
# 	#Definimos 2 diccionarios. El peso de cada producto y su rentabilidad
# 	peso = {'A': 12583, 'B': 9204, 'C': 12611, 'D': 12131, 'E': 12889, 'F': 11529}
# 	rentabilidad = {'A': 102564, 'B': 130043, 'C': 127648, 'D': 155058, 'E': 238846, 'F': 197030}
# 	#Definimos la lista de productos
# 	prod = ['A', 'B', 'C', 'D', 'E', 'F']
#
# 	#Iniciar el modelo, variables de decisión  y funcion objetivo
# 	model = LpProblem("Loading Truck Problem", LpMaximize)
# 	x = LpVariable.dicts('Enviar', prod, cat='Binary') #Una variable por cada producto
# 	model += lpSum([rentabilidad[i] * x[i] for i in prod]) #Funcion Objetivo, maximizar Rentabilidad x Unidades
#
# 	#Definir restricciones
# 	#Agregar una restricción para asegurar que el peso total del camión sea menor o igual a 25,000 lbs.
# 	model += lpSum([peso[i] * x[i] for i in prod]) <= 25000
# 	#Agreguar una restricción para que el modelo, como máximo, seleccione solo uno de los productos entre D, E y F.
# 	model += x['D'] + x['E'] + x['F'] <= 1
#
# 	#Resolver el modelo
# 	model.solve()
#
# 	#Imprimir los resultados en la consola
# 	for i in model.variables():
# 	    print(i.name, "=", i.varValue)
#
# 	#Preparar JSON
# 	respuesta_json = {
# 				'Estado': "Modelo resuelto con éxito!",
# 				'Enviar_A': int(model.variables()[0].varValue),
# 				'Enviar_B': int(model.variables()[1].varValue),
# 				'Enviar_C': int(model.variables()[2].varValue),
# 				'Enviar_D': int(model.variables()[3].varValue),
# 				'Enviar_E': int(model.variables()[4].varValue),
# 				'Enviar_F': int(model.variables()[5].varValue),
# 				'Status Code': 200
# 	}
#
# 	return jsonify(respuesta_json)




if __name__ == '__main__':
	app.run(debug=True)
