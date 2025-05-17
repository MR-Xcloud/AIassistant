"""
Script to update the knowledge base with product information and scrape additional data.
This will ensure the voice assistant can answer questions about products and projects.
"""

import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from company_products import COMPANY_PRODUCTS
from scrape_work_page import scrape_work_page

# File to save/load scraped data
DATA_CACHE_FILE = "scraped_data_cache.pkl"

def update_knowledge_base():
    """Update the knowledge base with product information"""
    print("Updating knowledge base with product information...")
    
    # Load existing data if available
    if os.path.exists(DATA_CACHE_FILE):
        try:
            with open(DATA_CACHE_FILE, 'rb') as f:
                data = pickle.load(f)
                texts = data['texts']
                model = data['model']
                index = data['index']
            print(f"Loaded {len(texts)} existing text chunks")
        except Exception as e:
            print(f"Error loading cache: {e}")
            texts = []
            model = SentenceTransformer("all-MiniLM-L6-v2")
            index = None
    else:
        texts = []
        model = SentenceTransformer("all-MiniLM-L6-v2")
        index = None
    
    # Add product information
    new_texts = []
    
    # Add product descriptions
    for product in COMPANY_PRODUCTS["Products"]:
        product_text = f"Product: {product['name']} - {product['description']} It is a {product['type']} for the {product['industry']} industry."
        new_texts.append(product_text)
    
    # Add project descriptions
    for project in COMPANY_PRODUCTS["Projects"]:
        project_text = f"Project: {project['name']} - {project['description']} It was developed for {project['client']} using {project['technologies']}."
        new_texts.append(project_text)
    
    # Add service descriptions
    services_text = f"WebMobril offers the following services: {', '.join(COMPANY_PRODUCTS['Services'])}"
    new_texts.append(services_text)
    
    # Add new texts to the existing texts
    texts.extend(new_texts)
    print(f"Added {len(new_texts)} product and project descriptions")
    
    # Scrape additional data from the Work page
    print("Scraping additional data from the Work page...")
    num_scraped = scrape_work_page()
    
    # If no new data was scraped, we still need to update with our product info
    if num_scraped == 0:
        # Create embeddings for all texts
        print("Creating embeddings for all text chunks...")
        all_embeddings = model.encode(texts, show_progress_bar=True)
        all_embeddings = np.array(all_embeddings)
        
        # Create a new FAISS index
        dimension = all_embeddings.shape[1]
        new_index = faiss.IndexFlatL2(dimension)
        new_index.add(all_embeddings)
        
        # Save the updated data
        print("Saving updated data...")
        with open(DATA_CACHE_FILE, 'wb') as f:
            pickle.dump({
                'texts': texts,
                'model': model,
                'index': new_index
            }, f)
        
        print("Data saved successfully!")
    
    return len(new_texts)

if __name__ == "__main__":
    num_new_chunks = update_knowledge_base()
    print(f"Knowledge base update completed. Added {num_new_chunks} new text chunks.")