from PyQt5.QtCore import QStringListModel, QThread
from pymd.element import available_elements, gen_element
from pymd.state import available_statistics, NVEState, NVTAndersenState
from pymd.atoms import Atoms
from pymd.util import xyz_in
from pymd.gui.model.SimulatorWorker import SimulatorWorker
import time

class Model(object):

    #### properties for value of Qt model contents ####
    @property
    def element_items(self):
        return self.element_model.stringList()
    @element_items.setter
    def element_items(self, value):
        self.element_model.setStringList(value)
    @property
    def statistics_items(self):
        return self.statistics_model.stringList()
    @statistics_items.setter
    def statistics_items(self, value):
        self.statistics_model.setStringList(value)

    def __init__(self):
        self._update_funcs = []

        #### create Qt models for compatible widget types ####
        self.element_model = QStringListModel()
        self.statistics_model = QStringListModel()
        self.element_items = available_elements()
        self.statistics_items = available_statistics()

        #### model variables ####
        self.element = "Ar"
        self.fromFile = False
        self.fileName = "Insert .xyz file"
        self.browseFile = False
        self.number = 216
        self.rho = 0.84
        self.L = (self.number/self.rho)**(1/3)
        self.statistics = 0
        self.t0 = 2
        self.rc = 3.5
        self.tBath = 4
        self.nu = 0.1
        self.eCorr = False
        self.steps = 10000
        self.dt = 0.001
        self.output = time.strftime("%Y%m%d-%H%M%S", time.localtime())
        self.fSamp = 1000
        self.unfold = False
        self.singleFile = True
        self.start = False

        self.atoms = None
        self.state = None

        self.worker = None

    def setSimulationData(self):
        element = gen_element(self.element)
        if self.fromFile:
            self.atoms = fromfile(self.rho, self.fileName)
        else:
            self.atoms = Atoms(self.number, self.rho, element)
        if self.statistics == 0:
            self.state = NVEState(self.atoms, self.t0, self.rc,
                                  self.eCorr)
        elif self.statistics == 1:
            self.state = NVTAndersenState(self.atoms, T0=self.t0,
                                          rc=self.rc,
                                          use_e_corr=self.eCorr,
                                          Tbath=self.tBath,
                                          nu=self.nu)

    def startSimulation(self):
        self.setSimulationData()
        values = {
            'steps' : self.steps,
            'dt'    : self.dt,
            'fSamp' : self.fSamp,
            'append': self.singleFile,
            'unfold': self.unfold,
            'outputfile' : self.output,
        }
        self.worker = SimulatorWorker(self.state, values)
        self.runSimulation(self.worker)
        self.announce_update()
    
    def runSimulation(self, worker):
        # Create a QThread object
        self.thread = QThread()
        # Create a worker object
        self.worker = worker
        # Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # Start the thread
        self.thread.start()

    def isInputValid(self) -> (bool, str):
        valid = False
        numattr = ["number", "rho", "L", "t0", "rc",
                   "steps", "dt", "fSamp"]
        addNumAttr = ['tBath', 'nu']
        vals = [getattr(self,n) for n in numattr]
        if self.statistics != 0:
            vals += [getattr(self, n) for n in addNumAttr]
        valid = all(v!=0 and v!= None for v in vals)
        if not valid:
            error = "Fill all numeric fields before\
                starting the simulation!"
        else:
            valid = valid and (self.rc < self.L/2)
            if not valid:
                error = "R_cutoff can't be greater than L/2"
            else:
                error = ""
        return valid, error

    def isFileValid(self, fileName: str):
        try:
            file = open(fileName, "r")
            self.number, _, _ = xyz_in(file)
            file.seek(0)
            next(file)
            next(file)
            self.element = next(file).split()[0]
            file.close()
            return True
        except Exception:
            return False

    def setFile(self, fileName: str):
        if self.isFileValid(fileName):
            self.fileName = fileName
        else:
            self.fileName = "File is not valid!"
            self.number = None
    
    def subscribe_update_func(self, func):
        if func not in self._update_funcs:
            self._update_funcs.append(func)

    def unsubscribe_update_func(self, func):
        if func in self._update_funcs:
            self._update_funcs.remove(func)

    def announce_update(self):
        for func in self._update_funcs:
            func()