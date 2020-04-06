from lxml import etree, objectify

with open('game1.xml') as f:
    test = f.read()
world = objectify.fromstring(test)

class Room:
    def __init__(self, room):
        self.connections = [] 
        self.isactive = False
        if hasattr(room, 'player'): # 
            self.isactive = True
            global player
            player = Player(room.player, room.get('id'))
        self.connections = str(room.connectsto).split(',')

class Player:
    def __init__(self, player, inroom):
        self.inroom = inroom
        self.name = input('What\'s your name?\n')
        
activeroom = Room(world.room[0])
print(player.name)