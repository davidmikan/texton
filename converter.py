from lxml import etree

def loadworld(gamefile): # can be moved to World
    with open(gamefile, 'r') as f:
        xmlstring = etree.parse(f)
        return xmlstring

def saveworld(rootobj, gamefile):
    with open(gamefile, 'wb+') as f:
        f.write(etree.tostring(rootobj, pretty_print=True))
        return

def unpack_properties(element) -> dict:
    """
    takes etree Element
    returns dictionary for children of <properties> tag with 
    key=tag, value=text
    """
    prop = {}
    for child in element.find('properties').getchildren():
        if not child.text:
            prop[child.tag] = ''
        elif child.tag == 'name':
            prop['name'] = child.text
        elif child.tag in ('id', 'key'):
            prop[child.tag] = child.text
        elif child.text in ['True', 'False']:
            prop[child.tag] = child.text == 'True'
        elif child.text.isdigit():
            prop[child.tag] = int(child.text)
        else:
            prop[child.tag] = child.text
    return prop
   
def pack_properties(prop):
    """
    takes dictionary
    returns etree Element 'properties'
    """
    propertyel = etree.Element('properties')
    for key in prop:
        x = etree.Element(key)
        x.text = str(prop[key])
        propertyel.append(x)
    return propertyel

def pack_events(events, handler):
    tree = etree.Element('events')
    for id in events:
        event = handler.get_event(id)
        element = handler.parser.pack_to_xml(event)
        tree.append(element)
    return tree
    