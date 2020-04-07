from lxml import etree, objectify
import objects

with open('game1.xml') as f:
    test = f.read()
world = objectify.fromstring(test)           

rooms = []

def initialize():
    global rooms
    global activeroom
    for child in world.getchildren():
        if child.tag == "room":
            rooms.append(Room(child))

class Room:
    def __init__(self, room):
        self.connections = []
        self.visited = False
        self.id = room.get('id')
        self.name = room.name
        self.description = room.description
        if hasattr(room, 'player'):
            global player
            player = Player(room.player, room.get("id"))
        self.connections = str(room.connectsto).split(',')
        print("Initialized Room " + room.get('id') + ', name: ' + self.name)
        return

class Player:
    def __init__(self, player, inroom):
        self.name = input("What's your name?\n")
        self.inroom = inroom
        self.inventory = []
        for object in player.inventory.getchildren():
            object = objects.classifyobject(object)
            print(object.name)
            return
    def update(self, player, inroom):
        self.inroom = inroom
        return

def changeroom(destination):
    activeroom = rooms[int(player.inroom)]
    
    player.inroom = destination
    activeroom = rooms[int(player.inroom)]
    print('You\'re in ' + activeroom.name)
    if activeroom.visited == False: 
        print(activeroom.description)
        activeroom.visited = True

def save():
    print('Saving...')
    s = etree.tostring(world, pretty_print=True)
    with open('game2.xml', 'wb') as f:
        f.write(s)

def exitgame(input):
    print('Ending Session...')
    quit()

commandlist = {
    'save': save,
    'exit': exitgame,
    'go to': changeroom
}

initialize()
print(rooms)
activeroom = rooms[int(player.inroom)]
print('Hello, ' + player.name + '! You\'re in room ' + activeroom.name)
print(activeroom.description)
activeroom.visited = True

def action():
    while True:
        uinput = input('> ')
        for command in commandlist:
            if uinput.startswith(command):
                uinput = uinput[len(command)+1:]
                commandlist[command](uinput)
                break
#action()
save()