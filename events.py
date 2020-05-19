from lxml import etree
import re

# nur für jetzt, wird noch geändert!

class EventHandler:

    """
    manages active events
    executes events
    contains predifined functions for Events
    """

    def __init__(self, world):
        self.world = world
        self.events = {}
        self.parser = EventDecoder(self)

    def check(self):
        """
        executes specifically active events
        in order world, playerobjects, activeroom, activeobjects
        """
        self.world.properties['steps'] += 1
        for eventid in self.world.events:
            self.check_event(eventid)
        for obj in self.world.player.inventory.values():
            for eventid in obj.events:
                self.check_event(eventid)
        for eventid in self.world.get_active_room().events:
            self.check_event(eventid)
        for obj in self.world.get_active_room().objects.values():
            for eventid in obj.events:
                self.check_event(eventid)

    def get_event(self, id):
        return self.events[id] or None

    # -- event execution -- #

    def check_event(self, eventid):
        """
        executes event when its if statements return true
        """
        if self.check_ifs(eventid): 
            self.execute_thens(eventid)

    def check_ifs(self,eventid):
        return all(self.compare(oneif) for oneif in self.events[eventid].ifs.values())

    def execute_thens(self, eventid):
        """
        executes 'then part' of an event
        names of functions and their corresponding object are mapped in a dictionary
        before execution placeholders in arguments are replaced by true value
        """
        # T E M P O R A R Y ! ! ! ! !
        functions = {
            'move': [self.world.move_object, 2],
            'say': [self.world.say, 1],
            'print': [print, 1]
        }
        for function, args in self.get_event(eventid).thens.items():
            args = self.parser.decode_arguments(args)
            if functions[function][1] == 1:
                functions[function][0](args[0])
            elif functions[function][1] == 2:
                functions[function][0](args[0], args[1])
            elif functions[function][1] == 3:
                functions[function][0](args[0], args[1], args[2])

    def compare(self, args) -> bool:
        """
        args = [value1, operator, value2]
        """
        args = self.parser.decode_arguments(args)
        result = eval(str(args[0]) + args[1] + str(args[2]))
        return result

    def save(self):
        return

    def __str__(self):
        return 'EVENTHANDLER'

class Event:

    """
    executable object
    syntax of self.ifs and self.ifs : {functionname: list of arguments}
    """

    def __init__(self, tree):
        self.id = tree.get('id')
        self.ifs = {}
        self.thens = {}

    def __str__(self):
        return f'EVENT {self.id}: ifs:{self.ifs}, thens:{self.thens}'

class EventDecoder:

    """
    for decoding events, which are packed in xml
    """

    def __init__(self, handler):
        self.handler = handler

    # -- Loading -- #
        

    def parse_xml(self, tree) -> Event:

        """
        takes lxml tree element <event>
        returns Event
        """
        event = Event(tree)
        # decode if elements
        for child in tree.find('if').getchildren():
            event.ifs[child.tag] = child.text.split(';')
        # decode then elements
        for child in tree.find('then').getchildren():
            if child.text:
                event.thens[child.tag] = child.text.split(';')
        return event

    # -- Saving -- #

    def pack_to_xml(self, event):
        
        """
        takes event object
        return lxml tree object <event>
        """

        tree = etree.Element('event')
        tree.set('id', event.id)
        ifs = etree.SubElement(tree, 'if')
        for name, args in event.ifs.items():
            x = etree.Element(name)
            x.text = ';'.join(args)
            ifs.append(x)
        thens = etree.SubElement(tree, 'then')
        for name, args in event.thens.items():
            x = etree.Element(name)
            x.text = ';'.join(args)
            thens.append(x)
        return tree

    # -- Executing -- #

    def decode_arguments(self, prearg) -> list:
        """
        takes list of pre-arguments
        replaces placesholder with true values
        returns list of arguments
        """
        arguments = []
        for x in prearg:
            if x.startswith('{') and x.endswith('}'):
                arguments.append(self.replace_var(x))
            else:
                if x in ['True', 'False']:
                    arguments.append(x == 'True')
                elif x.isdigit():
                    arguments.append(int(x))
                else:
                    arguments.append(x)
        return arguments

    def replace_var(self, expr): 
        """
        takes a string of like "{object/property}", with usaual syntax for placeholders
        returns requested object or property or None if nothing matching is found
        """
        expr = expr[1:-1].split('.')
        try:
            switch = {
            'o': (self.handler.world.get_object(expr[1]), 2),
            'r': (self.handler.world.get_room(expr[1]), 2),
            'w': (self.handler.world, 1),
            'p': (self.handler.world.player, 1)
            }
        except IndexError:
            switch = {
            'w': (self.handler.world, 1),
            'p': (self.handler.world.player, 1)
            }
        try:
            if len(expr) == switch[expr[0]][1]: return switch[expr[0]][0]
            return switch[expr[0]][0].get_property(expr[switch[expr[0]][1]])
        except:
            return None

        # if expr[0] == 'o':
        #     if len(expr) == 2: return self.handler.world.get_object(expr[1])
        #     return self.handler.world.get_object(expr[1]).get_property(expr[2])
        # elif expr[0] == 'r':
        #     if len(expr) == 2: return self.handler.world.get_room(expr[1])
        #     return self.handler.world.get_room(expr[1]).get_property(expr[2])
        # elif expr[0] == 'w':
        #     if len(expr) == 1: return self.handler.world
        #     return self.handler.world.get_property(expr[1])
        # elif expr[0] == 'p':
        #     if len(expr) == 1: return self.handler.world.player
        #     return self.handler.world.player.get_property(expr[1])
        # else:
        #     return None