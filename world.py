from lxml import etree
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
        self.gamefile = gamefile
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
        return Room.instances.get(roomid)

    def get_object(self, objid):
        return GameObject.instances.get(objid)

    def get_room_id(self, value, prop='name') -> str:
        """
        value

        prop (default 'name'): property to match the value to

        return: id of room
        TODO: 
            * prioritize active room, then nearby rooms, then the rest
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
            * prioritize inventory, then active room, nearby rooms and then the rest
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
            links = connection.links[:]
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
        if byplayer and roomid in self.get_nearby_rooms(roomid):
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

    def step(self):
        self.properties['steps'] += 1
        return self.properties['steps']

    def say(self, key, *obj): 
        # TODO: remove, create renderer script
        print('PLACEHOLDER')

    def save(self, gamefile=''):
        """
        gamefile: filepath
        converts itself into xml string and saves it in gamefile
        """
        self.properties['session'] += 1
        if not gamefile: gamefile = self.gamefile
        worldtree = etree.Element('world')
        worldtree.append(conv.pack_properties(self.properties))
        worldtree.append(conv.pack_events(self.events, self.eventhandler))
        worldtree.append(self.player.save())
        for room in self.rooms.values():
            worldtree.append(room.save())
        for con in self.connections.values():
            worldtree.append(con.save())
        conv.saveworld(worldtree, gamefile)

    def pretty_tree(self, obj=None, name='', style='light', inventory=[], sub_style='light', indent=0, tablen=2):
        styles = {
            # syntax is name: [upperleft, upperright, lowerleft, lowerright, vertical, horizontal, ]
            'light': [['┌', '┐', '└', '┘', '│', '─', '~ , ~'], [True]],
            'double': [['╔', '╗', '╚', '╝', '║', '═', '»,«'], [True]],
            'bold': [['█', '█', '█', '█', '█', '█', '▄,▄'], [True]],
            'header': [['█', '█', '█', '█', '', '█', '▄ , ▄'], [True]],
            'minecraft': [['◾️', '◾️', '◾️', '◾️', '◾️', '◾️', '◾️ ,'], [False]],
            'diamond': [['🔷', '🔷', '🔷', '🔷', '', '🔷', '🔸,'], [False]],
            'hearts': [['💗','💗','💗','💗','💗','💗', ', 💞'], [False]],
            'classic': [['-','-','-','-','|','-', '> ,'], [True]],
            'star': [['✨','✨','✨','✨','✨','✨', '⚡️ , ⚡️'], [False]]
        }
        if obj is None: 
            obj = self
            name = f"TextOn WORLD in {self.gamefile}"
        elif not name:
            classes = {Room: 'TextOn ROOM {id}', Connection: 'TextOn CONNECTION {id}', GameObject: 'TextOn GAMEOBJECT {id}', Player: 'TextOn PLAYER'}
            try: name = classes[obj.__class__].replace('{id}', 'id:'+obj.id)
            except KeyError: name = str(obj.__class__)
            except: name = classes[obj.__class__]
        styleconfig = styles[style][1]
        style = styles[style][0]
        if styleconfig[0]: 
            bridge_top = style[0] + (len(name)+2)*style[5] + style[1]
            bridge_bottom = style[2] + (len(name)+2)*style[5] + style[3]
        else:
            if not len(name)%2==0: name+=' '
            bridge_top = style[0] + (round(len(name)*0.5)+1)*style[5] + style[1]
            bridge_bottom = style[2] + (round(len(name)*0.5)+1)*style[5] + style[3]
        #title
        br = '\n' + indent * tablen * ' '
        output = ''
        output += f"{br}{bridge_top}"
        output += f"{br}{style[4]} {name} {style[4]}"
        output += f"{br}{bridge_bottom}"
        #links if connection
        if obj.__class__ == Connection:
            output += f"{br}{style[6].replace(',', 'links')}{''.join(str(br + link) for link in obj.links)}"
        #properties
        try: output += f"{br}{style[6].replace(',', 'properties')}{''.join(f'{br}{prop}: {val}' for prop, val in obj.properties.items())}"
        except: pass
        #inventory
        if inventory:
            output += f"{br}{style[6].replace(',', 'inventory')}"
            br = '\n' + (indent+1) * tablen * ' '
            for thing in inventory:
                output += f"{self.pretty_tree(obj=thing, style=sub_style, indent=indent+1, tablen=tablen)}"
        #WIP: events
        # try:
        #     output += f"{br}{style[6].replace(',', 'events')}"
        #     br = '\n' + (indent+1) * tablen * ' '
        #     for event in obj.events:
        #         output += f"{self.pretty_tree(obj=self.eventhandler.events[event], style=sub_style, indent=indent+1, tablen=tablen)}"
        # except: pass
        return output 

    def display_tree(self, tablen=4):
        indent = 0
        output = self.pretty_tree(style='hearts', tablen=tablen)
        indent += 1
        for connection in self.connections.values():
            output += self.pretty_tree(obj=connection, style='light', tablen=tablen, indent=indent)
        output += self.pretty_tree(obj=self.player, style='star', inventory=self.player.inventory.values(), sub_style='double', tablen=tablen, indent=indent)
        for room in self.rooms.values():
            output += self.pretty_tree(obj=room, style='double', inventory=room.objects.values(), sub_style='double', tablen=tablen, indent=indent)
        return output

    def __str__(self):
        props = {key: prop for key, prop in self.properties.items()}
        rooms = [room for room in self.rooms]
        return f'WORLD [{self.gamefile}]: properties={str(props)}, rooms={str(rooms)}'

class Connection:
    """
    represents a connection between 2 rooms
    self.links= [room-ids]
    """
    instances = {}
    def __init__(self, tree):
        self.id = tree.get('id')
        self.properties = conv.unpack_properties(tree)
        self.links = []
        for link in tree.findall('link'): 
            self.links.append(link.text)
        Connection.instances[self.id] = self
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
    instances = {}
    def __init__(self, world, tree):
        self.world = world
        self.id = tree.get('id')
        self.properties = conv.unpack_properties(tree)
        self.objects = {}
        for obj in tree.findall('object'):
            self.objects[obj.get('id')] = GameObject(obj, self.world)
        self.events = []
        for event in tree.find('events').findall('event'):
            self.events.append(event.get('id'))
            self.world.eventhandler.events[event.get('id')] = self.world.eventhandler.parser.parse_xml(event)
        Room.instances[self.id] = self
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
        return f'[ROOM {self.id}] properties={str(props)}, objects={str(objects)}'