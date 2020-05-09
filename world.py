from lxml import etree
from objects import Player
from objects import Object
from events import EventHandler
from events import Event
import converter as conv

global world

class World:
    def __init__(self, gamefile):
        tree = conv.loadworld(gamefile)
        self.properties = conv.unpack_properties(tree)
        self.player = Player(tree.find('player'))
        self.rooms = {}
        for room in tree.findall('room'):
            self.rooms[room.get('id')] = Room(self, room)
        self.connections = {}
        for connection in tree.findall('connection'):
            self.connections[connection.get('id')] = Connection(connection)
            for link in self.connections[connection.get('id')].links:
                self.rooms[link].connectsto.append(link)
        self.events = {}
        for event in tree.find('events').findall('event'):
            self.events[event.get('id')] = Event(event)
        self.eventhandler = EventHandler(self, tree)
        #self.eventhandler = EventHandler()
        return

    def get_property(self, prop):
        if self.properties[prop]:
            return self.properties[prop]
        else:
            return ''
            
    def set_property(self, prop, value):
        self.properties[prop] = value
        return self.properties[prop]

    def get_room_id(self, value, prop='name') -> str: # returns id of room with given property and value, standard is name
        for room in self.rooms.values():
            if value == room.get_property(prop): return room.id
        raise Exception(f'No Room with {prop} = {value}!')

    def get_active_room(self):
        return self.rooms[self.player.inroom]

    def get_nearby_rooms(self) -> list: # returns the list of the rooms the player can go to
        return self.rooms[self.player.inroom].connectsto

    def testfuncion(self):
        return self.rooms['0'].objects['001']

    def delete_object(self, objid):
        return

# --------- PLAYER ACTIONS ----------- #

    def changeroom(self, roomid, byplayer=True):
        if byplayer and roomid in self.get_nearby_rooms():
            self.player.inroom = roomid
        elif not byplayer and roomid in self.rooms:
            self.player.inroom = roomid
        else:
            raise Exception('Room not found!')

# ------------------------------------ #

    def step(self):
        self.properties['steps'] += 1
        return self.properties['steps']

    def save(self, gamefile):
        self.properties['session'] += 1

        worldtree = etree.Element('world')
        worldtree.append(conv.pack_properties(self.properties))
        worldtree.append(conv.pack_events(self.events))
        worldtree.append(self.player.save())
        for room in self.rooms.values():
            worldtree.append(room.save())
        for con in self.connections.values():
            worldtree.append(con.save())
        conv.saveworld(worldtree, gamefile)
        return 'Saved World!'

    def __str__(self):
        props = {key: prop for key, prop in self.properties.items()}
        rooms = [room for room in self.rooms]
        return f'WORLD: properties={str(props)}, rooms={str(rooms)}'

class Connection:
    def __init__(self, tree):
        self.id = tree.get('id')
        self.properties = conv.unpack_properties(tree)
        self.links = []
        for link in tree.findall('link'): self.links.append(link.text)
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
        tree = etree.Element('connection')
        tree.set('id', self.id)
        tree.append(conv.pack_properties(self.properties))
        for link in self.links:
            x = etree.SubElement(tree, 'link')
            x.text = link
        return tree

class Room:
    def __init__(self, world, tree):
        self.world = world
        self.id = tree.get('id')
        self.connectsto = []
        self.properties = conv.unpack_properties(tree)
        self.objects = {}
        for obj in tree.findall('object'):
            self.objects[obj.get('id')] = Object(obj)
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
        tree = etree.Element('room')
        tree.set('id', self.id)
        tree.append(conv.pack_properties(self.properties))
        tree.append(conv.pack_events(self.events))
        for obj in self.objects.values():
            tree.append(obj.save())
        return tree

    def __str__(self):
        props = {key: prop for key, prop in self.properties.items()}
        objects = [obj for obj in self.objects]
        return f'ROOM {self.id}: properties={str(props)}, objects={str(objects)}'