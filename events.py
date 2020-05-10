from lxml import etree
import re


class EventHandler:
    def __init__(self, world, tree):
        self.world = world
        self.events = {}
        self.parser = EventParser(self)

    def check(self):
        self.world.properties['steps'] += 1

    def save(self):
        return

    def __str__(self):
        return 'EVENTHANDLER'

class Event:
    def __init__(self, tree):
        self.id = tree.get('id')
        self.ifs = {}
        self.thens = {}
        return

    def check_ifs(self):
        for condition in self.ifs:
            pass

    def save(self):
        tree = etree.Element('event')
        tree.set('id', self.id)
        for ifkey, ifval in self.ifs.items():
            iftree = etree.Element(ifkey)
            iftree.text = ifval
            tree.append(iftree)
        for thenkey, thenval in self.thens.items():
            thentree = etree.Element(thenkey)
            thentree.text = thenval
            tree.append(thentree)
        return tree

    def __str__(self):
        return f'EVENT {self.id}: ifs:{self.ifs}, thens:{self.thens}'

class EventParser: #WIP

    def __init__(self, handler):
        self.handler = handler

    def parse_xml(self, tree) -> Event:
        event = Event(tree)
        # decode if elements
        for child in tree.find('if').getchildren:
            pass
    
    def decode_event(self, expr) -> list:
        #takes string and returns list of arguments
        pass
    
    def replace_var(self, expr): #takes string of form {o.001.name}, returns different types
        expr = expr[1:-1].split('.')
        if expr[0] == 'o':
            if not expr[2]: return self.world.get_object(expr[1])
            return self.world.get_object(expr[1]).get_property(expr[2])
        elif expr[0] == 'r':
            pass
        elif expr[0] == 'w':
            pass
        elif expr[0] == 'p':
            pass
        else:
            return None
