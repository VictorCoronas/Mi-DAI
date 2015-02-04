#-*- coding: utf-8 -*-
from lxml import etree
import urllib
import sys
import re

class ParseRssNews ():
	numeroElementos = 0
	numeroImagenes = 0

	if len(sys.argv) > 1:
		encontrado = False
		termino = sys.argv[1]

	def __init__ (self):
		print ('---- Principio del archivo')
	def start (self, tag, attrib):
		if tag == "item":
			self.numeroElementos+=1
		if tag == "enclosure":
			if attrib["type"]== "image/jpeg":
				self.numeroImagenes+=1
				print attrib["url"]
				#urllib.urlretrieve(attrib["url"], "imagenesDescargadas/" + str(self.numeroImagenes) + ".jpg")
	def data (self, data):
		if len(sys.argv) > 1:
			encuentra = re.compile('\s'+ self.termino +'\s')
			if encuentra.search(data) != None:
				self.encontrado = True

	def close (self):
		print ('---- Fin del archivo')
		print "Numero de elementos: " + str(self.numeroElementos)
		print "Numero de imagenes: " + str(self.numeroImagenes)

		if len(sys.argv) > 1:
			if self.encontrado:
				print 'El termino ' + self.termino + ' esta.'
			else:
				print 'El termino ' + self.termino + ' no esta.'

parser = etree.XMLParser (target=ParseRssNews ())
etree.parse ('portada.xml', parser)