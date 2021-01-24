from pymd.element import available_elements, element, gen_element
from pymd.atoms import Atoms, fromfile
from pymd.state import available_statistics, NVEState, NVTAndersenState
from pymd.util import xyz_in
from typing import Union
from PyQt5.QtCore import pyqtSignal, QObject, QThread

class Model:
    def __init__(self):
        self.fileName = None
        self.mode = None
        self.values = dict.fromkeys({
            'N','elem','rho','t0','rc','steps','dt','fSamp','use_ecorr',
            'append','unfold','outputfile','Tbath','nu'
            })
        self.element = None
        self.atoms = None
        self.state = None
        self.result = None
    
    def isValid(self, fileName: str):
        try:
            file = open(fileName, "r")
            self.values['N'],_,_ = xyz_in(file) 
            print(self.values['N'])
            file.seek(0)
            next(file)
            next(file)
            self.values['elem'] = next(file).split()[0]
            file.close()
            return True
        except:
            return False
    
    def setFile(self, fileName: str):
        if self.isValid(fileName):
            self.fileName = fileName
        else:
            self.fileName = None
    
    def available_elements(self):
        return available_elements()
    
    def available_statistics(self):
        return available_statistics()

    def setSimulationData(self):
        self.element = gen_element(self.values['elem'])
        if self.fileName:
            self.atoms = fromfile(self.values['rho'],self.fileName)
        else:
            self.atoms = Atoms(self.values['N'], self.values['rho'], self.element)
        if self.mode == 0:
            self.state = NVEState(self.atoms, self.values['t0'],
                                  self.values['rc'], self.values['use_ecorr'])
        elif self.mode == 1:
            self.state = NVTAndersenState(self.atoms, self.values['t0'],
                                          self.values['rc'], self.values['use_ecorr'])