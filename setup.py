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
    cythonfile  = "src/cython/force_LJ"
    cythonfile += "_par.pyx" if PARALLEL else ".pyx"
    compileargs = ["-03", "-ffast-math", "-march=native"]
    compileargs+= ["-fopenmp"] if PARALLEL else []
    linkargs    = ["-fopenmp"] if PARALLEL else []
    extensions += [
        Extension(name="pymd.force_LJ", sources=[cythonfile],
        include_dirs=[get_include()],
        extra_compile_args=compileargs,
        extra_link_args=linkargs)
    ]

# Build extensions
if __name__ == "__main__":
    setup(ext_modules=cythonize(extensions, nthreads=4))
