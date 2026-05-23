import pandas as pd

file_path = "data/bi_achats.xlsx"

# La vraie ligne d'en-tête est la première ligne du fichier
data = pd.read_excel(file_path, header=1)

print("\n===== DIMENSIONS =====")
print(data.shape)

print("\n===== COLONNES =====")
print(list(data.columns))

print("\n===== APERÇU DES DONNÉES =====")
print(data.head())

print("\n===== INFOS TYPES =====")
print(data.dtypes)

print("\n===== VALEURS MANQUANTES TOP 15 =====")
print(data.isna().sum().sort_values(ascending=False).head(15))