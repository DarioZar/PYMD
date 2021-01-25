from PyQt5 import QtGui, QtWidgets
from typing import Union

class MainController(object):

    def __init__(self, model):
        self.model = model

    #### widget event functions ####
    def change_element(self, text: str):
        self.model.element = text
    def change_fromFile(self, state: bool):
        self.model.fromFile = state
        self.model.fileName = "Insert .xyz file"
        self.model.number = None
        self.model.announce_update()
    def change_number(self, text: str):
        self.model.number = as_int(text)
    def change_rho(self, text: str):
        self.model.rho = as_float(text)
    def update_L(self):
        if self.model.number and self.model.rho and self.model.rho != 0:
            self.model.L = (self.model.number/self.model.rho)**(1/3)
        else:
            self.model.L = None
        self.model.announce_update()
    def change_statistics(self, index):
        self.model.statistics = index
        self.model.announce_update()
    def change_t0(self, text: str):
        self.model.t0 = as_float(text)
    def change_rc(self, text: str):
        self.model.rc = as_float(text)
    def change_tBath(self, text: str):
        self.model.tBath = as_float(text)
    def change_nu(self, text: str):
        self.model.nu = as_float(text)
    def change_eCorr(self, state: bool):
        self.model.eCorr = state
    def change_steps(self, text: str):
        self.model.steps = as_int(text)
    def change_dt(self, text: str):
        self.model.dt = as_float(text)
    def change_output(self, text: str):
        self.model.output = text
    def change_fSamp(self, text: str):
        self.model.fSamp = as_int(text)
    def change_unfold(self, state: bool):
        self.model.unfold = state
    def change_singleFile(self, state: bool):
        self.model.singleFile = state
    
    def change_start(self, checked):
        self.model.start = checked
        if checked:
            self.model.startSimulation()
        self.model.announce_update()
    
    def change_browseFile(self, checked, fileName):
        if fileName:
            self.model.setFile(fileName)
        self.model.announce_update()

    

def as_int(text: str) -> Union[int, None]:
        try:
            num = int(text)
        except ValueError:
            num = None
        return num
    
def as_float(text: str) -> Union[float, None]:
        try:
            num = float(text)
        except ValueError:
            num = None
        return num