from lxml import etree
import json
import time
import objects
import converter

def load(gamefile):
    global world
    global player
    global activeroom
    with open('statusmsg.json') as f:
        testdict = json.load(f)
        print(testdict['take'])
    world, player = converter.loadworld(gamefile)
    activeroom = world.rooms[player.inroom]
    print('ROOMS: ' + str(world.rooms))
    print('PLAYER: ' + str(player))

def findroomid(name):
    for roomid, room in world.rooms.items():
        if name.lower() == room.properties['name'].lower(): 
            return roomid

def findobjid(name, ininventory=False):
    for objid, obj in activeroom.objects.items():
        if name.lower() == obj.properties['name'].lower(): 
            return objid, ininventory
    for objid, obj in player.inventory.items():
        if name.lower() == obj.properties['name'].lower(): 
            ininventory = True
            return objid, ininventory
    return None

def changeroom(arg=''):
    global activeroom
    destination = findroomid(arg)
    if destination is None:
        print('There\'s no room like that here.')
        return
    if player.inroom == destination:
        print('You are already here.')
        return
    for con in activeroom.connectsto:
        if destination in world.connections[con].links:
            if not world.connections[con].properties['locked']:

                # go into room
                world.rooms[player.inroom] = activeroom # save active room
                player.inroom = destination # set player position to destination room
                activeroom = world.rooms[destination] # set active room to destination room
                print('You\'re in ' + activeroom.properties['name'])
                if activeroom.properties['visited'] == False: 
                    print(activeroom.properties['description'])
                    activeroom.properties['visited'] = True
                return

            else:
                print('The way is locked.')
                return
    print('You can\'t go to that room.')

def lookat(arg=''):
    if arg.startswith('around'):
        print(activeroom.properties['description'])
    elif arg.startswith('at '):
        obj, ininv = findobjid(arg[3:])
        if obj is not None:
            if ininv: print(player.inventory[obj].properties['description'])
            elif not ininv: print(activeroom.objects[obj].properties['description'])
    else:
        print('There\' nothing like that here.')

def take(arg=''):
    obj, x = findobjid(arg)
    if obj is not None:
        player.inventory[obj] = activeroom.objects[obj]
        del activeroom.objects[obj]
        print('You picked up ' + player.inventory[obj].properties['name'] + '.')
    else:
        print('Nothing like that to pick up here.')

def drop(arg=''):
    obj, x = findobjid(arg)
    if obj is not None:
        activeroom.objects[obj] = player.inventory[obj]
        del player.inventory[obj]
        print('You dropped ' + activeroom.objects[obj].properties['name'] + '!')
    else:
        print('You can\'t drop something you don\'t have.')

def checkinv(arg=''):
    invobjects = []
    for objid, obj in player.inventory.items():
        invobjects.append(obj.properties['name'])
    if len(invobjects) == 0:
        print('You have nothing in your inventory!')
    else:
        msg = 'Your inventory consists of: '
        for thing in invobjects: msg+= thing
        print(msg)

def save(arg=''):
    print('Saving...')
    converter.saveworld(world, player, 'test.xml')

def exitgame(arg=''):
    save()
    print('Goodbye!')
    quit()

def action():
    while True:
        uinput = input('> ')
        for command in commandlist:
            if uinput.startswith(command):
                uinput = uinput[len(command)+1:]
                commandlist[command](arg=uinput)
                break

commandlist = {
    'save': save,
    'exit': exitgame,
    'go to': changeroom,
    'look': lookat,
    'take': take,
    'inventory': checkinv,
    'drop': drop
}

load('game1.xml')
action()