import toml
from Cython.Build import cythonize
from numpy import get_include
from setuptools import Extension, setup

# Choose build option from toml file
options = toml.load("pyproject.toml")["build-system"]
PARALLEL = options["parallel"]
GUI = options["gui"]

extensions = []

# Lennard-Jones Cython Extension
cythonfile = "src/cython/force_LJ"
cythonfile += "_par.pyx" if PARALLEL else ".pyx"
compileargs = ["-O3", "-ffast-math", "-march=native"]
compileargs += ["-fopenmp"] if PARALLEL else []
linkargs = ["-fopenmp"] if PARALLEL else []
extensions += [
    Extension(
        name="pymd.force_LJ",
        sources=[cythonfile],
        include_dirs=[get_include()],
        extra_compile_args=compileargs,
        extra_link_args=linkargs,
    )
]

# Pair Correlation Cython Extension
cythonfile = "src/cython/pair_corr"
cythonfile += "_par.pyx" if PARALLEL else ".pyx"
compileargs = ["-O3", "-lm", "-ffast-math", "-march=native"]
compileargs += ["-fopenmp"] if PARALLEL else []
linkargs = ["-fopenmp"] if PARALLEL else []
extensions += [
    Extension(
        name="pymd.pair_corr",
        sources=[cythonfile],
        include_dirs=[get_include()],
        extra_compile_args=compileargs,
        extra_link_args=linkargs,
    )
]

install_requires = ["numpy", "matplotlib"]
if GUI:
    install_requires += ["pyqt5"]

# Build extensions
if __name__ == "__main__":
    setup(
        install_requires=install_requires,
        ext_modules=cythonize(extensions, nthreads=4),
    )
