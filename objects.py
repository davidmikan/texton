from lxml import etree
import converter as conv
from events import Event

class Object:
    def __init__(self, tree):
        self.id = tree.get('id')
        self.type = tree.get('type')
        self.properties = conv.unpack_properties(tree)
        self.events = {}
        for event in tree.find('events').findall('event'):
            self.events[event.get('id')] = Event(event)
        return
        
    def get_property(self, prop):
        if self.properties[prop]:
            return self.properties[prop]
        else:
            return ''
            
    def set_property(self, prop, value):
        self.properties[prop] = value
        return self.properties[prop]

    def save(self):
        tree = etree.Element('object')
        tree.set('id', self.id)
        tree.set('type', self.type)
        tree.append(conv.pack_properties(self.properties))
        tree.append(conv.pack_events(self.events))
        return tree

    def __str__(self):
        props = {key: prop for key, prop in self.properties.items()}
        return f'OBJECT {self.id}: properties: {str(props)}'

class Player:
    def __init__(self, tree):
        self.inroom = tree.get('inroom')
        self.properties = conv.unpack_properties(tree)
        self.inventory = {}
        for obj in tree.find('inventory').getchildren():
            self.inventory[obj.get('id')] = Object(obj)

    def get_property(self, prop):
        if self.properties[prop]:
            return self.properties[prop]
        else:
            return ''
            
    def set_property(self, prop, value):
        self.properties[prop] = value
        return self.properties[prop]

    def save(self):
        tree = etree.Element('player')
        tree.set('inroom', self.inroom)
        tree.append(conv.pack_properties(self.properties))
        inv = etree.SubElement(tree, 'inventory')
        for obj in self.inventory.values():
            inv.append(obj.save())
        return tree

    def __str__(self):
        props = {key: prop for key, prop in self.properties.items()}
        return f'PLAYER: inroom({self.inroom}), properties: {props}'


# def findobjects(search, firstmatch=True) -> list:
#     matches = []
#     # iterate first through inventory, then activerooms, then all rooms
#     for objid, obj in player.inventory.items():
#         if search in (obj.type, obj.properties['name']):
#             matches.append(objid)
#     for objid, obj in activeroom.objects.items():
#         if search in (obj.type, obj.properties['name']):
#             matches.append(objid)
#     for room in world.rooms.values():
#         for objid, obj in room.objects.items():
#             if search in (obj.type, obj.properties['name']):
#                 matches.append(objid)
#     if firstmatch: return [matches[0]]
#     else: return matches