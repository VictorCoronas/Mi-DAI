#-*- coding: utf-8 -*-
from lxml import etree
import re
import urllib
import sys
 
tree = etree.parse('portada.xml')
 
# Root element
rss = tree.getroot()
#Contadores y variables
contN = 0
contI = 0
if len(sys.argv) > 1:
    encontrado = False
    termino = sys.argv[1]
#Expresiones Regulares
im = re.compile('image(.?)*')
ct = re.compile('(.?)*encoded')
# First child
channel = rss[0]
 
for e in channel:
    if e.tag == 'item':
        contN += 1
        for i in e:
            if i.tag == 'enclosure':
                if im.search(i.get('type')) != None:
                    contI += 1
                    name = 'imagen' + str(contI) + '.jpg'
                    #urllib.urlretrieve(i.get('url'), name);
 
            if ct.search(i.tag) != None:
                if len(sys.argv) > 1:
                    tr = re.compile('\s'+termino+'\s')
                    text = etree.tostring(i)
                    if tr.search(text) != None:
                        encontrado = True
 
print 'Nmero de noticias: ' + str(contN)
print 'Nmero de imagenes: ' + str(contI)
if len(sys.argv) > 1:
    if encontrado:
        print 'El termino ' +termino+ ' est en el documento.'
    else:
        print 'El termino ' +termino+ ' no est en el documento.'