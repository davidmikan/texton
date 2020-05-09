from lxml import etree
x = etree.Element('test')
x.append(etree.Element('testt', text='123'))
print(x.find('testt').text)