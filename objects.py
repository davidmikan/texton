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
        for roomobj in self.rooms.values():
            world.append(roomobj.save())
        return world

class Room:
    def __init__(self, room):
        self.objects = []
        self.connections = []
        self.attr = {}
        self.attr['id'] = room.get('id')
        self.attr['visited'] = bool(room.get('visited')=='True')
        self.name = room.find('name').text
        self.description = room.find('description').text
        if room.find('player') is not None:
            self.player = Player(room.find('player'), room.get('id'))
        self.connections = room.find('connectsto').text.split(',')
        for el in room.findall('object'):
            self.objects.append(obj_assembler(el))
        return

    def save(self):
        room = etree.Element('room')
        for attribute in self.attr:
            room.set(attribute, str(self.attr[attribute]))
            print('ATTRIBUTES '+str(room.attrib))
        del self.attr
        for el in self.objects:
            room.append(el.save())
        del self.objects
        for attribute, value in self.__dict__.items():
            if not attribute in ['player', 'connections']:
                tag = etree.SubElement(room, attribute)
                tag.text = value
                print(attribute, value)
            if attribute == 'connections':
                tag = etree.SubElement(room, 'connectsto')
                tag.text = ''
                for i in value:
                    tag.text += i + ','
            if attribute == 'player':
                room.append(self.player.save())
        return room

class Player:
    def __init__(self, playerel, inroom):
        self.name = playerel.find('name').text
        if not bool(self.name): self.nameinput()
        self.inroom = inroom
        self.inventory = []
        for child in playerel.find('inventory').getchildren():
            obj = obj_assembler(child)
            self.inventory.append(obj)
        return
    def nameinput(self):
        self.name = input('What\'s your name?\n')
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
        self.attr = {}
        self.attr['type'] = item.get('type')
        return
    def save(self):
        obj = etree.Element('object')
        obj.set('type', 'standard')
        name = etree.SubElement(obj, 'name')
        name.text = self.name
        return obj
        
class CustomObject:
    def __init__(self, item):
        self.attr = {}
        self.tag = {}
        for child in item.getchildren():
            self.tag[child.tag] = child.text
        for attribute in item.attrib:
            self.attr[attribute] = item.get(attribute)
    def save(self):
        obj = etree.Element('object')
        for attribute in self.attr:
            obj.set(attribute, self.attr[attribute])
        for tag in self.tag:
            x = etree.SubElement(obj, tag)
            x.text = self.tag[tag]
        return obj

types = {
    'standard': StandardObject
}

def obj_save():
    return

def obj_assembler(item):
    if item.get('type') in types:
        obj = types[item.get('type')](item)
    else:
        obj = CustomObject(item)
    return obj
