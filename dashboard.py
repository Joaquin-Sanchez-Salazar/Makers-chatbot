import os
import pandas as pd
import matplotlib.pyplot as plt
import json

# 1) Base dir del script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 2) Carga de métricas
metrics_path = os.path.join(BASE_DIR, "metrics.csv")
df_metrics = pd.read_csv(metrics_path)

print("\nChatbot Test Metrics:\n")
print(df_metrics.to_string(index=False))

# 3) Accuracy by Intent
plt.figure(figsize=(10, 6))
plt.bar(df_metrics["intent"], df_metrics["accuracy"])
plt.title("Chatbot Accuracy by Intent")
plt.ylabel("Accuracy (%)")
plt.ylim(0, 110)
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "accuracy_by_intent.png"))
plt.show()

# 4) Carga del inventario (data.json)
data_path = os.path.join(BASE_DIR, "data.json")
with open(data_path, "r", encoding="utf-8") as f:
    data = json.load(f)
df_data = pd.DataFrame(data)

# Comprueba columnas disponibles
print("\nColumns in data.json:", df_data.columns.tolist())

# 5) Stock by Brand
brand_stock = df_data.groupby("brand")["stock"].sum().reset_index()
plt.figure(figsize=(8, 6))
plt.bar(brand_stock["brand"], brand_stock["stock"])
plt.title("Stock by Brand")
plt.ylabel("Total Stock")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "stock_by_brand.png"))
plt.show()

# 6) Stock by Processor Type
proc_stock = df_data.groupby("processor")["stock"].sum().reset_index()
plt.figure(figsize=(8, 6))
plt.bar(proc_stock["processor"], proc_stock["stock"])
plt.title("Stock by Processor Type")
plt.ylabel("Total Stock")
plt.xticks(rotation=45, ha="right")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "stock_by_processor.png"))
plt.show()

# 7) RAM Distribution
ram_stock = df_data.groupby("ram")["stock"].sum().reset_index()

plt.figure(figsize=(8, 6))
plt.bar(ram_stock["ram"], ram_stock["stock"])
plt.title("RAM Distribution of Stock")
plt.xlabel("RAM")
plt.ylabel("Total Stock")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()
plt.savefig(os.path.join(BASE_DIR, "ram_distribution_bar.png"))
plt.show()
