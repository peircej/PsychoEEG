"""Some classes to support import of data files
"""

from psychoeeg import io
import os, time, pylab

thisDir = os.path.split(__file__)[0]

def test_load_DBPA_file(filepath = os.path.join(thisDir, 'someDat_')):
    t0 = time.time()
    datFile = io.DBPA_file(filepath)
    print 't=%.3f' %(time.time()-t0)
    print datFile.info
    print datFile.data.shape
    incr=0
    for n in range(100,120):
        incr+=0.00005
        pylab.plot(incr+datFile.data[n, :])
    pylab.show()
    assert datFile.info == {'channels': 122, 'duration': 10, 'rate': 1000, 'samples': 10000}
    
if __name__ == '__main__':
    test_load_DBPA_file()