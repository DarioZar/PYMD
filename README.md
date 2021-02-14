# PYMD: PYthon Molecular Dynamics

Python package for MD simulations. Currently supporting NVE, NVT simulations with Lennard-Jones potential.

## Features
- PyQT GUI
- Object-Oriented API
- Fast force computation using Cython

## Installation
### Requirements
Python (pip) and gcc with math module
### Installing the package
1. Clone the repo
```bash
git clone https://github.com/DarioZar/pymd.git
```
2. Install using pip
```bash
pip install ./pymd
```

## Usage
```python
from pymd.element import gen_element
from pymd.atoms import Atoms
from pymd.state import NVTAndersenState

argon = gen_element("Ar")
atoms = Atoms(N=256, rho=0.8, elem=argon)
state = NVTAndersenState(atoms=atoms, T0=1.2, Tbath=1.2, nu=5, rc=3)

output, trajectory = state.simulate(s=10000, dt=0.001, fSamp=100)
```
