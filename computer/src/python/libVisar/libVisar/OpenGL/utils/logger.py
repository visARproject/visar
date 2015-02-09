class Logger(object):
    ''' Verbosity:
        0 -> Do nothing
        1 -> print warnings
        2 -> print warnings and log messages
    '''
    verbosity = 0
    max_verbosity = 2

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
            print 'VISAR Log:', out_str

    @classmethod
    def warn(self, *args):
        if self.verbosity > 0:
            out_str = " ".join([str(i) for i in args])
            print 'VISAR Warning:', out_str