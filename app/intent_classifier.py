from transformers import pipeline

classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def classify_intent(text):
    candidate_labels = [
        "specifications inquiry",
        "price inquiry",
        "stock inquiry",
        "count by brand",
        "greeting",
        "unknown"
    ]

    result = classifier(text, candidate_labels)
    return result["labels"][0]
