from lxml import etree

def loadworld(gamefile):
    with open(gamefile, 'r') as f:
        xmlstring = etree.parse(f)
        return xmlstring

def saveworld(rootobj, gamefile):
    with open(gamefile, 'wb+') as f:
        f.write(etree.tostring(rootobj, pretty_print=True))
        return

def unpack_properties(element) -> dict:
    prop = {}
    for child in element.find('properties').getchildren():
        if not child.text:
            prop[child.tag] = ''
        elif child.tag in ('id', 'key'):
            prop[child.tag] = child.text
        elif child.text in ['True', 'False']:
            prop[child.tag] = bool(child.text=='True')
        elif child.text.isdigit():
            prop[child.tag] = int(child.text)
        else:
            prop[child.tag] = child.text
    return prop
   
def pack_properties(prop):
    propertyel = etree.Element('properties')
    for key in prop:
        x = etree.Element(key)
        x.text = str(prop[key])
        propertyel.append(x)
    return propertyel

def pack_events(events):
    tree = etree.Element('events')
    for event in events.values():
        tree.append(event.save())
    return tree