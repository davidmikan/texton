from lxml import etree, objectify

with open('game1.xml') as f:
    test = f.read()
world = objectify.fromstring(test)           

rooms = []

def initialize():
    global rooms
    for child in world.getchildren():
        if child.tag == "room":
            rooms.append(Room(child))
            print("Initialized Room " + child.get("id"))

class Room:
    def __init__(self, room):
        self.connections = [] 
        self.isactive = False
        if hasattr(room, 'player'):
            self.isactive = True
            global player
            player = Player(room.player, room.get("id"))
        self.connections = str(room.connectsto).split(',')
        return

class Player:
    def __init__(self, player, inroom):
        self.name = input("What's your name?\n")
        self.inroom = inroom
        return
    def update(self, player, inroom):
        self.inroom = inroom
        return

initialize()
print(rooms)
print(rooms[0].isactive, rooms[0].connections)
print(player.name, player.inroom)

