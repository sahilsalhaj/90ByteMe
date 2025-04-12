from sentence_transformers import SentenceTransformer
import json

with open("config.json") as f:
    config = json.load(f)

model = SentenceTransformer(config["embedding_model"])

def get_embedding(text):
    return model.encode(text, convert_to_numpy=True)
