from lxml import etree
import re


class EventHandler:
    def __init__(self, world):
        self.world = world
        self.events = {}
        self.parser = EventParser(self)

    def check(self):
        self.world.properties['steps'] += 1
        # execute world events
        for eventid in self.world.events:
            self.check_event(eventid)
        # execute active room events
        for eventid in self.world.get_active_room().events:
            self.check_event(eventid)
        # execute active room object events
        for obj in self.world.get_active_room().objects.values():
            for eventid in obj.events:
                self.check_event(eventid)
        # players inventory objects events
        for obj in self.world.player.inventory.values():
            for eventid in obj.events:
                self.check_event(eventid)

    # -- event execution -- #

    def check_event(self, eventid):
        event = self.get_event(eventid)
        if event.check_ifs():
            self.execute_thens(event)
        return
            
        print('Executed event', eventid)
        return

    def check_thens(self, event):
        for function, arguments in event.thens.items:
            function = function + '(arguments)'
            arguments = self.parser.decode_arguments(arguments)
            exex(function)
        return

            

    # -- pre-defined functions -- #


    def save(self):
        return

    def get_event(self, id):
        return self.events[id] or None

    def __str__(self):
        return 'EVENTHANDLER'

class Event:
    def __init__(self, tree):
        self.id = tree.get('id')
        self.ifs = {}
        self.thens = {}
        return

    def check_ifs(self): #checks condition an return Boolean
        for condition in self.ifs:
            pass

    def __str__(self):
        return f'EVENT {self.id}: ifs:{self.ifs}, thens:{self.thens}'

class EventParser:

    def __init__(self, handler):
        self.handler = handler

    # -- Loading -- #
        
    def parse_xml(self, tree) -> Event:
        event = Event(tree)
        # decode if elements
        for child in tree.find('if').getchildren():
            event.ifs[child.tag] = child.text.split(';')
        # decode then elements
        for child in tree.find('then').getchildren():
            event.thens[child.tag] = child.text.split(';')
        return event

    # -- Saving -- #

    def pack_to_xml(self, event):
        # takes event object returns etree element
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
        #takes list of pre-arguments and returns list of arguments
        arguments = []
        for x in prearg:
            if x[0] == '{' and x[-1] == '}':
                arguments.append(self.replace_var(x))
            else:
                if x in ['True', 'False']:
                    arguments.append(x == 'True')
                elif x.isdigit():
                    arguments.append(int(x))
                elif x[0] == '~':
                    arguments.append(x[1:])
                else:
                    arguments.append(x)
        return arguments
    
    def replace_var(self, expr): #see documentation section "EventParser"
        expr = expr[1:-1].split('.')
        if expr[0] == 'o':
            if len(expr) == 2: return self.handler.world.get_object(expr[1])
            return self.handler.world.get_object(expr[1]).get_property(expr[2])
        elif expr[0] == 'r':
            if len(expr) == 2: return self.handler.world.get_room(expr[1])
            return self.handler.world.get_room(expr[1]).get_property(expr[2])
        elif expr[0] == 'w':
            if len(expr) == 1: return self.handler.world
            return self.handler.world.get_property(expr[1])
        elif expr[0] == 'p':
            if len(expr) == 1: return self.handler.world
            return self.handler.world.get_property(expr[1])
        else:
            return None
