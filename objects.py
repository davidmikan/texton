from lxml import etree
import converter as conv
from events import Event

class GameObject:
    """
    general object
    self.properties = {name: value}
    """
    
    def __init__(self, tree, world):
        self.id = tree.get('id')
        self.type = tree.get('type')
        self.properties = conv.unpack_properties(tree)
        self.world = world
        self.events = []
        for event in tree.find('events').findall('event'):
            self.events.append(event.get('id'))
            self.world.eventhandler.events[event.get('id')] = self.world.eventhandler.parser.parse_xml(event)
        return
        
    def get_property(self, prop):
        return self.properties.get(prop)
            
    def set_property(self, prop, value):
        self.properties[prop] = value
        return self.properties[prop]

    def save(self):
        tree = etree.Element('object')
        tree.set('id', self.id)
        tree.set('type', self.type)
        tree.append(conv.pack_properties(self.properties))
        tree.append(conv.pack_events(self.events, self.world.eventhandler))
        return tree

    def __str__(self):
        props = {key: prop for key, prop in self.properties.items()}
        return f'OBJECT {self.id}: properties: {str(props)}'

class Player:

    """
    self.properties = {name: value}
    self.inventory = {object-id: GameObject}
    """

    def __init__(self, tree, world):
        self.inroom = tree.get('inroom')
        self.properties = conv.unpack_properties(tree)
        self.inventory = {}
        self.world = world
        self.events = []
        for event in tree.find('events').findall('event'):
            self.events.append(event.get('id'))
            self.world.eventhandler.events[event.get('id')] = self.world.eventhandler.parser.parse_xml(event)
        for obj in tree.find('inventory').getchildren():
            self.inventory[obj.get('id')] = GameObject(obj, self.world)

    def get_property(self, prop):
        return self.properties.get(prop)
            
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
        inv = [key for key in self.inventory]
        return f'PLAYER: inroom({self.inroom}), properties: {props}, inventory:{inv}'