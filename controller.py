import world as wrld

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

def teleport_to_room(uinput):
    if world.set_active_room(world.get_room_id(uinput)) is not None:
        print('woosh')
    else:
        world.say('room_notfound')

def save(uinput):
    world.say('world_saving')
    world.save(uinput)
    world.say('world_saved')

def exit(uinput):
    save(uinput)
    world.say('world_quit')
    quit()

if __name__ == '__main__':
    world = wrld.World('files/game1.xml')
    commands = {
        'exit': exit,
        'save': save,
        'go to': go_to_room,
        'teleport to': teleport_to_room
    }
    print('SESSION: ' + str(world.get_property('session')))

    while True:
        print('\nSTEP: ' + str(world.get_property('steps')))
        uinput = input('> ')
        for command in commands:
            if uinput.startswith(command):
                world.step()
                commands[command](uinput[len(command):].strip())
                break
