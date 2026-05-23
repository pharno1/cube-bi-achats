from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path

app = FastAPI(
    title="API Achats BI",
    description="API REST pour exposer les données achats nettoyées vers un Cube BI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_PATH = Path("data/achats_clean.csv")


def load_data():
    data = pd.read_csv(DATA_PATH)
    data["purchase_date"] = pd.to_datetime(data["purchase_date"], errors="coerce")
    return data


@app.get("/")
def home():
    return {
        "message": "API Achats BI opérationnelle",
        "endpoints": [
            "/achats",
            "/fournisseurs",
            "/magasins",
            "/kpi",
            "/achats/filtres"
        ]
    }


@app.get("/achats")
def get_achats(limit: int = Query(20, ge=1, le=500)):
    data = load_data()
    return data.head(limit).to_dict(orient="records")


@app.get("/fournisseurs")
def get_fournisseurs():
    data = load_data()
    fournisseurs = sorted(data["supplier"].dropna().unique().tolist())
    return {"fournisseurs": fournisseurs}


@app.get("/magasins")
def get_magasins():
    data = load_data()
    magasins = data[["store_code", "store_name", "network"]].drop_duplicates()
    return magasins.to_dict(orient="records")


@app.get("/kpi")
def get_kpi():
    data = load_data()

    total_quantity = float(data["quantity"].sum())
    total_purchase_value = float(data["purchase_value"].sum())
    total_purchase_amount = float(data["total_purchase_amount"].sum())
    total_selling_amount = float(data["total_selling_amount"].sum())
    estimated_margin = float(data["estimated_margin_amount"].sum())

    return {
        "total_quantity": total_quantity,
        "total_purchase_value": total_purchase_value,
        "total_purchase_amount": total_purchase_amount,
        "total_selling_amount": total_selling_amount,
        "estimated_margin": estimated_margin,
        "rows": len(data)
    }


@app.get("/achats/filtres")
def get_achats_filtered(
    supplier: str | None = None,
    network: str | None = None,
    category: str | None = None,
    limit: int = Query(50, ge=1, le=1000)
):
    data = load_data()

    if supplier:
        data = data[data["supplier"].str.lower() == supplier.lower()]

    if network:
        data = data[data["network"].str.lower() == network.lower()]

    if category:
        data = data[data["category"].str.lower() == category.lower()]

    return data.head(limit).to_dict(orient="records")


@app.get("/analyse/fournisseurs")
def analyse_fournisseurs():
    data = load_data()

    result = data.groupby("supplier").agg(
        total_quantity=("quantity", "sum"),
        total_purchase_value=("purchase_value", "sum"),
        total_margin=("estimated_margin_amount", "sum"),
        nb_lignes=("supplier", "count")
    ).reset_index()

    result = result.sort_values("total_purchase_value", ascending=False)

    return result.to_dict(orient="records")


@app.get("/analyse/categories")
def analyse_categories():
    data = load_data()

    result = data.groupby("category").agg(
        total_quantity=("quantity", "sum"),
        total_purchase_value=("purchase_value", "sum"),
        total_margin=("estimated_margin_amount", "sum"),
        nb_lignes=("category", "count")
    ).reset_index()

    result = result.sort_values("total_purchase_value", ascending=False)

    return result.to_dict(orient="records")