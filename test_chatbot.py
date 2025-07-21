import requests
import re
import json
import csv

BASE_URL = "http://localhost:8000/chat"
TIMEOUT = 5

test_cases = [
    # — get total stock (10 tests)
    ("How many laptops are there?", "get total stock"),
    ("How big is your inventory?", "get total stock"),
    ("Total units available?", "get total stock"),
    ("¿Tienen muchas laptops en stock?", "get total stock"),
    ("How many do you currently have?", "get total stock"),
    ("What is your total stock count?", "get total stock"),
    ("¿Cuántas computadoras hay en total?", "get total stock"),
    ("Show total number of units", "get total stock"),
    ("Dime el stock total", "get total stock"),
    ("Count all available computers", "get total stock"),

    # — get stock by brand / list brands (15 tests)
    ("How many Apple computers are left?", "get stock by brand"),
    ("Stock for HP?", "get stock by brand"),
    ("Do you have Dell laptops?", "get stock by brand"),
    ("How many Pavilion models are in stock?", "get stock by brand"),
    ("HP availability?", "get stock by brand"),
    ("Remaining Apple laptops?", "get stock by brand"),
    ("Dell stock count", "get stock by brand"),
    ("¿Stock de Apple laptops?", "get stock by brand"),
    ("Quantity of HP notebooks?", "get stock by brand"),
    ("Which brands do you sell?", "list brands"),
    ("¿Qué marcas manejan?", "list brands"),
    ("Tienen computadoras de la marca Apple?", "list brands"),
    ("What brands do you currently stock?", "list brands"),
    ("Show me all brands", "list brands"),

    # — get computer specifications (12 tests)
    ("What are the specs of the Envy?", "get computer specifications"),
    ("Tell me about the HP Envy.", "get computer specifications"),
    ("Give me technical details for the MacBook.", "get computer specifications"),
    ("RAM and processor of Dell Inspiron 14?", "get computer specifications"),
    ("¿Qué especificaciones tiene la Dell?", "get computer specifications"),
    ("What does the Pavilion 15 offer?", "get computer specifications"),
    ("Can you describe the Apple laptop specs?", "get computer specifications"),
    ("Show specifications for HP Pavilion 15", "get computer specifications"),
    ("¿Detalles de hardware de MacBook Air?", "get computer specifications"),
    ("Tell me Dell Inspiron 14 specs", "get computer specifications"),
    ("¿Qué RAM y CPU tiene la Envy?", "get computer specifications"),
    ("Technical specs of Apple MacBook Air", "get computer specifications"),

    # — get price of a computer (11 tests)
    ("Price of the HP Envy?", "get price of a computer"),
    ("How much does the Mac cost?", "get price of a computer"),
    ("What's the cost of the Dell Inspiron?", "get price of a computer"),
    ("Cuánto cuesta la Pavilion 15?", "get price of a computer"),
    ("Envy price please.", "get price of a computer"),
    ("Tell me the cost for the Apple MacBook Air.", "get price of a computer"),
    ("How much is the HP Pavilion 15?", "get price of a computer"),
    ("¿Precio de la Dell Inspiron 14?", "get price of a computer"),
    ("Cost to buy MacBook Air?", "get price of a computer"),
    ("¿Cuál es el precio de Envy?", "get price of a computer"),
    ("Give me the price of HP Envy", "get price of a computer"),

    # — small talk (12 tests)
    ("I love HP laptops.", "small talk"),
    ("Apple is expensive.", "small talk"),
    ("Inspiron sounds cool.", "small talk"),
    ("Quiero una computadora buena.", "small talk"),
    ("Laptop Dell bonita.", "small talk"),
    ("Hi, can you help me?", "small talk"),
    ("What can you do?", "small talk"),
    ("Tell me a joke.", "small talk"),
    ("How are you?", "small talk"),
    ("Buenos días, ¿qué tal?", "small talk"),
    ("I need assistance.", "small talk"),
    ("¿Qué sabes hacer?", "small talk"),

    # — new tests (13 tests)
    ("What's your total computer inventory?", "get total stock"),
    ("Do you stock any Apple laptops?", "get stock by brand"),
    ("Show me your laptop count", "get total stock"),
    ("List all brands you carry", "list brands"),
    ("Tell me Pavilion stock", "get stock by brand"),
    ("Give me info on Apple laptops", "get stock by brand"),
    ("What's the spec of the MacBook Air?", "get computer specifications"),
    ("How much would an Envy cost?", "get price of a computer"),
    ("Overall laptop availability?", "get total stock"),
    ("Brands in stock right now?", "list brands"),
    ("Specs of HP Envy laptop?", "get computer specifications"),
    ("Remaining stock of Dell Inspiron?", "get stock by brand"),
    ("Price for MacBook Air please", "get price of a computer"),
]

