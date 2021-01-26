import json
import os
from math import sqrt
from typing import List


class Element:
    """
    Element object, with information about normal units.

    Attributes:
        name (str): name of element
        mass (float): mass of element
        sigma (float): sigma, in Lennard-Jones potential
        eps (float): epsilon, in Lennard-Jones potential
        units (Dict[str,float]): normal units for element
    """

    def __init__(self, name: str, mass: float, sigma: float, eps: float):
        """
        Initialize element.

        Args:
            name (str): name of element
            mass (float): mass of element
            sigma (float): sigma, in Lennard-Jones potential
            eps (float): epsilon, in Lennard-Jones potential
        """
        # Boltzmann constant
        k = 1.380649e-23
        self.name = name
        self.mass = mass * 1.661e-27
        self.sigma = sigma * 1e-9
        self.eps = eps * k
        self.units = {
            "length": self.sigma,
            "energy": self.eps,
            "mass": self.mass,
            "time": self.sigma * sqrt(self.mass / self.eps),
            "rho": self.mass / (self.sigma ** 3),
            "temp": self.eps / k,
            "pressure": self.eps / (self.sigma ** 3),
            "velocity": sqrt(self.eps / self.mass),
            "force": self.eps / self.sigma,
        }

    def __str__(self):
        return f"{self.name}, mass={self.mass:.3e} Kg, \
            sigma={self.sigma:.3e} m, epsilon={self.eps:.3e} J"


def gen_element(name: str) -> Element:
    """
    Generate element, retrieving data from the species JSON file.

    Args:
        name (str): element chemical symbol

    Raises:
        Exception: if name is not defined in the species.json file

    Returns:
        Element: element object
    """
    if name not in available_elements():
        raise Exception("Element not defined in species.json")
    path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(path, "data", "species.json")
    with open(filename, "r") as f:
        species = json.load(f)
        elem = species["name" == name]
    elem = Element(name, elem["mass"], elem["sigma"], elem["eps"])
    return elem


def available_elements() -> List[str]:
    """
    List of elements defined in the species.json file

    Returns:
        List[str]: list of elements defined in the species.json file
    """
    path = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(path, "data", "species.json")
    with open(filename, "r") as f:
        species = json.load(f)
        elem_list = [specie["name"] for specie in species]
    return elem_list
