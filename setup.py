from setuptools import Extension, setup
from Cython.Build import cythonize
import toml
from numpy import get_include

# Choose build option from toml file
options = toml.load("pyproject.toml")["build-system"]
PARALLEL   = options["parallel"]
PUREPYTHON = options["purepython"]

extensions = []

if not PUREPYTHON:
    cythonfile = "src/cython/force_LJ"
    cythonfile += "_par.pyx" if PARALLEL else ".pyx"
    extensions += [
        Extension(name="force_LJ", sources=[cythonfile],
        include_dirs=[get_include()])
    ]

# Build extensions
if __name__ == "__main__":
    setup(ext_modules=cythonize(extensions, nthreads=4))
