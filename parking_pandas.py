import json
import pandas as pd
from pandas import json_normalize

with open('./st_park_p.json', 'r') as file:
    data = json.load(file)


df = json_normalize(data)  # Pandas a une methode pour traiter les datasets avec des valeurs nestés. Ceci n'est pas obligatoire pour note dataset.


# On filtre les données selon nos critères
filtered_df = df[(df['etat'] == 'LIBRE') & (df['np_total'] < 200)]

# On calcule le Ratio pour chaque entrée
filtered_df['ratio'] = filtered_df['libres'] / filtered_df['np_total']

# Si'il existe des données satisfaisant nos critères nous calculons la moyenne
if not filtered_df.empty:
    average_ratio = filtered_df['ratio'].mean()
    print(f"Pourcentage Moyenne d'emplacements libres': {average_ratio:.10f}")
    print(f"Nombre de parkings utilisés dans ce calcul: {len(filtered_df)}")
else:
    print("Aucun parking satisfaisant les critères")