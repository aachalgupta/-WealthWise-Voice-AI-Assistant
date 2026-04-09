"""
ingest.py
Loads WealthWise Advisory FAQs into Qdrant vector database.
"""

import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import OpenAI
from faq_data import faqs

load_dotenv()

QDRANT_URL      = os.getenv("QDRANT_URL")
QDRANT_API_KEY  = os.getenv("QDRANT_API_KEY")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
COLLECTION_NAME = "wealthwise_faqs"
EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_SIZE     = 1536

openai_client = OpenAI(api_key=OPENAI_API_KEY)
qdrant_client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)


def get_embedding(text: str) -> list[float]:
    response = openai_client.embeddings.create(
        input=text,
        model=EMBEDDING_MODEL
    )
    return response.data[0].embedding


def create_collection():
    existing = [c.name for c in qdrant_client.get_collections().collections]
    if COLLECTION_NAME in existing:
        print(f"Collection '{COLLECTION_NAME}' already exists. Deleting and recreating...")
        qdrant_client.delete_collection(COLLECTION_NAME)
    qdrant_client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    print(f"Collection '{COLLECTION_NAME}' created.\n")

def ingest_faqs():
    points = []
    for i, faq in enumerate(faqs):
        text_to_embed = f"Question: {faq['question']} Answer: {faq['answer']}"
        embedding = get_embedding(text_to_embed)
        points.append(
            PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "question": faq["question"],
                    "answer":   faq["answer"],
                }
            )
        )
        print(f"  [{i+1}/{len(faqs)}] Embedded: {faq['question']}")

    batch_size = 10
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        qdrant_client.upsert(collection_name=COLLECTION_NAME, points=batch)
        print(f"  Uploaded batch {i // batch_size + 1} ({len(batch)} points)")

    print(f"\n✅ Successfully ingested {len(faqs)} FAQs into Qdrant collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    print("Starting WealthWise FAQ ingestion...\n")
    create_collection()
    ingest_faqs()
