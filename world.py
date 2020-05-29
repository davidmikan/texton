from lxml import etree
from json import load as jsonload
from objects import Player, GameObject
from events import EventHandler, Event
import converter as conv

class World:
    """
    root object of the game
    contains all methods for actions
    self.rooms
        {room-id: Room object}
    self.player
        Player object
    self.eventhandler
        EventHandler objects containing Events
    self.properties
        {name: value}
    """

    def __init__(self, gamefile):
        """
        takes path to a xml-gamefile and extracts the world
        """
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
            # -- WIP -- #            
        self.eventhandler = EventHandler(self)
        self.events = []
        for event in tree.find('events').findall('event'):
            self.events.append(event.get('id'))
            self.eventhandler.events[event.get('id')] = self.eventhandler.parser.parse_xml(event)
        for room in self.rooms.values(): print(room)

#   ---tools---

    def __set_active_room(self, roomid):
        """
        sets player.inroom to provided id
        """
        if roomid in self.rooms:
            self.player.inroom = roomid
            return self.get_active_room()
        else: raise IndexError(f'Room with ID {roomid} not existent!')

    def __delete_object(self, objid):
        """
        takes object-id
        and deletes the object
        """
        if objid in self.player.inventory:
            del self.player.inventory[objid]
        for room in self.rooms.values():
            if objid in room.objects:
                del room.objects[objid]

#   ---

    def get_property(self, prop):
        return self.properties.get(prop)
        
    def set_property(self, prop, value):
        self.properties[prop] = value
        return self.properties[prop]

    def get_room(self, roomid):
        return self.rooms.get(roomid)

    def get_object(self, objid):
        if objid in self.player.inventory:
            return self.player.inventory[objid]
        for room in self.rooms.values():
            if objid in room.objects:
                return room.objects[objid]
        return None

    def get_room_id(self, value, prop='name') -> str:
        """
        value

        prop (default 'name'): property to match the value to

        return: id of room
        TODO: 
            * alternative_names property ("Wien Mitte - The Mall" -> "mall"/"wien mitte")
            * search through multiple properties
            * option to return first match, or all the matches
        """
        for room in self.rooms.values():
            if value.lower == room.properties[prop].lower:
                return room.id
        return None

    def get_object_id(self, value, prop='name'):
        """
        TODO:
            * implement :p
        """
        pass

    def get_active_room(self):
        return self.rooms.get(self.player.inroom)

    def get_nearby_rooms(self, roomid) -> list:
        """
        return: 
            list of connection ids that link provided room
        TODO:
            WIP
        """
        matches = []
        for connection in self.connections.values():
            links = connection.links
            if roomid in links:
                links.remove(roomid)
                matches.append(connection.id)
        return matches                              

    def move_object(self, objid, destination):
        """
        objid: 
            object-id
        destination: 
            room-id or 'inv' for inventory
            moves 
            object from its current container into the destination container
        TODO: 
            * add distinction //david:?
        """
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

    def move_to_room(self, roomid, byplayer=True):
        """
        byplayer (default True):   
            if True, check for connection from active room and 
            whether it is locked
            if False, always move player to room
        return: 
            entered Room or None
        TODO: 
            WIP
            * check if connection locked, if yes -> unlock_room
        """
        if byplayer and roomid in self.get_nearby_rooms():
            return self.__set_active_room(roomid)
        elif not byplayer and roomid in self.rooms:
            self.player.inroom = roomid
            return self.rooms[roomid]
        else:
            return None

    def player_move_object(self, objid):
        """ 
        TODO: 
            merge into move_object
        """
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
        """
        gamefile: filepath
        converts itself into xml string and saves it in gamefile
        """
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

    def __str__(self):
        props = {key: prop for key, prop in self.properties.items()}
        rooms = [room for room in self.rooms]
        return f'WORLD: properties={str(props)}, rooms={str(rooms)}'

class Connection:

    """
    represents a connection between 2 rooms
    self.links= [room-ids]
    """

    def __init__(self, tree):
        self.id = tree.get('id')
        self.properties = conv.unpack_properties(tree)
        self.links = []
        for link in tree.findall('link'): 
            self.links.append(link.text)
        return
    
    def get_property(self, prop):
        return self.properties.get(prop)

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
    """
    self.objects = {object-id: GameObject}
    self.properties = {name: value}
    """
    
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
        return self.properties.get(prop)
            
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
        return f'[ROOM {self.id}] properties={str(props)}, objects={str(objects)}, connects to={str(self.connectsto)}'