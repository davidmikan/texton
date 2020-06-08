import world as wrld

def process_uinput(uinput):
    """
    takes raw user input as argument and returns (command, arguments)

    TODO:
        * process input
        * define return syntax
    """
    global commands
    uinput = uinput.lower().strip()

    # test for command
    for command in commands:
        if uinput.startswith(command): break
        else: command = None
    if not command:
        return (None,None)

    # process arguments
    
    arguments = uinput[len(command):].strip()
    return (command, arguments)

 # -- commands -- #

def go_to_room(uinput):
    destination = world.move_to_room(world.get_room_id(uinput)) or world.move_to_room(uinput)
    if destination is not None:
        description = ''
        if destination.get_property('visited'): description += '\n' + destination.get_property('description')
        print(
            'You\'re in',
            destination.get_property('name'),
            'now!',
            description
        )
    else:
        world.say('room_notfound')

def teleport_to_room(uinput):
    """
    TODO: dont bypass World.move_to_room, use it's byplayer functionality
    """
    destination = world.move_to_room(world.get_room_id(uinput), byplayer=False) or world.move_to_room(uinput, byplayer=False)
    if destination is not None:
        description = ''
        if destination.get_property('visited'): description += '\n' + destination.get_property('description')
        print(
            'You\'re in',
            destination.get_property('name'),
            'now!',
            description
        )
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
        command, arguments = process_uinput(input('> '))
        if not command:
            world.say('command_not_found')
            continue
        world.step()
        commands[command](arguments)
