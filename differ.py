import numpy as np
import sympy as sp
from pytexit import py2tex
import sys

formula = str(sys.argv[1])
variablese = sys.argv[2]


 
werte = variablese.split(",")
anzahl_variablen = 0
for i in werte:
    anzahl_variablen += 1

anzahl_variablen_2 = range(anzahl_variablen)



#Dieser Speicher hat als keys die var_i und als values die variable nach der abgeleitet wird.
speicher = {}
for i, wert in enumerate(werte,0):
    speicher[f"var_{i}"] = wert



werte =  sp.symbols(str(werte))



speicher_2 = {}  # Speicher die Ableitungen in key = d_i und value = ableitung nach index

for i in anzahl_variablen_2:
    ableitung = sp.diff(formula, speicher[f"var_{i}"])
    speicher_2[f"d_{i}"] = ableitung



#Speicher für wonach abgeleitet wurde und dann das Delta_variable erstellt
speicher_delta = {}
for i in anzahl_variablen_2:
    speicher_delta[f"delta_{i}"] = "Delta" + speicher[f"var_{i}"]




equation = str()
for i in anzahl_variablen_2:
    if i == 0:
        equation = "(" +  str(speicher_2["d_0"]) + "*" + speicher_delta["delta_0"] + ")**2"
    else:
        new_string = " + (" + str(speicher_2[f"d_{i}"]) + "*" + speicher_delta[f"delta_{i}"] + ")**2" 
        equation += new_string

getexte_eq = py2tex(equation,print_formula=False, print_latex=False)

#Ausgabe
print(getexte_eq, "&",equation)
