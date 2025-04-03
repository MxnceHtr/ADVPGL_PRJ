#!/usr/bin/env python3
import pandas as pd
import datetime
import os

# Charger les données depuis data.csv
try:
    df = pd.read_csv("data.csv")
except Exception as e:
    print("Erreur lors de la lecture de data.csv:", e)
    exit(1)

# Convertir les noms de colonnes en minuscules pour faciliter le traitement
df.columns = [col.strip().lower() for col in df.columns]

# Identifier la colonne temporelle (elle peut être "timestamp" ou "time")
if 'timestamp' in df.columns:
    time_column = 'timestamp'
elif 'time' in df.columns:
    time_column = 'time'
else:
    print("Aucune colonne de date trouvée dans data.csv")
    exit(1)

# Conversion de la colonne temporelle en datetime
df[time_column] = pd.to_datetime(df[time_column])

# Déterminer la date du jour
today = datetime.date.today()

# Filtrer les données du jour
df_today = df[df[time_column].dt.date == today]

if df_today.empty:
    print("Aucune donnée pour aujourd'hui.")
    exit(0)

# Trier les données par date
df_today = df_today.sort_values(time_column)

# Calcul des indicateurs du jour
open_price = df_today.iloc[0]['price']
close_price = df_today.iloc[-1]['price']
high_price = df_today['high'].max() if 'high' in df_today.columns else df_today['price'].max()
low_price = df_today['low'].min() if 'low' in df_today.columns else df_today['price'].min()
volatility = high_price - low_price
evolution = (close_price - open_price) / open_price * 100

# Préparer le rapport quotidien sous forme de dictionnaire
report = {
    "date": today.strftime("%Y-%m-%d"),
    "open": open_price,
    "close": close_price,
    "high": high_price,
    "low": low_price,
    "volatility": volatility,
    "evolution_%": evolution
}

# Chemin vers le fichier daily_report.csv
report_file = "daily_report.csv"

# Charger le fichier existant s'il existe, sinon créer un DataFrame vide
if os.path.exists(report_file):
    try:
        df_report = pd.read_csv(report_file)
    except Exception as e:
        print("Erreur lors de la lecture de daily_report.csv:", e)
        df_report = pd.DataFrame()
else:
    df_report = pd.DataFrame()

# Supprimer une éventuelle entrée déjà existante pour aujourd'hui
if not df_report.empty and 'date' in df_report.columns:
    df_report = df_report[df_report['date'] != report["date"]]

# Ajouter le nouveau rapport en utilisant pd.concat au lieu de append()
df_report = pd.concat([df_report, pd.DataFrame([report])], ignore_index=True)

# Sauvegarder le rapport dans daily_report.csv
df_report.to_csv(report_file, index=False)

print("Daily report généré pour", today)
