class PlotController(object):
    def __init__(self, model):
        self.model = model

    def change_units(self, id):
        self.model.change_units(id)
        self.model.announce_update()

    def change_buttonId(self, id):
        self.model.var = id + 1
        self.model.change_units(self.model.units)
        self.model.announce_update()

    def change_dr(self, value: float):
        self.model.dr = value

    def change_start(self, value: int):
        self.model.grStart = value

    def change_stop(self, value: int):
        self.model.grStop = value

    def change_step(self, value: int):
        self.model.grStep = value

    def change_plot(self):
        self.model.calcGr()
