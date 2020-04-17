from lxml import etree

class World:
    def __init__(self, tree):
        #properties
        self.properties = get_prop(tree)
        #events
        self.events = {}
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
        tree = '\nworld:\n'
        for room in self.rooms:
            tree += '  room ' + self.rooms[room].id + ':\n'
            for prop in self.rooms[room].properties:
                tree += '    ' + prop + ': ' + str(self.rooms[room].properties[prop]) + '\n'
            for obj in self.rooms[room].objects:
                tree += '    object ' + self.rooms[room].objects[obj].id + ':\n'
                for prop in self.rooms[room].objects[obj].properties:
                    tree += '      ' + prop + ': ' + str(self.rooms[room].objects[obj].properties[prop]) + '\n'
        return tree

    def save(self):
        world = etree.Element('world')
        #properties
        world.append(prop_xml(self.properties))
        #events
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
    def __init__(self, playerel, inroom):
        self.inroom = inroom
        #properties
        self.properties = get_prop(playerel)
        #events
        self.events = {}
        #inventory
        self.inventory = {}
        for obj in playerel.find('inventory').getchildren():
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
    def __init__(self, item):
        #attributes
        self.id = item.get('id')
        self.type = item.get('type')
        #properties
        self.properties = get_prop(item)
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

class ObjPath:
    def __init__(self, world, player):
        for room in world.rooms:
            name = "room." + str(room)
            self.__dict__[name] = []
            for obj in world.rooms[room]:
                self.__dict__[name].append(str(obj))
        self.__dict__['player']
        for obj in player.inventory:
            self.__dict__['player'].append(str(obj))
        return
    
    def __repr__(self):
        for x in self.__dict__:
            print(x)
            for y in self.dict[x]:
                print('\t', y)

def get_prop(element):
    prop = {}
    for child in element.find('properties').getchildren():
            if child.text in ['True', 'False']:
                prop[child.tag] = bool(child.text=='True')
            else:
                prop[child.tag] = child.text
    return prop
    
def prop_xml(prop):
    property = etree.Element('properties')
    for key in prop:
        x = etree.Element(key)
        x.text = str(prop[key])
        property.append(x)
    return property