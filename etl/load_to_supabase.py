import os
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client

# =========================
# CONFIGURATION
# =========================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL ou SUPABASE_KEY manquant dans le fichier .env")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

DATA_PATH = "data/achats_clean.csv"


# =========================
# HELPERS
# =========================

def clean_text(value):
    if pd.isna(value) or value in ["nan", "None", ""]:
        return "Non renseigné"
    return str(value).strip()


def clean_number(value):
    if pd.isna(value):
        return 0
    return float(value)


def get_or_create_supplier(supplier_name):
    supplier_name = clean_text(supplier_name)

    res = supabase.table("dim_fournisseur") \
        .select("supplier_id") \
        .eq("supplier_name", supplier_name) \
        .execute()

    if res.data:
        return res.data[0]["supplier_id"]

    insert = supabase.table("dim_fournisseur") \
        .insert({"supplier_name": supplier_name}) \
        .execute()

    return insert.data[0]["supplier_id"]


def get_or_create_store(store_code, store_name, network):
    store_code = clean_text(store_code)
    store_name = clean_text(store_name)
    network = clean_text(network)

    res = supabase.table("dim_magasin") \
        .select("store_id") \
        .eq("store_code", store_code) \
        .execute()

    if res.data:
        return res.data[0]["store_id"]

    insert = supabase.table("dim_magasin") \
        .insert({
            "store_code": store_code,
            "store_name": store_name,
            "network": network
        }) \
        .execute()

    return insert.data[0]["store_id"]


def get_or_create_product(category, product_group, article_description, color, origin):
    category = clean_text(category)
    product_group = clean_text(product_group)
    article_description = clean_text(article_description)
    color = clean_text(color)
    origin = clean_text(origin)

    res = supabase.table("dim_produit") \
        .select("product_id") \
        .eq("category", category) \
        .eq("product_group", product_group) \
        .eq("article_description", article_description) \
        .eq("color", color) \
        .eq("origin", origin) \
        .execute()

    if res.data:
        return res.data[0]["product_id"]

    insert = supabase.table("dim_produit") \
        .insert({
            "category": category,
            "product_group": product_group,
            "article_description": article_description,
            "color": color,
            "origin": origin
        }) \
        .execute()

    return insert.data[0]["product_id"]


def get_or_create_date(purchase_date, year, month, week):
    purchase_date = pd.to_datetime(purchase_date).date().isoformat()

    res = supabase.table("dim_date") \
        .select("date_id") \
        .eq("purchase_date", purchase_date) \
        .execute()

    if res.data:
        return res.data[0]["date_id"]

    insert = supabase.table("dim_date") \
        .insert({
            "purchase_date": purchase_date,
            "year": int(year),
            "month": int(month),
            "week": int(week)
        }) \
        .execute()

    return insert.data[0]["date_id"]


# =========================
# LOAD DATA
# =========================

data = pd.read_csv(DATA_PATH)

print("===== CHARGEMENT DU FICHIER CLEAN =====")
print("Dimensions :", data.shape)

inserted_rows = 0

for _, row in data.iterrows():

    supplier_id = get_or_create_supplier(row["supplier"])
    store_id = get_or_create_store(
        row["store_code"],
        row["store_name"],
        row["network"]
    )
    product_id = get_or_create_product(
        row["category"],
        row["product_group"],
        row["article_description"],
        row["color"],
        row["origin"]
    )
    date_id = get_or_create_date(
        row["purchase_date"],
        row["year"],
        row["month"],
        row["week"]
    )

    fact_row = {
        "supplier_id": supplier_id,
        "store_id": store_id,
        "product_id": product_id,
        "date_id": date_id,

        "invoice_id": clean_text(row["invoice_id"]),
        "quantity": clean_number(row["quantity"]),
        "buy_price": clean_number(row["buy_price"]),
        "selling_price": clean_number(row["selling_price"]),
        "coefficient": clean_number(row["coefficient"]),
        "margin": clean_number(row["margin"]),
        "purchase_value": clean_number(row["purchase_value"]),
        "invoice_product_value": clean_number(row["invoice_product_value"]),
        "total_purchase_amount": clean_number(row["total_purchase_amount"]),
        "total_selling_amount": clean_number(row["total_selling_amount"]),
        "estimated_margin_amount": clean_number(row["estimated_margin_amount"])
    }

    supabase.table("fact_achats").insert(fact_row).execute()
    inserted_rows += 1

print("===== CHARGEMENT TERMINÉ =====")
print(f"Lignes insérées dans fact_achats : {inserted_rows}")