import json
from langdetect import detect
from fuzzywuzzy import fuzz
from sentence_transformers import SentenceTransformer, util

# Load model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load data
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

intents_examples = {
    "get total stock": [
        "how many computers do you have",
        "total available stock",
        "total units available",
        "cuántas computadoras tienen en total",
        "how many laptops are there",
        "¿Tienen muchas laptops en stock?",
        "inventory size",
        "what computers are available",
        "stock general"
    ],
    "get stock by brand": [
        "how many HP laptops are available",
        "¿Cuántas computadoras Apple hay?",
        "stock of Dell",
        "availability of HP",
        "how many Apple computers are left",
        "Do you have Dell laptops?",
        "stock for Pavilion",
        "how many Pavilion models are in stock",
        "what brands do you currently stock",
        "¿Tienen computadoras de la marca Apple?"
    ],
    "get computer specifications": [
        "tell me the specs of the HP Pavilion 15",
        "cuéntame más sobre la Dell",
        "especificaciones de la MacBook",
        "RAM and processor of Dell Inspiron 14",
        "Give me technical details for the MacBook",
        "What does the Pavilion 15 offer?",
        "Can you describe the Apple laptop specs?",
        "tell me about the HP Envy"
    ],
    "get price of a computer": [
        "how much is the Dell Inspiron",
        "precio de la HP Pavilion",
        "cost of MacBook",
        "Envy price please",
        "cuánto cuesta la computadora Apple",
        "Tell me the cost for the Apple MacBook Air",
        "Price of the HP Envy",
        "cuánto cuesta la Pavilion 15"
    ],
    "small talk": [
        "hi", "hello", "hola", "buenos días", "what can you do?",
        "can you help me?", "I love HP laptops", "Inspiron sounds cool",
        "apple is expensive", "quiero una computadora buena", "laptop bonita"
    ]
}

translations = {
    "en": {
        "stock_by_brand": "We have {stock} {entity} {noun} available.",
        "specs": "{name} - RAM: {ram} - Processor: {processor} - Price: {price} - Stock: {stock}",
        "total": "We have {total} {noun} in stock.",
        "price": "The price of {name} is {price}.",
        "list_brands": "We stock: {brands}.",
        "not_found": "Sorry, I couldn't find that computer.",
        "not_understood": "Sorry, I didn't understand your request.",
        "welcome": "Welcome! Ask me anything about the available computers."
    },
    "es": {
        "stock_by_brand": "Tenemos {stock} {noun} {entity} disponibles.",
        "specs": "{name} - RAM: {ram} - Procesador: {processor} - Precio: {price} - Stock: {stock}",
        "total": "Tenemos {total} {noun} en stock.",
        "price": "El precio de {name} es {price}.",
        "list_brands": "Disponemos de: {brands}.",
        "not_found": "Lo siento, no encontré esa computadora.",
        "not_understood": "Lo siento, no entendí tu solicitud.",
        "welcome": "¡Bienvenido! Pregúntame cualquier cosa sobre las computadoras disponibles."
    }
}

name_aliases = {
    "dell inspiron": "Dell Inspiron 14",
    "hp pavilion": "HP Pavilion 15",
    "macbook": "Apple MacBook Air",
    "mac": "Apple MacBook Air",
    "hp envy": "HP Envy",
    "pavilion": "HP Pavilion 15",
    "dell": "Dell Inspiron 14",
    "apple": "Apple MacBook Air",
    "inspiron": "Dell Inspiron 14",
    "envy": "HP Envy"
}
brand_aliases = {
    "hp": "HP", "hewlett packard": "HP", "apple": "Apple",
    "mac": "Apple", "dell": "Dell", "pavilion": "HP"
}

SMALLTALK = intents_examples["small talk"]
BRAND_KEYWORDS = ["brand", "brands", "marca", "marcas"]

# flat list and embeddings
flat = [(intent, ex) for intent, exs in intents_examples.items() for ex in exs]
texts = [ex for _, ex in flat]
embs = embedder.encode(texts, convert_to_tensor=True)

def get_language(text):
    try:
        return detect(text)
    except:
        return "en"

def is_smalltalk(msg):
    return any(fuzz.partial_ratio(p.lower(), msg) >= 90 for p in SMALLTALK)

def is_brand_list_query(msg):
    return any(k in msg for k in BRAND_KEYWORDS)

def extract_closest_computer_name(msg, th=80):
    opts = list({pc["name"] for pc in data}) + list(name_aliases.keys())
    best,score=None,0
    for n in opts:
        s = fuzz.partial_ratio(n.lower(), msg)
        if s>score and s>=th:
            best,score=n,s
    return name_aliases.get(best.lower(), best) if best else None

def extract_closest_brand(msg, th=80):
    opts = list({pc["brand"] for pc in data}) + list(brand_aliases.keys())
    best,score=None,0
    for b in opts:
        s = fuzz.partial_ratio(b.lower(), msg)
        if s>score and s>=th:
            best,score=b,s
    return brand_aliases.get(best.lower(), best) if best else None

def classify_intent(message, threshold=0.60):
    msg = message.lower()
    if is_smalltalk(msg):
        return "small talk"
    if is_brand_list_query(msg):
        return "list brands"
    emb_q = embedder.encode(msg, convert_to_tensor=True)
    sims = util.cos_sim(emb_q, embs)[0]
    idx = int(sims.argmax()); score = float(sims[idx])
    intent = flat[idx][0]
    if score < threshold:
        return "not_understood"
    return intent

def generate_response(message):
    lang = get_language(message)
    t = translations.get(lang, translations["en"]) 
    msg = message.lower()

    if msg in ["hi", "hello", "hola", "buenos días", "buenas"]:
        return t["welcome"]

    intent = classify_intent(msg)

    if intent == "get total stock":
        total = sum(int(pc["stock"]) for pc in data)
        noun = "computer" if total == 1 else "computers"
        if lang == "es":
            noun = "computadora" if total == 1 else "computadoras"
        return t["total"].format(total=total, noun=noun)

    if intent == "list brands":
        brands = sorted({pc["brand"] for pc in data})
        return t["list_brands"].format(brands=", ".join(brands))

    if intent == "get stock by brand":
        name = extract_closest_computer_name(msg)
        if name:
            for pc in data:
                if pc["name"].lower() == name.lower():
                    count = pc["stock"]; ent = name
                    noun = "computer" if count == 1 else "computers"
                    if lang == "es":
                        noun = "computadora" if count == 1 else "computadoras"
                    return t["stock_by_brand"].format(stock=count, entity=ent, noun=noun)
        brand = extract_closest_brand(msg)
        if brand:
            count = sum(int(pc["stock"]) for pc in data if pc["brand"].lower() == brand.lower())
            ent = brand
            noun = "computer" if count == 1 else "computers"
            if lang == "es":
                noun = "computadora" if count == 1 else "computadoras"
            return t["stock_by_brand"].format(stock=count, entity=ent, noun=noun)
        return t["not_found"]

    if intent == "get computer specifications":
        name = extract_closest_computer_name(msg)
        if name:
            for pc in data:
                if pc["name"].lower() == name.lower():
                    return t["specs"].format(**pc)
        return t["not_found"]

    if intent == "get price of a computer":
        name = extract_closest_computer_name(msg)
        if name:
            for pc in data:
                if pc["name"].lower() == name.lower():
                    return t["price"].format(name=pc["name"], price=pc["price"])
        return t["not_found"]

    if intent == "small talk":
        return t["welcome"]

    return t["not_understood"]
