from lxml import etree
import urllib
import sys
nItem = 0
nImg = 0
ocurrenciasClave = False
pClave = sys.argv[1]

class ParseRssNews ():
	def __init__ (self):
		print ('---- Principio del archivo')
	def start (self, tag, attrib):
		global nItem
		global nImg
		if tag == "item":
			nItem+=1
		if tag == "enclosure":
			if attrib["type"]== "image/jpeg":
				nImg+=1
				print attrib["url"]
				#urllib.urlretrieve(attrib["url"], "./imgDown/"+str(nImg)+".jpg")
	def data(self, data):
		global ocurrenciasClave
		if data.find(pClave)>=0:
			ocurrenciasClave=True
	def close (self):
		print ('---- Fin del archivo')
		print ("Numero de elementos: %s") %nItem
		print ("Numero de imagenes (jpeg): %s") %nImg
		print ("La palabra -- %s -- aparece (1) no aparece (0): %s")%(pClave,int(ocurrenciasClave))

parser = etree.XMLParser (target=ParseRssNews ())
etree.parse ('portada.xml', parser)