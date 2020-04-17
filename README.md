# optimizacion_supply_chain
En este repositorio guardo mis ejemplos de optimizacion de supply chain

### Programa de mantenimiento preventivo
En una cantera usan sierras de diamante para cortar losas de mármol. Para el mantenimiento preventivo, las sierras solo pueden funcionar durante 4 horas consecutivas, luego se completa una inspección de 1 hora antes de que se les permita volver al servicio. La cantera opera turnos de 10 horas. Al final del turno, si las hojas de la sierra no se han utilizado durante 4 horas consecutivas, el tiempo restante se utilizará al comienzo del siguiente turno. La cantidad esperada de hojas de sierra necesarias para cada hora se enumera a continuación. Nuestro objetivo es determinar la cantidad mínima de hojas de sierra necesarias para el cambio.

Esta API funciona enviando un POST vía Postman con el siguiente formato:
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

Los numeros entre comillas son las horas de trabajo y los numeros sin comillas son la cantidad de máquinas que tienen que estar funcionando en cada hora.

Para minimizar este problema utilizamos la librería `pulp`

El output del modelo es otro JSON con el resultado de cuántas máquinas iniciar en cada día para minimizar la utilización de las máquinas y cumplir con la demanda.