"""
Data cleaner script to clean and organize the scraped data.
This script removes duplicates, categorizes content, and extracts structured information.
"""

import pickle
import os
import re
import json
import faiss
import numpy as np

# File to load scraped data
DATA_CACHE_FILE = "scraped_data_cache.pkl"
CLEAN_DATA_FILE = "clean_data.pkl"
CLEAN_TEXT_FILE = "clean_data.txt"

def clean_scraped_data():
    """Clean and organize the scraped data"""
    print("Cleaning scraped data...")
    
    # Load scraped data
    if not os.path.exists(DATA_CACHE_FILE):
        print(f"Error: {DATA_CACHE_FILE} not found. Please run the scraper first.")
        return False
    
    try:
        with open(DATA_CACHE_FILE, 'rb') as f:
            data = pickle.load(f)
            texts = data['texts']
            model = data['model']
            index = data['index']
        print(f"Loaded {len(texts)} text chunks")
    except Exception as e:
        print(f"Error loading cache: {e}")
        return False
    
    # Step 1: Remove duplicates
    print("Removing duplicates...")
    unique_texts = []
    seen_content = set()
    
    for text in texts:
        # Extract the content part (after the source)
        if ":" in text:
            content = text.split(":", 1)[1].strip()
        else:
            content = text.strip()
            
        # Skip very short content
        if len(content) < 20:
            continue
            
        # Skip if we've seen this content before
        content_normalized = re.sub(r'\s+', ' ', content.lower())
        if content_normalized in seen_content:
            continue
            
        seen_content.add(content_normalized)
        unique_texts.append(text)
    
    print(f"Removed {len(texts) - len(unique_texts)} duplicates")
    
    # Step 2: Categorize content
    print("Categorizing content...")
    categories = {
        "products": [],
        "services": [],
        "company_info": [],
        "team": [],
        "contact": [],
        "other": []
    }
    
    for text in unique_texts:
        text_lower = text.lower()
        
        # Categorize based on content
        if any(keyword in text_lower for keyword in ["product", "project", "portfolio", "work", "case study"]):
            categories["products"].append(text)
        elif any(keyword in text_lower for keyword in ["service", "offer", "solution", "expertise"]):
            categories["services"].append(text)
        elif any(keyword in text_lower for keyword in ["company", "about us", "mission", "vision", "founded", "history"]):
            categories["company_info"].append(text)
        elif any(keyword in text_lower for keyword in ["team", "staff", "employee", "ceo", "founder", "director"]):
            categories["team"].append(text)
        elif any(keyword in text_lower for keyword in ["contact", "address", "phone", "email", "location"]):
            categories["contact"].append(text)
        else:
            categories["other"].append(text)
    
    for category, items in categories.items():
        print(f"  {category}: {len(items)} items")
    
    # Step 3: Extract structured information
    print("Extracting structured information...")
    
    # Extract product information
    products = []
    for text in categories["products"]:
        # Try to extract product name
        product_name = None
        content = ""
        if ":" in text:
            source, content = text.split(":", 1)
            if "product" in source.lower() or "project" in source.lower():
                # Try to extract product name from content
                product_name = content.strip().split(" - ")[0].strip()
        
        if product_name and len(product_name) > 3:
            # Check if we already have this product
            if not any(p.get("name", "").lower() == product_name.lower() for p in products):
                products.append({
                    "name": product_name,
                    "description": content.strip(),
                    "source": text
                })
    
    print(f"Extracted {len(products)} products")
    
    # Extract team information
    team_members = []
    for text in categories["team"]:
        # Look for name patterns
        name_match = re.search(r'([A-Z][a-z]+ [A-Z][a-z]+)', text)
        if name_match:
            name = name_match.group(1)
            
            # Look for role patterns
            role = None
            role_patterns = [
                r'(?:is|as) (?:the|a|an) ([^\.]+)',
                r'([^,]+?)(?:,| at| of| in)',
                r'- ([^-]+)'
            ]
            
            for pattern in role_patterns:
                role_match = re.search(pattern, text)
                if role_match:
                    role = role_match.group(1).strip()
                    break
            
            if role:
                # Check if we already have this person
                if not any(m.get("name", "").lower() == name.lower() for m in team_members):
                    team_members.append({
                        "name": name,
                        "role": role,
                        "source": text
                    })
    
    print(f"Extracted {len(team_members)} team members")
    
    # Create clean data structure
    clean_data = {
        "products": products,
        "team_members": team_members,
        "categories": categories,
        "unique_texts": unique_texts
    }
    
    # Save clean data
    try:
        with open(CLEAN_DATA_FILE, 'wb') as f:
            pickle.dump(clean_data, f)
        
        # Also save as JSON for easy inspection
        with open("clean_data.json", 'w', encoding='utf-8') as f:
            # Convert to JSON-serializable format
            json_data = {
                "products": products,
                "team_members": team_members,
                "categories": {k: len(v) for k, v in categories.items()}
            }
            json.dump(json_data, f, indent=2)
        
        print(f"Saved clean data to {CLEAN_DATA_FILE} and clean_data.json")
    except Exception as e:
        print(f"Error saving clean data: {e}")
        return False
    
    # Save as text file for easy reading
    try:
        with open(CLEAN_TEXT_FILE, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("CLEAN DATA EXPORT\n")
            f.write("=" * 80 + "\n\n")
            
            # Write products section
            f.write("=" * 80 + "\n")
            f.write("PRODUCTS\n")
            f.write("=" * 80 + "\n\n")
            
            for i, product in enumerate(products):
                f.write(f"Product {i+1}: {product.get('name', 'Unknown')}\n")
                f.write("-" * 40 + "\n")
                f.write(f"Description: {product.get('description', 'No description')}\n")
                f.write(f"Source: {product.get('source', 'No source')}\n\n")
            
            # Write team members section
            f.write("=" * 80 + "\n")
            f.write("TEAM MEMBERS\n")
            f.write("=" * 80 + "\n\n")
            
            for i, member in enumerate(team_members):
                f.write(f"Team Member {i+1}: {member.get('name', 'Unknown')}\n")
                f.write("-" * 40 + "\n")
                f.write(f"Role: {member.get('role', 'Unknown role')}\n")
                f.write(f"Source: {member.get('source', 'No source')}\n\n")
            
            # Write categorized content
            for category, items in categories.items():
                f.write("=" * 80 + "\n")
                f.write(f"{category.upper()} ({len(items)} items)\n")
                f.write("=" * 80 + "\n\n")
                
                for i, item in enumerate(items[:20]):  # Limit to first 20 items per category
                    f.write(f"Item {i+1}: {item}\n\n")
                
                if len(items) > 20:
                    f.write(f"... and {len(items) - 20} more items\n\n")
        
        print(f"Saved clean data as text to {CLEAN_TEXT_FILE}")
    except Exception as e:
        print(f"Error saving text file: {e}")
    
    # Update the original data with the clean texts
    try:
        # Re-encode the clean texts
        print("Re-encoding clean texts...")
        clean_embeddings = model.encode(unique_texts, show_progress_bar=True)
        
        # Create a new FAISS index
        dimension = clean_embeddings.shape[1]
        new_index = faiss.IndexFlatL2(dimension)
        new_index.add(clean_embeddings)
        
        # Save the updated data
        print("Saving updated data...")
        with open(DATA_CACHE_FILE, 'wb') as f:
            pickle.dump({
                'texts': unique_texts,
                'model': model,
                'index': new_index
            }, f)
        
        print("Data saved successfully!")
    except Exception as e:
        print(f"Error updating original data: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = clean_scraped_data()
    if success:
        print("Data cleaning completed successfully!")
    else:
        print("Data cleaning failed.")