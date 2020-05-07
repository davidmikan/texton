from lxml import etree
import re

class Event:
    def __init__(self, ev):
        self.id = ev.get('id')
        self.x = 'Hello World'

    def check(self):
        print(str(world.rooms))

    def save(self):
        event = etree.Element('event')
        event.set('id', self.id)
        return event

def check():
    print('checked')

def findobj(id, world, player, activeroom):
    return

def math(expressions):
    expressions = expressions.split(';')
    for exp in expressions:
        pass
        print(exp)

