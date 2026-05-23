import os
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client


# =========================
# CONFIG PAGE
# =========================

st.set_page_config(
    page_title="Cube BI Achats",
    page_icon="🌸",
    layout="wide"
)


# =========================
# STYLE
# =========================

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #111827;
}
.subtitle {
    font-size: 18px;
    color: #6b7280;
    margin-bottom: 20px;
}
.kpi-card {
    background: #ffffff;
    padding: 18px;
    border-radius: 16px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    border: 1px solid #e5e7eb;
}
.section-title {
    font-size: 24px;
    font-weight: 700;
    color: #111827;
    margin-top: 24px;
}
</style>
""", unsafe_allow_html=True)


# =========================
# CONNEXION SUPABASE
# =========================

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Clés Supabase manquantes dans le fichier .env")
    st.stop()

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# =========================
# CHARGEMENT DES DONNÉES
# =========================

@st.cache_data(ttl=300)
def load_table(table_name):
    response = supabase.table(table_name).select("*").execute()
    return pd.DataFrame(response.data)


fact = load_table("fact_achats")
dim_fournisseur = load_table("dim_fournisseur")
dim_magasin = load_table("dim_magasin")
dim_produit = load_table("dim_produit")
dim_date = load_table("dim_date")

data = (
    fact
    .merge(dim_fournisseur, on="supplier_id", how="left")
    .merge(dim_magasin, on="store_id", how="left")
    .merge(dim_produit, on="product_id", how="left")
    .merge(dim_date, on="date_id", how="left")
)

data["purchase_date"] = pd.to_datetime(data["purchase_date"], errors="coerce")

numeric_cols = [
    "quantity",
    "buy_price",
    "selling_price",
    "purchase_value",
    "invoice_product_value",
    "total_purchase_amount",
    "total_selling_amount",
    "estimated_margin_amount"
]

for col in numeric_cols:
    data[col] = pd.to_numeric(data[col], errors="coerce").fillna(0)


# =========================
# SIDEBAR FILTRES
# =========================

st.sidebar.title("🔎 Filtres")

suppliers = sorted(data["supplier_name"].dropna().unique())
networks = sorted(data["network"].dropna().unique())
categories = sorted(data["category"].dropna().unique())
stores = sorted(data["store_name"].dropna().unique())

selected_suppliers = st.sidebar.multiselect(
    "Fournisseur",
    suppliers,
    default=suppliers
)

selected_networks = st.sidebar.multiselect(
    "Réseau",
    networks,
    default=networks
)

selected_categories = st.sidebar.multiselect(
    "Catégorie produit",
    categories,
    default=categories
)

selected_stores = st.sidebar.multiselect(
    "Magasin",
    stores,
    default=stores
)

min_date = data["purchase_date"].min().date()
max_date = data["purchase_date"].max().date()

date_range = st.sidebar.date_input(
    "Période",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

filtered = data[
    (data["supplier_name"].isin(selected_suppliers)) &
    (data["network"].isin(selected_networks)) &
    (data["category"].isin(selected_categories)) &
    (data["store_name"].isin(selected_stores)) &
    (data["purchase_date"].dt.date >= start_date) &
    (data["purchase_date"].dt.date <= end_date)
]

if filtered.empty:
    st.warning("Aucune donnée disponible avec les filtres sélectionnés.")
    st.stop()


# =========================
# HEADER
# =========================

st.markdown('<div class="main-title">🌸 Cube BI Achats — Pilotage des achats fleurs</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Dashboard connecté à Supabase pour analyser les achats, fournisseurs, magasins, marges et qualité data.</div>',
    unsafe_allow_html=True
)


# =========================
# KPI
# =========================

total_purchase = filtered["purchase_value"].sum()
total_quantity = filtered["quantity"].sum()
total_margin = filtered["estimated_margin_amount"].sum()
nb_suppliers = filtered["supplier_name"].nunique()
nb_stores = filtered["store_name"].nunique()
avg_buy_price = filtered["buy_price"].mean()

k1, k2, k3, k4, k5, k6 = st.columns(6)

k1.metric("Montant achats", f"{total_purchase:,.0f} €".replace(",", " "))
k2.metric("Quantité", f"{total_quantity:,.0f}".replace(",", " "))
k3.metric("Marge estimée", f"{total_margin:,.0f} €".replace(",", " "))
k4.metric("Fournisseurs", nb_suppliers)
k5.metric("Magasins", nb_stores)
k6.metric("Prix achat moyen", f"{avg_buy_price:,.2f} €".replace(",", " "))

st.divider()


# =========================
# TABS
# =========================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Vue globale",
    "🚚 Fournisseurs",
    "🏬 Magasins",
    "🌿 Produits",
    "✅ Qualité data"
])


# =========================
# TAB 1 — VUE GLOBALE
# =========================

with tab1:
    st.markdown('<div class="section-title">Évolution temporelle des achats</div>', unsafe_allow_html=True)

    evolution = (
        filtered.groupby("purchase_date")
        .agg(
            montant_achats=("purchase_value", "sum"),
            marge_estimee=("estimated_margin_amount", "sum"),
            quantite=("quantity", "sum")
        )
        .reset_index()
        .sort_values("purchase_date")
    )

    st.line_chart(evolution, x="purchase_date", y=["montant_achats", "marge_estimee"])

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Répartition par réseau")
        network_perf = (
            filtered.groupby("network")["purchase_value"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        st.bar_chart(network_perf, x="network", y="purchase_value")

    with col2:
        st.subheader("Achats par catégorie")
        cat_perf = (
            filtered.groupby("category")["purchase_value"]
            .sum()
            .sort_values(ascending=False)
            .reset_index()
        )
        st.bar_chart(cat_perf, x="category", y="purchase_value")


# =========================
# TAB 2 — FOURNISSEURS
# =========================

with tab2:
    st.markdown('<div class="section-title">Analyse fournisseurs</div>', unsafe_allow_html=True)

    suppliers_perf = (
        filtered.groupby("supplier_name")
        .agg(
            montant_achats=("purchase_value", "sum"),
            quantite=("quantity", "sum"),
            marge_estimee=("estimated_margin_amount", "sum"),
            prix_achat_moyen=("buy_price", "mean"),
            nb_lignes=("supplier_name", "count")
        )
        .reset_index()
        .sort_values("montant_achats", ascending=False)
    )

    st.dataframe(suppliers_perf, use_container_width=True)

    st.subheader("Top fournisseurs par montant d’achats")
    st.bar_chart(suppliers_perf.head(10), x="supplier_name", y="montant_achats")


# =========================
# TAB 3 — MAGASINS
# =========================

with tab3:
    st.markdown('<div class="section-title">Analyse magasins</div>', unsafe_allow_html=True)

    stores_perf = (
        filtered.groupby(["store_code", "store_name", "network"])
        .agg(
            montant_achats=("purchase_value", "sum"),
            quantite=("quantity", "sum"),
            marge_estimee=("estimated_margin_amount", "sum"),
            nb_lignes=("store_name", "count")
        )
        .reset_index()
        .sort_values("montant_achats", ascending=False)
    )

    st.dataframe(stores_perf, use_container_width=True)

    st.subheader("Top magasins par montant d’achats")
    st.bar_chart(stores_perf.head(10), x="store_name", y="montant_achats")


# =========================
# TAB 4 — PRODUITS
# =========================

with tab4:
    st.markdown('<div class="section-title">Analyse produits & familles</div>', unsafe_allow_html=True)

    product_perf = (
        filtered.groupby(["category", "product_group", "article_description"])
        .agg(
            montant_achats=("purchase_value", "sum"),
            quantite=("quantity", "sum"),
            marge_estimee=("estimated_margin_amount", "sum"),
            prix_achat_moyen=("buy_price", "mean")
        )
        .reset_index()
        .sort_values("montant_achats", ascending=False)
    )

    st.dataframe(product_perf, use_container_width=True)

    st.subheader("Top familles produits")
    group_perf = (
        filtered.groupby("product_group")["purchase_value"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    st.bar_chart(group_perf, x="product_group", y="purchase_value")


# =========================
# TAB 5 — QUALITÉ DATA
# =========================

with tab5:
    st.markdown('<div class="section-title">Contrôle qualité des données</div>', unsafe_allow_html=True)

    q1, q2, q3, q4 = st.columns(4)

    q1.metric("Lignes analysées", len(filtered))
    q2.metric("Valeurs manquantes", int(filtered.isna().sum().sum()))
    q3.metric("Doublons", int(filtered.duplicated().sum()))
    q4.metric("Colonnes", filtered.shape[1])

    missing = filtered.isna().sum().reset_index()
    missing.columns = ["colonne", "valeurs_manquantes"]
    missing = missing.sort_values("valeurs_manquantes", ascending=False)

    st.subheader("Valeurs manquantes par colonne")
    st.dataframe(missing, use_container_width=True)

    st.subheader("Aperçu des données consolidées")
    st.dataframe(filtered.head(100), use_container_width=True)


# =========================
# CONCLUSION
# =========================

st.divider()

st.markdown("""
### Lecture métier

Ce dashboard simule un **Cube BI Achats** alimenté par un pipeline ETL semi-automatique.  
Les données sont extraites d’un fichier achats, nettoyées avec Python, exposées via API, chargées dans Supabase,
puis restituées dans Streamlit pour le pilotage décisionnel.

Le projet permet d’analyser :
- les montants d’achats,
- les fournisseurs clés,
- les magasins concernés,
- les catégories produits,
- les marges estimées,
- et la qualité des données.
""")