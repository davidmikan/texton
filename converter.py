from lxml import etree
import objects

def readtopy(path):
        #open XML file and preparing tree element
        with open(path, 'r') as file:
                xmlstring = file.read()
        tree = etree.XML(xmlstring)
        #transferring informations to objects via object's method
        world = objects.World(tree)
        print("Sucessfully read XML file...")
        return world

def writetoxml(world, path):        
        tree = world.save()
        xmlstring = etree.tostring(tree, pretty_print=True)
        with open(path, 'wb+') as file:
                file.write(xmlstring)
        print("Sucessfully wrote XML file...")
        return
        
##testing       
##path = "test.xml"
##path2 = "test2.xml"
##
##x = readtopy(path)
##writetoxml(x, path2)
