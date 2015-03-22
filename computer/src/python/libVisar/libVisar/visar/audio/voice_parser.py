import xml.etree.ElementTree as ET

class Parser(object):
  setting_tree = ET.parse('voice_control.xml')
  root_setting_xml = setting_tree.getroot()

  key_words = {}

  for child in root_setting_xml:
    key_words[child.get('name').lower()] = child.get('name').upper()

    if child.get('alias') == "True":
      for grandchildren in child:
        key_words[grandchildren.get('name').lower()] = child.get('name').upper()

  @classmethod
  def parse(self, text):
    words = text.split(' ')
    tup = ()
    for x in range(0, len(words)):
      command = ""
      args = ""
      
      for y in range(0, x):
        command + words[y]
      
      for y in range(x, len(words)):
        args + words[y]
      
      if command in self.key_words:
        tup = (command, args)
      else:
        break

    return tup

if __name__ == '__main__':
  print Parser.parse("Call Alpha Bravo")