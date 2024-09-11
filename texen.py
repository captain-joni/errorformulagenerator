import numpy as np
import sympy as sp
from pytexit import py2tex
import sys

formula = str(sys.argv[1])

py2tex(formula, print_latex = True)