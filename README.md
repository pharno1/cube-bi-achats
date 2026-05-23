# 🌸 Projet 2 — Automatisation API → Cube BI Achats

## 🎯 Objectif

Automatiser l’intégration des données achats depuis un fichier Excel vers un modèle décisionnel type Cube BI, afin d’améliorer la fiabilité des analyses achats et réduire les traitements manuels.

## 🧠 Contexte

Ce projet simule un flux BI réel : les données achats sont d’abord stockées dans un fichier source, nettoyées avec Python, exposées via une API REST, puis chargées dans Supabase/PostgreSQL avant d’être restituées dans un dashboard Streamlit.

## 🏗️ Architecture

```text
BI Achats.xlsx
      ↓
Python / pandas
Nettoyage & normalisation
      ↓
achats_clean.csv
      ↓
API REST FastAPI
      ↓
Supabase / PostgreSQL
Modèle en étoile
      ↓
Dashboard Streamlit
Cube BI Achats