def analyze_response(resp: str, expected: str) -> bool:
    txt = resp.lower().strip()

    if expected == "get total stock":
        return bool(re.match(
            r'^(we have|tenemos)\s+\d+\s+(computers?|computadoras?)(\s+(in stock|en stock))?\.?$',
            txt
        ))

    if expected == "list brands":
        return bool(re.match(r'^(we stock|disponemos de):', txt))

    if expected == "get stock by brand":
        eng = re.match(r'^we have\s+\d+\s+.+?\s+computers?\s+available\.?$', txt)
        esp = re.match(r'^tenemos\s+\d+\s+.+?\s+computadoras?\s+disponibles\.?$', txt)
        return bool(eng or esp)

    if expected == "get computer specifications":
        return "ram:" in txt and ("processor:" in txt or "procesador:" in txt)

    if expected == "get price of a computer":
        return txt.startswith("the price of") or txt.startswith("el precio de")

    if expected == "small talk":
        return "welcome" in txt or "bienvenido" in txt

    return False

print("📦 Ejecutando pruebas...\n")
success = 0
failures = []
summary = {intent: {"ok": 0, "tot": 0} for _, intent in test_cases}

for i, (msg, expected) in enumerate(test_cases, 1):
    try:
        r = requests.post(BASE_URL, json={"message": msg}, timeout=TIMEOUT)
        r.raise_for_status()
        resp = r.json().get("response", "")
    except Exception as e:
        resp = f"[ERROR] {e}"

    ok = analyze_response(resp, expected)
    mark = "🟩" if ok else "🟥"
    print(f"{mark} Test {i}: {msg}\n   → {resp}\n")

    summary[expected]["tot"] += 1
    if ok:
        success += 1
        summary[expected]["ok"] += 1
    else:
        failures.append((i, msg, resp))

# Save failures
with open("test_results.txt", "w", encoding="utf-8") as f:
    for i, msg, resp in failures:
        f.write(f"Test {i}: {msg}\n→ {resp}\n\n")

total = len(test_cases)
overall_acc = success / total * 100
metrics = {
    "overall_accuracy": round(overall_acc, 2),
    "by_intent": {
        intent: {
            "accuracy": round(stats["ok"] / stats["tot"] * 100, 2),
            "correct": stats["ok"],
            "total": stats["tot"]
        }
        for intent, stats in summary.items()
    }
}

# Save metrics
with open("metrics.json", "w", encoding="utf-8") as f:
    json.dump(metrics, f, ensure_ascii=False, indent=2)
with open("metrics.csv", "w", newline='', encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["intent", "correct", "total", "accuracy"])
    for intent, stats in metrics["by_intent"].items():
        writer.writerow([intent, stats["correct"], stats["total"], stats["accuracy"]])

print("✅ Resultados guardados en test_results.txt, metrics.json y metrics.csv\n")
print("📊 DESGLOSE POR INTENCIÓN:")
for intent, stats in metrics["by_intent"].items():
    print(f"🔹 {intent}: {stats['correct']}/{stats['total']} ({stats['accuracy']}%)")
print(f"\n🎯 Accuracy general: {metrics['overall_accuracy']}%")
