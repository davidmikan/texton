from lxml import etree
import re

class EventHandler:
    def __init__(self, world, tree):
        self.world = world
        self.parser = []

    def check(self):
        self.world.properties['steps'] += 1

    def save(self):
        return

    def __str__(self):
        return f'EVENTHANDLER: DONT KNOW WHAT TO PUT IN HERE'

class Event:
    def __init__(self, tree):
        self.id = tree.get('id')
        self.ifs = {}
        for child in tree.find('if').getchildren():
            self.ifs[child.tag] = child.text
        self.thens = {}
        for child in tree.find('then').getchildren():
            self.thens[child.tag] = child.text
        return

    def check_ifs(self):
        for condition in self.ifs:

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

class EventParser:

    def argument_parser(expr) -> list:
        # -- READ ME -- #
        #
        