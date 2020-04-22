from lxml import etree
import re
import json
import objects
import converter

def load(gamefile):
    global world
    global player
    global activeroom
    global messages
    world, player = converter.loadworld(gamefile)
    activeroom = world.rooms[player.inroom]
    print('ROOMS: ' + str(world.rooms))
    print('PLAYER: ' + str(player))
    with open('statusmsg.json') as f:
        messages = json.load(f)

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
        say('room_notfound')
        return
    if player.inroom == destination:
        say('room_alreadyactive')
        return
    for con in activeroom.connectsto:
        if destination in world.connections[con].links:
            if not world.connections[con].properties['locked'] or unlockroom(con):

                # go into room
                world.rooms[player.inroom] = activeroom # save active room
                player.inroom = destination # set player position to destination room
                activeroom = world.rooms[destination] # set active room to destination room
                say('room_entered', activeroom)
                if activeroom.properties['visited'] == False: 
                    print(activeroom.properties['description'])
                    activeroom.properties['visited'] = True
                return

            else:
                say('room_locked')
                return
    say('room_accessfailed')

def unlockroom(id):
    if world.connections[id].properties['key'] in player.inventory:
        world.connections[id].properties['locked'] = False
        return True
    return False

def lookat(arg=''):
    if arg.startswith('around'):
        print(activeroom.properties['description'])
    elif arg.startswith('at '):
        obj, ininv = findobjid(arg[3:])
        if obj is not None:
            if ininv: print(player.inventory[obj].properties['description'])
            elif not ininv: print(activeroom.objects[obj].properties['description'])
    else:
        say('object_notfound')

def take(arg=''):
    obj, x = findobjid(arg)
    if obj is not None:
        player.inventory[obj] = activeroom.objects[obj]
        del activeroom.objects[obj]
        say('object_taken', player.inventory[obj])
    else:
        say('object_notfound')

def drop(arg=''):
    obj, x = findobjid(arg)
    if obj is not None:
        activeroom.objects[obj] = player.inventory[obj]
        del player.inventory[obj]
        say('object_dropped', activeroom.objects[obj])
    else:
        say('object_notininv')

def checkinv(arg=''):
    invobjects = []
    for obj in player.inventory.values():
        invobjects.append(obj.properties['name'])
    if len(invobjects) == 0:
        say('inventory_empty')
    else:
        msg = messages['inventory_list'] + ' '
        for thing in invobjects: msg+= thing
        print(msg)

def say(key, obj=None):
    output = messages[key]
    if obj is not None:
        for prop in re.findall(r'\{(.+?)\}', output):
            output = output.replace('{'+prop+'}', obj.properties[prop])
    print(output)

def save(arg=''):
    say('world_saving')
    if converter.saveworld(world, player, 'test.xml'): say('world_saved')
    else: say('world_savefailed')

def exitgame(arg=''):
    save()
    say('world_quit')
    quit()

def action():
    while True:
        uinput = input('> ').lower()
        for command in commandlist:
            if uinput.startswith(command):
                uinput = uinput[len(command)+1:]
                commandlist[command](arg=uinput)
                break

commandlist = {
    'save': save,
    'exit': exitgame,
    'go to': changeroom, 'go': changeroom,
    'look': lookat,
    'take': take, 'pick up': take,
    'inventory': checkinv, 'show inventory': checkinv, 'check inventory': checkinv,
    'drop': drop
}

load('game1.xml')
action()