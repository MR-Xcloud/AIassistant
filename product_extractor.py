"""
Product extractor module to extract structured product information.
This module processes the scraped data to extract specific product details.
"""

import pickle
import os
import re
from company_products import COMPANY_PRODUCTS

# File to save/load scraped data
DATA_CACHE_FILE = "scraped_data_cache.pkl"
PRODUCTS_FILE = "extracted_products.pkl"

def extract_products():
    """Extract structured product information from scraped data"""
    print("Extracting product information from scraped data...")
    
    # Load scraped data
    if not os.path.exists(DATA_CACHE_FILE):
        print(f"Error: {DATA_CACHE_FILE} not found. Please run the scraper first.")
        return []
    
    try:
        with open(DATA_CACHE_FILE, 'rb') as f:
            data = pickle.load(f)
            texts = data['texts']
        print(f"Loaded {len(texts)} text chunks")
    except Exception as e:
        print(f"Error loading cache: {e}")
        return []
    
    # Initialize products list with known products
    products = COMPANY_PRODUCTS["Products"].copy()
    
    # Extract product information from texts
    product_texts = [text for text in texts if "product" in text.lower() or "project" in text.lower()]
    
    # Extract product names
    product_names = set()
    for product in products:
        product_names.add(product["name"].lower())
    
    # Find potential new product names
    for text in product_texts:
        # Look for patterns like "Product: Name" or "Project: Name"
        matches = re.findall(r'(?:product|project)(?:\s+from|\s*:)\s*([^\.,:]+)', text.lower())
        for match in matches:
            product_name = match.strip()
            if product_name and len(product_name) > 3 and product_name not in product_names:
                product_names.add(product_name)
    
    print(f"Found {len(product_names)} potential product names")
    
    # Extract information for each product
    for product_name in product_names:
        # Skip products we already have information for
        if any(p["name"].lower() == product_name for p in products):
            continue
        
        # Find texts related to this product
        related_texts = [text for text in texts if product_name in text.lower()]
        
        if not related_texts:
            continue
        
        # Extract description
        description = ""
        for text in related_texts:
            if "description" in text.lower() or "about" in text.lower():
                # Extract the part after "description:" or similar
                desc_match = re.search(r'(?:description|about)(?:\s+from|\s*:)\s*([^\.]+)', text, re.IGNORECASE)
                if desc_match:
                    description = desc_match.group(1).strip()
                    break
        
        # If no specific description found, use the first substantial related text
        if not description and related_texts:
            description = related_texts[0].split(":", 1)[1].strip() if ":" in related_texts[0] else related_texts[0]
        
        # Extract type
        product_type = "Web & Mobile Application"  # Default
        for text in related_texts:
            if "type" in text.lower() or "platform" in text.lower() or "technology" in text.lower():
                if "mobile" in text.lower() and "web" in text.lower():
                    product_type = "Web & Mobile Application"
                    break
                elif "mobile" in text.lower() or "app" in text.lower():
                    product_type = "Mobile App"
                    break
                elif "web" in text.lower():
                    product_type = "Web Application"
                    break
        
        # Extract industry
        industry = "Technology"  # Default
        for text in related_texts:
            if "industry" in text.lower() or "sector" in text.lower():
                for ind in ["Healthcare", "Finance", "Retail", "Education", "Transportation", "Real Estate"]:
                    if ind.lower() in text.lower():
                        industry = ind
                        break
        
        # Create product entry
        new_product = {
            "name": product_name.title(),
            "description": description,
            "type": product_type,
            "industry": industry
        }
        
        products.append(new_product)
    
    print(f"Extracted information for {len(products)} products")
    
    # Save extracted products
    try:
        with open(PRODUCTS_FILE, 'wb') as f:
            pickle.dump(products, f)
        print(f"Saved product information to {PRODUCTS_FILE}")
    except Exception as e:
        print(f"Error saving product information: {e}")
    
    return products

if __name__ == "__main__":
    products = extract_products()
    print(f"Extracted {len(products)} products")