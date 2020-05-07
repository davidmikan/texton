from lxml import etree
import re
import json
import objects
import converter

def load(gamefile):
    global messages
    converter.loadworld(gamefile)
    objects.activeroom = objects.world.rooms[objects.player.inroom]
    print('ROOMS: ' + str(objects.world.rooms))
    print('PLAYER: ' + str(objects.player))
    with open('statusmsg.json') as f:
        messages = json.load(f)

def findroomid(name):
    for roomid, room in objects.world.rooms.items():
        if name.lower() == room.properties['name'].lower(): 
            return roomid

def findobjid(name, ininventory=False):
    for objid, obj in objects.activeroom.objects.items():
        if name.lower() == obj.properties['name'].lower(): 
            return objid, ininventory
    for objid, obj in objects.player.inventory.items():
        if name.lower() == obj.properties['name'].lower(): 
            ininventory = True
            return objid, ininventory
    return None

def changeroom(arg=''):
    destination = findroomid(arg)
    if destination is None:
        say('room_notfound')
        return
    if objects.player.inroom == destination:
        say('room_alreadyactive')
        return
    for con in objects.activeroom.connectsto:
        if destination in objects.world.connections[con].links:
            if not objects.world.connections[con].properties['locked'] or unlockroom(con):

                # go into room
                objects.world.rooms[objects.player.inroom] = objects.activeroom # save active room
                objects.player.inroom = destination # set player position to destination room
                objects.activeroom = objects.world.rooms[destination] # set active room to destination room
                say('room_entered', objects.activeroom)
                if objects.activeroom.properties['visited'] == False: 
                    print(objects.activeroom.properties['description'])
                    objects.activeroom.properties['visited'] = True
                return

            else:
                say('room_locked')
                return
    say('room_accessfailed')

def unlockroom(id):
    if objects.world.connections[id].properties['key'] in objects.player.inventory:
        objects.world.connections[id].properties['locked'] = False
        return True
    return False

def lookat(arg=''):
    if arg.startswith('around'):
        print(objects.activeroom.properties['description'])
    elif arg.startswith('at '):
        obj, ininv = findobjid(arg[3:])
        if obj is not None:
            if ininv: print(objects.player.inventory[obj].properties['description'])
            elif not ininv: print(objects.activeroom.objects[obj].properties['description'])
    else:
        say('object_notfound')

def take(arg=''):
    obj, x = findobjid(arg)
    if obj is not None:
        objects.player.inventory[obj] = objects.activeroom.objects[obj]
        del objects.activeroom.objects[obj]
        say('object_taken', objects.player.inventory[obj])
    else:
        say('object_notfound')

def drop(arg=''):
    obj, x = findobjid(arg)
    if obj is not None:
        objects.activeroom.objects[obj] = objects.player.inventory[obj]
        del objects.player.inventory[obj]
        say('object_dropped', objects.activeroom.objects[obj])
    else:
        say('object_notininv')

def checkinv(arg=''):
    invobjects = []
    for obj in objects.player.inventory.values():
        invobjects.append(obj.properties['name'])
    if len(invobjects) == 0:
        say('inventory_empty')
    else:
        msg = messages['inventory_list'] + ' '
        for thing in invobjects: msg+= '; '+thing
        print(msg)

def say(key, obj=None):
    output = messages[key]
    if obj is not None:
        for prop in re.findall(r'\{(.+?)\}', output):
            output = output.replace('{'+prop+'}', obj.properties[prop])
    print(output)

def save(arg=''):
    say('world_saving')
    if converter.saveworld(objects.world, objects.player, 'test.xml'): say('world_saved')
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
                # call command, run check
                uinput = uinput[len(command)+1:]
                commandlist[command](arg=uinput)
                objects.events.check()
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