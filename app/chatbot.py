from app.intent_classifier import classify_intent

def generate_response(message, data):
    intent = classify_intent(message.lower())

    if intent == "greeting":
        return "Hello! How can I assist you with the computers?"

    elif intent == "count by brand":
        for item in data:
            if item["brand"].lower() in message.lower():
                return f"We have {item['stock']} {item['brand']} computers available."
        return "We don't have that brand available."

    elif intent in ["specifications inquiry", "price inquiry", "stock inquiry"]:
        for item in data:
            if item["model"].lower() in message.lower() or item["brand"].lower() in message.lower():
                return f"{item['brand']} {item['model']}: RAM: {item['ram']}, Processor: {item['processor']}, Price: S/. {item['price']}, Stock: {item['stock']}"
        return "I couldn't find that model."

    else:
        return "Sorry, I didn't understand your question. Could you rephrase it?"
