from lxml import etree
import events

def __init__():
    global world
    global player
    global activeroom

class World:
    def __init__(self, tree):
        #properties
        self.properties = get_prop(tree)
        #events
        self.events = {}
        for event in tree.find('events').findall('event'):
            self.events[event.get('id')] = events.Event(event)
        #connections
        self.connections = {}
        for con in tree.findall('connection'):
            self.connections[con.get('id')] = Connection(con)
        print('CONNECTIONS: ' + str(self.connections))
        #rooms
        self.rooms = {}
        for room in tree.findall('room'):
            self.rooms[room.get('id')] = Room(room)
        # assign connections to rooms
        for conid, con in self.connections.items():
            for link in con.links:
                self.rooms[link].connectsto.append(conid)
        return

    def display(self):
        proptree = '\nWORLD: \n'
        for propname, propvalue in self.properties.items():
            proptree += str(propname) + ': ' + str(propvalue) + '\n'
        print(proptree)

    def save(self):
        world = etree.Element('world')
        #properties
        world.append(prop_xml(self.properties))
        #events
        for event in self.events.values():
            world.append(event.save())
        #rooms
        for room in self.rooms.values():
            world.append(room.save())
        #connections
        for con in self.connections.values():
            world.append(con.save())
        return world

class Room:
    def __init__(self, room):
        self.id = room.get('id')
        #properties
        self.properties = get_prop(room)
        #events
        self.events = {}
        #objects
        self.objects = {}
        for obj in room.findall('object'):
            self.objects[obj.get('id')] = Object(obj)
        #temporary vars
        self.connectsto = []
        #player
        if room.find('player') is not None:
            self.player = Player(room.find('player'), self.id)
        return

    def save(self):
        room = etree.Element('room')
        room.set('id', self.id)
        #properties
        room.append(prop_xml(self.properties))
        #events
        #objects
        for obj in self.objects.values():
            room.append(obj.save())
        #player
        if hasattr(self, 'player'):
            room.append(self.player.save())
        return room

class Connection:
    def __init__(self, con):
        #properties
        self.id = con.get('id')
        self.links = []
        for link in con.findall('link'): self.links.append(link.text)
        self.properties = get_prop(con)
        #events
        return

    def save(self):
        #properties
        con = etree.Element('connection')
        con.set('id', self.id)
        con.append(prop_xml(self.properties))
        for link in self.links:
            x = etree.SubElement(con, 'link')
            x.text = link
        return con

class Player:
    def __init__(self, plitem, inroom):
        self.inroom = inroom
        #properties
        self.properties = get_prop(plitem)
        #events
        self.events = {}
        #inventory
        self.inventory = {}
        for obj in plitem.find('inventory').getchildren():
            self.inventory[obj.get('id')] = Object(obj)
        return
        
    def nameinput(self):
        self.name = input('What\'s your name?\n')
        return
        
    def save(self):
        player = etree.Element('player')
        #properties
        player.append(prop_xml(self.properties))
        #events
        #inventory
        inv = etree.SubElement(player, 'inventory')
        for obj in self.inventory.values():
            inv.append(obj.save())
        return player
    
class Object:
    def __init__(self, objitem):
        #attributes
        self.id = objitem.get('id')
        self.type = objitem.get('type')
        #properties
        self.properties = get_prop(objitem)
        #events
        self.events = {}
        return
        
    def save(self):
        obj = etree.Element('object')
        obj.set('id', self.id)
        obj.set('type', self.type)
        #properties
        obj.append(prop_xml(self.properties))
        #events
        return obj

class Event:
    def __init__(self, evitem):
        pass

class ObjPath:
    #work in progress
    def __init__(self, world, player):
        for room in world.rooms:
            name = "room." + str(room)
            self.__dict__[name] = []
            for obj in world.rooms[room].objects:
                self.__dict__[name].append(str(obj))
        self.__dict__['player'] = []
        for obj in player.inventory:
            self.__dict__['player'].append(str(obj))
        return
    
    def __str__(self):
        pathstr = 'world \n'
        for x in self.__dict__:
            pathstr += '+---' + x + '\n'
            for y in self.__dict__[x]:
                pathstr += '+\t|---' + 'object.' + y + '\n'
        print(pathstr)

def get_prop(element):
    prop = {}
    for child in element.find('properties').getchildren():
            if not child.text:
                prop[child.tag] = ''
            elif child.text in ['True', 'False']:
                prop[child.tag] = bool(child.text=='True')
            elif child.text.isdigit():
                prop[child.tag] = int(child.text)
            else:
                prop[child.tag] = child.text
    return prop
   
def prop_xml(prop):
    propertyel = etree.Element('properties')
    for key in prop:
        x = etree.Element(key)
        x.text = str(prop[key])
        propertyel.append(x)
    return propertyel

def findroom(prop) -> list:
    matches = []
    for roomid, room in world.rooms.items():
        if prop in room.properties.values(): 
            matches.append(roomid)
    return matches

def findobjects() -> list:
    return