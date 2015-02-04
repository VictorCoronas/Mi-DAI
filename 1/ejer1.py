#!/usr/bin/env python
# -*- coding: iso-8859-15 -*-
#Juego de adivinar numero aleatotia

import random

intentos = 0

print("Bien venido al juego de azar...")

print("Como te llamas")

nombre = raw_input()

x = random.randint(0,100)

print("Hola" + nombre)

while intentos < 10:
	intentos = intentos +1
	print("Elige numero del 1 al 100")
	numero = raw_input()
	numero = int(numero)

	if numero < x:
		print("Tu numero es menor")

	if numero > x:
		print("Tu numero es mayor")

	if numero == x:
		break

if numero == x:
    print ("Olee!! Has ganado!")
    print (nombre + " lo lograste con %d intentos" % (intentos))
    print ("Bye Bye")

if numero!= x:
 	print ("Has perdido")