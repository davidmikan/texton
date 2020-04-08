from lxml import etree

class World:
    def __init__(self, tree):
        self.rooms = {}
        for child in tree.getchildren():
            if child.tag == 'room':
                self.rooms[child.get('id')] = Room(child)    
        return
    def save(self):
        world = etree.Element('world')
        for x in self.rooms.values():
            world.append(x.save())
        return world
        

class Room:
    def __init__(self, room):
        self.connections = []
        self.visited = False
        self.hasplayer = False
        self.id = room.get('id')
        self.name = room.find('name').text
        self.description = room.find('description').text
        if room.find('player') is not None:
            self.player = Player(room.find('player'), room.get('id'))
            self.hasplayer = True
        self.connections = room.find('connectsto').text.split(',')
        return
    def save(self):
        room = etree.Element('room')
        room.set('id', self.id)
        name = etree.SubElement(room, 'name')
        name.text = self.name
        desc = etree.SubElement(room, 'description')
        desc.text = self.description
        connections = etree.SubElement(room, 'connectsto')
        connections.text = ",".join(self.connections)
        if self.hasplayer:
            room.append(self.player.save())
        return room
        

class Player:
    def __init__(self,playel, inroom):
        self.name = playel.find('name').text
        self.inroom = inroom
        self.inventory = []
        for child in playel.find('inventory').getchildren():
            obj = obj_assembler(child)
            self.inventory.append(obj)
        return
    def nameinput(self):
        self.name = input('What\s your name?\n')
        return
    def save(self):
        pl = etree.Element('player')
        name = etree.SubElement(pl, 'name')
        name.text = self.name
        inventory = etree.SubElement(pl, 'inventory')
        inv_objects = [x.save() for x in self.inventory]
        for x in inv_objects: inventory.append(x)
        return pl
        
            
class StandardObject:
    def __init__(self, item):
        self.name = item.find('name').text
        return
    def save(self):
        obj = etree.Element('object')
        obj.set('type', 'standard')
        name = etree.SubElement(obj, 'name')
        name.text = self.name
        return obj
        

class xObject(StandardObject):
    def __init__(self, item):
        StandardObject.__init__(self,item)
        self.type = item.get('type')
    def save(self):
        obj = etree.Element('object')
        obj.set('type', self.type)
        name = etree.SubElement(obj, 'name')
        name.text = self.name
        return obj

types = {
    'standard': StandardObject
}

def obj_assembler(item):
    if item.get('type') in types:
        obj = types[item.get('type')](item)
    else:
        obj = xObject(item)
    return obj
