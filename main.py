from lxml import etree
import time
import objects
import converter

def load():
    gamefile = 'game1.xml'
    global world
    global player
    global activeroom
    world, player = converter.loadworld(gamefile)
    activeroom = world.rooms[player.inroom]
    print('ROOMS: ' + str(world.rooms))
    print('PLAYER: ' + str(player))

def changeroom(destination):
    if world.rooms[destination] is not None:
        world.rooms[player.inroom] = activeroom
        player.inroom = destination
        activeroom = world.rooms[destination]
        print('You\'re in ' + activeroom.name)
        if activeroom.attr['visited'] == False: 
            print(activeroom.description)
            activeroom.attr['visited'] = True

def save():
    print('Saving...')
    converter.saveworld(world, player, 'test.xml')

def exitgame(input):
    save()
    print('Ending Session...')
    quit()

def action():
    while True:
        uinput = input('> ')
        for command in commandlist:
            if uinput.startswith(command):
                uinput = uinput[len(command)+1:]
                commandlist[command](uinput)
                break

commandlist = {
    'save': save,
    'exit': exitgame,
    'go to': changeroom
}

# world = converter.readtopy("game2.xml")
# activeroom = rooms[int(player.inroom)]
# print('Hello, ' + player.name + '! You\'re in room ' + activeroom.name)
# print(activeroom.description)
# activeroom.visited = True
load()
changeroom('2')
save()
#action()