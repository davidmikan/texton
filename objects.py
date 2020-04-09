from lxml import etree

class World:
	def __init__(self, tree):
		self.playsession = tree.get('playsession')
		#properties
		self.properties = get_prop(tree)
		#events
		self.events = {}
		#rooms
		self.rooms = {}
		for room in tree.findall('room'):
			self.rooms[room.get('id')] = Room(room)
		return
	def save(self):
		world = etree.Element('world')
		world.set('playsession', self.playsession)
		#properties
		world.append(prop_xml(self.properties))
		#events
		#rooms
		for room in self.rooms.values():
			world.append(room.save())
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
        

def get_prop(element):
	prop = {}
	for child in element.find('properties').getchildren():
			prop[child.tag] = child.text
	return prop
	
def prop_xml(prop):
	property = etree.Element('properties')
	for key in prop:
		x = etree.Element(key)
		x.text = prop[key]
		property.append(x)
	return property