from flask import Flask, jsonify, request
from pulp import *

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

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

	model.solve()

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

if __name__ == '__main__':
	app.run(debug=True)