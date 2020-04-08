from lxml import etre
import objects

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

world = converter.readtopy("game2.xml")
activeroom = rooms[int(player.inroom)]
print('Hello, ' + player.name + '! You\'re in room ' + activeroom.name)
print(activeroom.description)
activeroom.visited = True
