import logging
import os
import lib

class base_class:
    '''
    Container Class for MIRIAD Tasks
    '''
    def __init__(self, task, **kwargs):
        self.__dict__.update(kwargs)
        self.task = task
    def __getitem__(self, key):
        return getattr(self, key)
    def keywords(self):
        lib.masher(task=self.task+" -kw")
    def help(self):
        lib.masher(task=self.task+" -k")
    def go(self):
        '''
        Should run the entire thing.
        '''
        output = lib.masher(**self.__dict__)
        logger = logging.getLogger(self.task)
        logger.info('Completed.')

class crosscal:
    '''
    Main class that does selfcal
    '''
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    def __getitem__(self, key):
        return getattr(self, key)
    def go(self):
        '''
        Should run the entire thing.
        '''
        wsrtfits.go()

wsrtfits = base_class('wsrtfits')
wsrtfits.in_ = ""
wsrtfits.op = 'uvin'
wsrtfits.velocity='optbary'
wsrtfits.out = ''
