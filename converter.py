from lxml import etree
import objects

def topy(xmlfile):
	with open(xmlfile, 'w') as file:
		xmlstring = file.read()
	world = e