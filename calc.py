import numpy as np
import sympy as sp
import sys
import json

# Daten von stdin lesen
data = json.loads(sys.stdin.read())

# Formeln extrahieren
original_formula = str(data['formulas']['Original'])
original_formula_neu = original_formula.replace("sin(", "np.sin(").replace("cos(", "np.cos(").replace("exp(","np.exp(").replace("tan(","np.tan(").replace("pi","np.pi")
error_formula = str(data['formulas']['errorFormula'])


# Variablenwerte und Fehler verarbeiten
for variable, values in data['werte'].items():
    globals()[variable] = float(values['value'])  
    delta_var_name = f"Delta{variable}"
    globals()[delta_var_name] = float(values['error'])  # Fehlerwert dynamisch zuweisen


ergebniss1 = eval(original_formula_neu)
ergebniss2 = eval(error_formula)
ergebniss3 = np.float64(ergebniss2)
ergebniss4 = np.sqrt(ergebniss3)

result = {
    'formelwert': ergebniss1,
    'errorwert': ergebniss4
}

#WoooWW WAASSS du liest dir actualy meinen Code durch?
# Du musst kaputt sein. Aber naja du hast nun ein weiteres Captain Easteregg gefunden. Schreibe mir dein Lieblingsbuchgenre an (easteregg@joni.info) oder auf der Kommunikationsplattform deiner Wahl

# Ausgabe an stdout
print(json.dumps(result))
