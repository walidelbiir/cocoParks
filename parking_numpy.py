import json
import numpy as np

with open('st_park_p.json', 'r') as file:
    data = json.load(file)


# On peut faire un loop pour etraire les donnees nester pour mieux les traiter mais dans notre cas nos donnees ne sont pas nestés 
# On extrait que les fields importants 
filtered_data = [
    (item.get('np_total'), item.get('libres'))
    for item in data
    if isinstance(item, dict) and item.get('etat') == 'LIBRE' and item.get('np_total',201) < 200 
    # on utilise 201 comme valeur de defaut si on ne trouve pas une valeur de np_total pour que la condition echoue et on skip l'entrée
]

# Si on trouve de données qui correcpond a nos conditions on les transforme en numpy arrays et on fait notre calcules
if filtered_data:
    np_totals, libres = np.array(filtered_data, dtype=float).T  # Ceci pour séparer les colonnes
    ratios = libres / np_totals
    average_ratio = np.mean(ratios)

    print(f"Pourcentage Moyenne d'emplacements libres': {average_ratio:.10f}")
    print(f"Nombre de parkings utilisés dans ce calcul: {len(np_totals)}")
else:
    print("Aucun parking satisfaisant les critères")
