#-*- coding: utf-8 -*-
from lxml import etree
import urllib
import re
import sys

numeroElementos = 0
numeroImagenes = 0

ct = re.compile('(.?)*encoded')

if len(sys.argv) > 1:
    encontrado = False
    termino = sys.argv[1]

tree = etree.parse('portada.xml')
# Root element
rss = tree.getroot()
# Los elementos funcionan como listas # First child
channel = rss[0]

for e in channel:
	if e.tag == "item":
		numeroElementos+=1
		for i in e:
			if i.tag == "enclosure":
				if i.attrib["type"]== "image/jpeg":
					numeroImagenes+=1
					print i.attrib["url"]
					#urllib.urlretrieve(i.attrib["url"], "imagenesDescargadas/" + str(numeroImagenes) + ".jpg")
					
            if ct.search(i.tag) != None:
                if len(sys.argv) > 1:
                    tr = re.compile('\s'+termino+'\s')
                    text = etree.tostring(i)
                    if tr.search(text) != None:
                        encontrado = True

print "Numero de elementos: " + str(numeroElementos)
print "Numero de imagenes: " + str(numeroImagenes)
if len(sys.argv) > 1:
    if encontrado:
        print 'El termino ' +termino+ ' está en el documento.'
    else:
       print 'El termino ' +termino+ ' no está en el documento.'