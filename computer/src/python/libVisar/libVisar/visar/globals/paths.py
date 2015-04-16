import os
import sys


class Paths(object):

    @staticmethod
    def get_path_to_file(_file):
        '''Call this with the argument '__file__'
        ex:
            >>> Paths.get_path_to_file(__file__)

        This is the only way you will ever call this function, with this exact text
        '''
        absolute_file_path = os.path.dirname(os.path.realpath(_file))
        return absolute_file_path

    @staticmethod
    def get_path_to_visar():
        this_path = Paths.get_path_to_file(__file__)
        visar_path = os.path.join(this_path, '..', '..')
        return visar_path


if __name__ == '__main__':
    print Paths.get_path_to_file(__file__)
    print Paths.get_path_to_visar()