import xml.etree.ElementTree as ET
import os
from ...OpenGL.utils import Logger

class Parser(object):
    # path leading to this file
    fpath = os.path.dirname(os.path.realpath(__file__))

    # xml that is holding all aliases
    vc_xml_dir = os.path.join(fpath, 'voice_control.xml')
    vc_setting_tree = ET.parse(vc_xml_dir)
    vc_root_setting_xml = vc_setting_tree.getroot()

    # xml that is holding all of the subs for the letters or numbers
    anr_xml_dir = os.path.join(fpath, 'alpha-numeric_replacements.xml')
    anr_setting_tree = ET.parse(anr_xml_dir)
    anr_root_setting_xml = anr_setting_tree.getroot()

    # dictionary for key words
    key_words = {}

    # get all key words, convert them to lowercase, and save in dictionary
    for child in vc_root_setting_xml:
        key_words[child.get('name').lower()] = child.get('name').lower()

        if child.get('alias') == "True":
            for grandchildren in child:
                key_words[grandchildren.get('name').lower()] = child.get('name').lower()

    # dictionary for replacements
    replacements = {}

    # get all replacements and put them in dictionary
    for child in anr_root_setting_xml:
        replacements[child.get('name').lower()] = child.get('return').upper()

    @classmethod
    def parse(self, text):
        words = text.split(' ')

        # handle one word text segments
        if len(words) == 1:
          if text.lower() in self.key_words:
            return (self.key_words[text.lower()], '')
          else:
            return ('',text)
            
        # find command and seperate the rest as arguments
        tup = ()
        command = ""
        args = ""
        for x in range(1, len(words)):
            test_command = ""
            test_args = ""

            for y in range(0, x):
                if y == 0:
                    test_command = words[y]
                else:
                    test_command += " " + words[y]
          
            for y in range(x, len(words)):
                if y == len(words) - 1:
                    test_args += words[y]
                else:
                    test_args += words[y] + " "

            if test_command.lower() in self.key_words:
                command = self.key_words[test_command.lower()]
                args = test_args
            else:
                break

        # Logger.log('tuple: %s' % (tup,)) #Debug

        args_list = args.split(' ')

        # replace words with what they are replacing
        # e.g. alpha = a, zero = 0
        args = ""
        for x in args_list:
            if x.lower() in self.replacements:
                args += self.replacements[x.lower()]

        tup = (command, args)

        return tup

if __name__ == '__main__':
    print Parser.key_words
    print Parser.parse("Call Now Alpha Bravo")
