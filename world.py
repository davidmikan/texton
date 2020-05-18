from lxml import etree
from json import load as jsonload
from objects import Player
from objects import GameObject
from events import EventHandler
from events import Event
import converter as conv

class World:
    def __init__(self, gamefile):
        self.statusmessages = {}
        with open('files/statusmsg.json', 'r') as f:
            self.statusmessages = jsonload(f)
        print(self.statusmessages['world_loading'])
        tree = conv.loadworld(gamefile)
        self.properties = conv.unpack_properties(tree)
        self.player = Player(tree.find('player'), self)
        self.rooms = {}
        for room in tree.findall('room'):
            self.rooms[room.get('id')] = Room(self, room)
        self.connections = {}
        for connection in tree.findall('connection'):
            self.connections[connection.get('id')] = Connection(connection)
            for link in self.connections[connection.get('id')].links:
                self.rooms[link].connectsto.append(link)
        self.eventhandler = EventHandler(self)
        self.events = []
        for event in tree.find('events').findall('event'):
            self.events.append(event.get('id'))
            self.eventhandler.events[event.get('id')] = self.eventhandler.parser.parse_xml(event)
        print(self.statusmessages['world_loaded'])

# --------------PROPERTIES------------ #

    def get_property(self, prop):
        return self.properties[prop] or ''
        
    def set_property(self, prop, value):
        self.properties[prop] = value
        return self.properties[prop]

# --------------ROOMS----------------- #

    def get_room(self, roomid):
        return self.rooms.get(roomid)

    def get_room_id(self, value, prop='name') -> str: # returns id of room with given property and value, standard is name
        for room in self.rooms.values():
            if value == room.get_property(prop): return room.id
        raise Exception(f'No Room with {prop} = {value}!')

    def get_active_room(self):
        return self.rooms[self.player.inroom]
    
    def set_active_room(self, roomid):
        if roomid in self.rooms:
            self.player.inroom = roomid

    def get_nearby_rooms(self) -> list: # returns the list of the rooms the player can go to
        return self.rooms[self.player.inroom].connectsto

# ------------OBJECTS---------------- #

    def delete_object(self, objid):
        if objid in self.player.inventory:
            del self.player.inventory[objid]
        for room in self.rooms.values():
            if objid in room.objects:
                del room.objects[objid]

    def get_object(self, objid):
        if objid in self.player.inventory:
            return self.player.inventory[objid]
        for room in self.rooms.values():
            if objid in room.objects:
                return room.objects[objid]
        return None

    def move_object(self, objid, destination):
        obj = self.get_object(objid)
        if obj is not None:
            if destination == 'inv':
                container = self.player.inventory
            elif self.get_room(destination) is not None:
                container = self.get_room(destination).objects
            else:
                raise Exception(f'Can\'t locate destination {destination}')
            container[objid] = obj
        else:
            raise Exception(f'Can\'t locate object {objid}')

# --------- PLAYER ACTIONS ----------- #

    def player_move_to_room(self, roomid, byplayer=True):
        if byplayer and roomid in self.get_nearby_rooms():
            self.player.inroom = roomid
        elif not byplayer and roomid in self.rooms:
            self.player.inroom = roomid
        else:
            raise Exception('Room not found!')

    def player_move_object(self, objid):
        x = self.get_object(objid)
        self.player.inventory[objid] = x
        del self.rooms['0'].objects[objid]

# ------------------------------------ #

    def step(self):
        self.properties['steps'] += 1
        return self.properties['steps']

    def say(self, key, *obj): # TODO: implement property replacement
        print(self.statusmessages[key])

    def save(self, gamefile):
        self.properties['session'] += 1

        worldtree = etree.Element('world')
        worldtree.append(conv.pack_properties(self.properties))
        worldtree.append(conv.pack_events(self.events, self.eventhandler))
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
        return self.properties[prop] or ''

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

    def __str__(self):
        return f'CONNECTION {self.id}: links:{self.links[0]+"<->"+self.links[1]}, properties:{self.properties}'

class Room:
    def __init__(self, world, tree):
        self.world = world
        self.id = tree.get('id')
        self.connectsto = []
        self.properties = conv.unpack_properties(tree)
        self.objects = {}
        for obj in tree.findall('object'):
            self.objects[obj.get('id')] = GameObject(obj, self.world)
        self.events = []
        for event in tree.find('events').findall('event'):
            self.events.append(event.get('id'))
            self.world.eventhandler.events[event.get('id')] = self.world.eventhandler.parser.parse_xml(event)
        return

    def get_property(self, prop):
        return self.properties[prop] or ''
            
    def set_property(self, prop, value):
        self.properties[prop] = value
        return self.properties[prop]

    def save(self):
        tree = etree.Element('room')
        tree.set('id', self.id)
        tree.append(conv.pack_properties(self.properties))
        tree.append(conv.pack_events(self.events, self.world.eventhandler))
        for obj in self.objects.values():
            tree.append(obj.save())
        return tree

    def __str__(self):
        props = {key: prop for key, prop in self.properties.items()}
        objects = [obj for obj in self.objects]
        return f'ROOM {self.id}: properties={str(props)}, objects={str(objects)}'