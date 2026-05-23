import pandas as pd
from pathlib import Path

SOURCE_FILE = "data/bi_achats_augmente.xlsx"
OUTPUT_FILE = "data/achats_clean.csv"

# Lecture du fichier avec la bonne ligne d'en-tête
data = pd.read_excel(SOURCE_FILE)

# Sélection des colonnes utiles pour le projet API / Cube BI
cols_to_keep = [
    "Supplier",
    "Year",
    "Month",
    "Week",
    "Day",
    "Invoice",
    "Emova Code",
    "Shop",
    "Network",
    "Category",
    "Group Product",
    "Article Description",
    "Grower",
    "FluxAchats",
    "Origin",
    "Color",
    "BuyPrice",
    "Selling Price",
    "Coefficient",
    "Marge",
    "Quantity",
    "lInvTotalProductValue",
    "PurchaseValue",
    "InvoiceKind_"
]

data = data[cols_to_keep].copy()

# Renommage propre des colonnes
data = data.rename(columns={
    "Supplier": "supplier",
    "Year": "year",
    "Month": "month",
    "Week": "week",
    "Day": "purchase_date",
    "Invoice": "invoice_id",
    "Emova Code": "store_code",
    "Shop": "store_name",
    "Network": "network",
    "Category": "category",
    "Group Product": "product_group",
    "Article Description": "article_description",
    "Grower": "grower",
    "FluxAchats": "purchase_flow",
    "Origin": "origin",
    "Color": "color",
    "BuyPrice": "buy_price",
    "Selling Price": "selling_price",
    "Coefficient": "coefficient",
    "Marge": "margin",
    "Quantity": "quantity",
    "lInvTotalProductValue": "invoice_product_value",
    "PurchaseValue": "purchase_value",
    "InvoiceKind_": "invoice_kind"
})

# Nettoyage des types
data["purchase_date"] = pd.to_datetime(data["purchase_date"], errors="coerce")

numeric_cols = [
    "year",
    "month",
    "week",
    "invoice_id",
    "buy_price",
    "selling_price",
    "coefficient",
    "margin",
    "quantity",
    "invoice_product_value",
    "purchase_value"
]

for col in numeric_cols:
    data[col] = pd.to_numeric(data[col], errors="coerce")

text_cols = [
    "supplier",
    "store_code",
    "store_name",
    "network",
    "category",
    "product_group",
    "article_description",
    "grower",
    "purchase_flow",
    "origin",
    "color",
    "invoice_kind"
]

for col in text_cols:
    data[col] = data[col].astype(str).str.strip()

# Suppression des lignes sans date ou sans fournisseur
data = data.dropna(subset=["purchase_date", "supplier"])

# Suppression des doublons
data = data.drop_duplicates()

# Création de KPI utiles
data["total_purchase_amount"] = data["quantity"] * data["buy_price"]
data["total_selling_amount"] = data["quantity"] * data["selling_price"]
data["estimated_margin_amount"] = data["total_selling_amount"] - data["total_purchase_amount"]

# Contrôle qualité simple
quality_report = {
    "rows": len(data),
    "columns": len(data.columns),
    "missing_values_total": int(data.isna().sum().sum()),
    "duplicates": int(data.duplicated().sum()),
    "total_quantity": float(data["quantity"].sum()),
    "total_purchase_value": float(data["purchase_value"].sum())
}

# Export clean
Path("data").mkdir(exist_ok=True)
data.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

print("===== FICHIER NETTOYÉ CRÉÉ =====")
print(OUTPUT_FILE)

print("\n===== DIMENSIONS =====")
print(data.shape)

print("\n===== COLONNES FINALES =====")
print(list(data.columns))

print("\n===== APERÇU =====")
print(data.head())

print("\n===== RAPPORT QUALITÉ =====")
for key, value in quality_report.items():
    print(f"{key}: {value}")