class StandardObject:
    def __init__(self, item):
        self.name = item.name

types = {
    'standard': StandardObject
}

def classifyobject(object):
    object = types[(object.get('type'))](object)
    return object