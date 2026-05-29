import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from sentence_transformers import SentenceTransformer
from database import products_col

def generate_embeddings():
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    col = products_col()
    products = list(col.find({}))
    print(f"Found {len(products)} products in MongoDB.")
    
    updated_count = 0
    for p in products:
        text = f"{p.get('name', '')} {p.get('category', '')} {p.get('description', '')}"
        
        # Calculate embedding
        embedding = model.encode(text).tolist()
        
        # Update document
        result = col.update_one(
            {"_id": p["_id"]},
            {"$set": {"embedding": embedding}}
        )
        if result.modified_count > 0:
            updated_count += 1
            
    print(f"Successfully generated and stored embeddings for {updated_count} products.")

if __name__ == "__main__":
    generate_embeddings()
