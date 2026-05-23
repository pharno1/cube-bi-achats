-- =========================
-- DIMENSION FOURNISSEUR
-- =========================
CREATE TABLE IF NOT EXISTS dim_fournisseur (
    supplier_id SERIAL PRIMARY KEY,
    supplier_name TEXT UNIQUE
);

-- =========================
-- DIMENSION MAGASIN
-- =========================
CREATE TABLE IF NOT EXISTS dim_magasin (
    store_id SERIAL PRIMARY KEY,
    store_code TEXT UNIQUE,
    store_name TEXT,
    network TEXT
);

-- =========================
-- DIMENSION PRODUIT
-- =========================
CREATE TABLE IF NOT EXISTS dim_produit (
    product_id SERIAL PRIMARY KEY,
    category TEXT,
    product_group TEXT,
    article_description TEXT,
    color TEXT,
    origin TEXT
);

-- =========================
-- DIMENSION DATE
-- =========================
CREATE TABLE IF NOT EXISTS dim_date (
    date_id SERIAL PRIMARY KEY,
    purchase_date DATE UNIQUE,
    year INT,
    month INT,
    week INT
);

-- =========================
-- TABLE DE FAITS ACHATS
-- =========================
CREATE TABLE IF NOT EXISTS fact_achats (
    purchase_id SERIAL PRIMARY KEY,
    supplier_id INT REFERENCES dim_fournisseur(supplier_id),
    store_id INT REFERENCES dim_magasin(store_id),
    product_id INT REFERENCES dim_produit(product_id),
    date_id INT REFERENCES dim_date(date_id),

    invoice_id TEXT,
    quantity NUMERIC,
    buy_price NUMERIC,
    selling_price NUMERIC,
    coefficient NUMERIC,
    margin NUMERIC,
    purchase_value NUMERIC,
    invoice_product_value NUMERIC,
    total_purchase_amount NUMERIC,
    total_selling_amount NUMERIC,
    estimated_margin_amount NUMERIC
);