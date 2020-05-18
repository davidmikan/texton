import json
import world as wrld
import converter as conv

def go_to_room(uinput):
    old_room = world.get_active_room()
    active_room = world.move_to_room(world.get_room_id(uinput))
    if active_room is not None:
        description = ''
        if active_room.get_property('visited'): description += '\n' + active_room.get_property('description')
        print(
            'You\'re in',
            active_room.get_property('name'),
            'now!',
            description
        )
    else:
        world.say('room_notfound')

def exit(uinput):
    world.save('files/test.xml')
    print(uinput)
    quit()

world = wrld.World('files/game1.xml')
commands = {
    'exit': exit,
    'go to': go_to_room
}
print('SESSION: ' + str(world.get_property('session')))
world.say('world_loaded')

while True:
    print('\nSTEP: ' + str(world.get_property('steps')))
    uinput = input('> ')
    for command in commands:
        if uinput.startswith(command):
            world.step()
            commands[command](uinput[len(command):].strip())
            break
    