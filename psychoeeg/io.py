"""Some classes to support import of data files
"""

import os, glob
import numpy
import time

try:
    import ConfigParser as configparser #gets rename to lowercase in python 3
except:
    import configparser

class _BaseDataFile(object):
    """
    """
    def __init__(self, filepath):
        """
        """
        self.filepath = filepath
        self.info = self._loadHeader()
        self.data = self._loadData()
    def _findFile(self, ending='', orSimilar=False):
        """Finds files using the base filename and the optional `ending` param (used to separate data from header)
        
        If orSimilar==True then this function will first search for the exact file and then for any file of the appropriate
        format in that folder. (For a header file that can be useful, just to retrieve the 
        """
        #fetch all header/data files matching path
        searchPattern = self.filepath+'*'+ending
        filenames = glob.glob(searchPattern)
        #check if we have exactly one matching file
        filename=None
        if len(filenames)==0 and orSimilar:
            folder = os.path.split(os.path.abspath(self.filepath))[0]
            print('No exact match found for\n\t %s' %(searchPattern))
            searchPattern = os.path.join(folder, '*'+ending)
            print('...searching instead for\n\t %s' %(searchPattern))
            filenames = glob.glob(searchPattern)
        
        if len(filenames)==0:
            print('No file found: %s' %(searchPattern))
        elif len(filenames)>1:
            print('Multiple files found')
        else:
            filename = filenames[0]
        return filename

class DBPA_file(_BaseDataFile):
    """
    DBPA amplifiers are made by Sensorium. Excellent signal to noise on the amp, with a very basic file format -
    a 5-line ASCII header file (config-style file) and a binary data file.
    
    Example usage:
        datFile = io.DBPA_file('jwp_2013_18_02') #don't include file extension
        print datFile.info  #print the header info (samples, seconds etc)
            {'channels': 122, 'duration': 761, 'rate': 1000, 'samples': 761000}
        print datFile.data.shape
            (122, 761000) #channels, samples
            
    """
    def _loadHeader(self):
        """Load info from a header file ('*.h.txt')
        """
        filename = self._findFile(ending='h.txt', orSimilar=True)
        if not filename:
            print('No header file')
        #this header file looks like a config file with a single section
        cfg = configparser.ConfigParser()
        hdr = {}
        f = open(filename)
        cfg.readfp(f) #operates in place (doesn't return anything)
        f.close()
        hdr['channels'] = cfg.items('File Information')
        for name, val in cfg.items('File Information'): #reads entries in File Info section as a list of tuples
            if name.lower()=='number of channels':
                hdr['channels']=int(val.replace('"', '')) # convert '"200"' to 200
            elif name.lower()=='samples per second':
                hdr['rate']=int(val.replace('"', '')) # convert '"200"' to 200
        return hdr

    def _loadData(self):
        """

        :param offset: the sample number to start reading from
        """
        data = []
        filename = self._findFile(ending='dat')
        fileSize = os.stat(filename).st_size
        self.info['duration'] = int(fileSize/self.info['rate']/self.info['channels']/4) #4 bytes per sample
        self.info['samples'] = self.info['duration']*self.info['rate']
        if not filename:
            print('No data file')
        fileSize = os.stat(filename).st_size
        data = numpy.fromfile(filename, dtype='>f')# data are big-endian float32
        data = data.reshape([self.info['samples'],self.info['channels']])
        data = data.transpose() # to get (channels, time)
        return data
