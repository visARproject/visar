from colorama import Fore, Back, Style
import sys

class Logger(object):
    ''' 
    Verbosity:
        0 -> Do nothing
        1 -> print warnings
        2 -> print warnings and log messages

    Colorama Examples:
        print(Fore.RED + 'some red text')
        print(Back.GREEN + 'and with a green background')
        print(Style.DIM + 'and in dim text')
        print(Fore.RESET + Back.RESET + Style.RESET_ALL)
        print('back to normal now')

    '''
    verbosity = 0
    max_verbosity = 2
    reset_color = Fore.RESET + Back.RESET + Style.RESET_ALL

    @classmethod
    def set_verbosity(self, verbosity):
        if isinstance(verbosity, str):
            mapping = {
                'low': 1,
                'off': 0,
                'warn': 1,
                'log': 2,
            }
            assert verbosity in mapping.keys(), "Unknown verbosity type, {}".format(verbosity)
            verbosity = mapping[verbosity.lower()]
            
        assert 0 <= verbosity <= self.max_verbosity, "Verbosity out of range"
        self.verbosity = verbosity

    @classmethod
    def log(self, *args):
        if self.verbosity > 1:
            out_str = " ".join([str(i) for i in args])
            print Fore.BLUE + '[VISAR Log]:', out_str + self.reset_color

    @classmethod
    def warn(self, *args):
        if self.verbosity > 0:
            out_str = " ".join([str(i) for i in args])
            print Fore.RED + '[VISAR Warning]:', out_str + self.reset_color
