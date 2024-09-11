import numpy as np
import sympy as sp
import sys
import json

# Daten von stdin lesen
data = json.loads(sys.stdin.read())

# Formeln extrahieren
original_formula = str(data['formulas']['Original'])
error_formula = str(data['formulas']['errorFormula'])

#print(f"Originalformel: {original_formula}")
#print(f"Fehlerformel: {error_formula}")

# Variablenwerte und Fehler dynamisch verarbeiten
for variable, values in data['werte'].items():
    globals()[variable] = float(values['value'])  # Dynamisch Variable erstellen
    delta_var_name = f"Delta{variable}"
    globals()[delta_var_name] = float(values['error'])  # Fehlerwert dynamisch zuweisen
    #print(f"{variable} = {globals()[variable]}, {delta_var_name} = {globals()[delta_var_name]}")

# Weitere Berechnungen können hier stattfinden
ergebniss1 = eval(original_formula)
ergebniss2 = eval(error_formula)
ergebniss3 = np.float64(ergebniss2)
ergebniss4 = np.sqrt(ergebniss3)

result = {
    'formelwert': ergebniss1,
    'errorwert': ergebniss4
}


# Beispiel: Rückgabe von irgendeinem Ergebnis
#result = {
#    "message": "Berechnung erfolgreich",
#    "Ergebniss": ergebniss1
#}

# Schicke das Ergebnis zurück an stdout
print(json.dumps(result))
