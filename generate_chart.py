import matplotlib.pyplot as plt
import json
import os
from datetime import date

# Fichier qui stocke l'historique des résultats
HISTORY_FILE = "results_history.json"

# Charge l'historique existant ou crée un nouveau
if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "r") as f:
        results = json.load(f)
else:
    # Données de démo pour commencer
    results = [
        {"date": "2026-04-01", "ok": 3, "ko": 0},
        {"date": "2026-04-02", "ok": 2, "ko": 1},
    ]

# Ajoute le résultat d'aujourd'hui (à personnaliser selon les vrais résultats)
today = str(date.today())
if not any(r["date"] == today for r in results):
    results.append({"date": today, "ok": 3, "ko": 0})

# Sauvegarde l'historique mis à jour
with open(HISTORY_FILE, "w") as f:
    json.dump(results, f, indent=2)

# Génère le graphique
dates = [r["date"] for r in results]
ok   = [r["ok"]   for r in results]
ko   = [r["ko"]   for r in results]

plt.figure(figsize=(10, 5))
plt.plot(dates, ok, label="Tests OK ✅", marker="o", color="green", linewidth=2)
plt.plot(dates, ko, label="Tests KO ❌", marker="x", color="red",   linewidth=2)
plt.xlabel("Date")
plt.ylabel("Nombre de tests")
plt.title("Évolution des résultats des tests Selenium - Reddit")
plt.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("test_results.png")
print("✅ Graphique généré : test_results.png")