import pandas as pd
import numpy as np
from pathlib import Path
from random import choice, randint, uniform

OUTPUT_FILE = "data/bi_achats_augmente.xlsx"

np.random.seed(42)

suppliers = ["VDV", "Flora Holland", "Rose Africa", "Tulip Export", "Orchidées France"]
networks = ["Franchise", "Succursale"]
shops = [
    ("CF0018", "MONCEAU FLEURS PARIS 15"),
    ("CF0021", "MONCEAU FLEURS LYON"),
    ("CF0032", "MONCEAU FLEURS MARSEILLE"),
    ("ANR012", "AU NOM DE LA ROSE BOULOGNE"),
    ("ANR155", "AU NOM DE LA ROSE PUTEAUX"),
    ("HF001", "HAPPY PARIS OPERA"),
]
categories = ["Fleurs coupées", "Plantes", "Bouquets", "Accessoires"]
product_groups = ["Roses", "Tulipes", "Orchidées", "Lys", "Plantes vertes", "Bouquets mixtes"]
origins = ["Pays-Bas", "France", "Kenya", "Espagne", "Italie"]
colors = ["Rouge", "Blanc", "Rose", "Jaune", "Mixte", "Vert"]
purchase_flows = ["Stock", "Commande spéciale", "Réassort", "Promotion"]
invoice_kinds = ["Factuur", "Creditnota"]

rows = []

for i in range(500):
    date = pd.Timestamp("2024-01-01") + pd.Timedelta(days=randint(0, 365))
    store_code, shop = choice(shops)
    quantity = randint(5, 250)
    buy_price = round(uniform(0.8, 8.5), 2)
    selling_price = round(buy_price * uniform(1.3, 2.5), 2)
    purchase_value = round(quantity * buy_price, 2)
    invoice_value = round(quantity * selling_price, 2)
    margin = round(invoice_value - purchase_value, 2)
    coefficient = round(selling_price / buy_price, 2)

    rows.append({
        "Supplier": choice(suppliers),
        "Year": date.year,
        "Month": date.month,
        "Week": int(date.isocalendar().week),
        "Day": date,
        "Invoice": randint(600000, 699999),
        "concaXB": randint(60000000000000, 69999999999999),
        "EMP code": store_code.replace("CF", "4CC"),
        "Emova Code": store_code,
        "Shop": shop,
        "Network": choice(networks),
        "Customer": "EMOVA",
        "SO": randint(30000000, 39999999),
        "Order type": np.nan,
        "Order Type": np.nan,
        "Category": choice(categories),
        "ID Group": randint(100, 999),
        "Group Product": choice(product_groups),
        "Broncode": randint(10000, 99999),
        "Shortcode": f"ART{randint(1000, 9999)}",
        "Article Description": choice(product_groups) + " premium",
        "Supplier.1": choice(suppliers),
        "Supplier.2": choice(suppliers),
        "Grower": choice(["Grower A", "Grower B", "Grower C", "Grower D"]),
        "Grower.1": choice(["Grower A", "Grower B", "Grower C", "Grower D"]),
        "Standing order": choice(["Oui", "Non"]),
        "FluxAchats": choice(purchase_flows),
        "Origin": choice(origins),
        "Certification": np.nan,
        "Color": choice(colors),
        "Length": randint(30, 90),
        "PotSize": np.nan,
        "Cr1": np.nan,
        "Cr2": np.nan,
        "Cr3": np.nan,
        "Net Weight": np.nan,
        "IncomingBox": randint(1, 20),
        "Incoming Packing": randint(1, 10),
        "Outgoing Box": np.nan,
        "Outgoing Packing": np.nan,
        "Minimum Order": randint(1, 20),
        "BuyPrice": buy_price,
        "Selling Price": selling_price,
        "Coefficient": coefficient,
        "Marge": margin,
        "Quantity": quantity,
        "lotId": randint(30000000, 39999999),
        "InvoiceKind_": choice(invoice_kinds),
        "lInvTotalProductValue": invoice_value,
        "PurchaseValue": purchase_value,
        "sOrderLine": randint(30000000, 39999999),
        "Reserve": np.nan,
        "Price": np.nan,
        "Diff": np.nan
    })

data = pd.DataFrame(rows)

# On ajoute une première ligne vide pour respecter ton format actuel lu avec header=1
header_row = pd.DataFrame([data.columns], columns=data.columns)
final_data = pd.concat([header_row, data], ignore_index=True)

Path("data").mkdir(exist_ok=True)
final_data.to_excel(OUTPUT_FILE, index=False, header=False)

print("Fichier généré :", OUTPUT_FILE)
print("Dimensions :", data.shape)
print(data.head())