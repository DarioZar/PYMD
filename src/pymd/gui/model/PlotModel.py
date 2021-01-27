import pymd.atoms as mdatoms


class PlotModel(object):
    def __init__(self, output, atomsOutput, rc):
        self._update_funcs = []

        self.output = output
        self.atomsOutput = atomsOutput

        self.grStart = 0
        self.grStop = 10
        self.grStep = 1

        self.rc = rc
        self.dr = 0.1

    def calcGr(self):
        self.gr = mdatoms.pair_correlation(
            self.atomsOutput[self.grStart : self.grStop : self.grStep],
            self.rc,
            self.dr,
        )
        self.announce_update()

    def subscribe_update_func(self, func):
        if func not in self._update_funcs:
            self._update_funcs.append(func)

    def unsubscribe_update_func(self, func):
        if func in self._update_funcs:
            self._update_funcs.remove(func)

    def announce_update(self):
        for func in self._update_funcs:
            func()
