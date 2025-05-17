"""
Script to specifically scrape the Work/Portfolio page of WebMobril.
This will extract information about projects and products developed by the company.
"""

import requests
from bs4 import BeautifulSoup
import pickle
import os
import time
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from urllib.parse import urljoin

# File to save/load scraped data
DATA_CACHE_FILE = "scraped_data_cache.pkl"

def discover_links(base_url, headers):
    """Discover relevant links from the main website"""
    print(f"Discovering links from {base_url}...")
    try:
        response = requests.get(base_url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/') or href.startswith(base_url):
                    full_url = urljoin(base_url, href)
                    if any(keyword in full_url.lower() for keyword in ['portfolio', 'work', 'project', 'case', 'study', 'product', 'service']):
                        if full_url not in links:
                            links.append(full_url)
            print(f"Discovered {len(links)} relevant links")
            return links
        return []
    except Exception as e:
        print(f"Error discovering links: {e}")
        return []

def scrape_work_page():
    """Scrape the Work/Portfolio page of WebMobril"""
    print("Scraping the Work/Portfolio page...")
    
    # Initial URLs to scrape
    urls = [
        "https://www.webmobril.com/work/",
        "https://www.webmobril.com/",  # Main website
        "https://www.webmobril.com/services/",  # Services page
        "https://www.webmobril.com/about-us/"  # About page
    ]
    
    # Headers for the request
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/90.0.4430.93 Safari/537.36"
    }
    
    # Discover additional links
    additional_links = discover_links("https://www.webmobril.com/", headers)
    urls.extend(additional_links)
    
    # Remove duplicates
    urls = list(set(urls))
    
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
    
    # Track new texts added
    new_texts = []
    
    # Scrape each URL
    for url in urls:
        print(f"Scraping {url}...")
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code != 200:
                print(f"Failed to access {url}: {response.status_code}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract all text from the page
            page_text = soup.get_text(separator=' ', strip=True)
            
            # Split into paragraphs
            paragraphs = [p.get_text(separator=' ', strip=True) for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])]
            paragraphs = [p for p in paragraphs if len(p) > 50]  # Filter out short paragraphs
            
            # Extract project information - try different selectors
            project_elements = []
            
            # Try different common class names for project items
            for class_name in ['project-item', 'portfolio-item', 'case-study', 'product-item', 'work-item', 'service-item']:
                elements = soup.find_all('div', class_=class_name)
                if elements:
                    project_elements.extend(elements)
            
            # Try article tags
            project_elements.extend(soup.find_all('article'))
            
            # Try common grid layouts
            for class_name in ['col-md-4', 'col-md-6', 'col-lg-4', 'col-sm-6']:
                elements = soup.find_all('div', class_=class_name)
                if elements:
                    project_elements.extend(elements)
            
            # Extract text from project elements
            for element in project_elements:
                project_text = element.get_text(separator=' ', strip=True)
                if len(project_text) > 100:  # Filter out very short descriptions
                    new_texts.append(f"Project from {url}: {project_text}")
            
            # Add paragraphs as separate chunks
            for paragraph in paragraphs:
                new_texts.append(f"Content from {url}: {paragraph}")
            
            # Add a delay to be respectful to the server
            time.sleep(1)
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    # Add new texts to the existing texts
    texts.extend(new_texts)
    print(f"Added {len(new_texts)} new text chunks")
    
    # Create embeddings for the new texts
    if new_texts:
        print("Creating embeddings for new text chunks...")
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
    else:
        print("No new text chunks found.")
    
    return len(new_texts)

if __name__ == "__main__":
    num_new_chunks = scrape_work_page()
    print(f"Scraping completed. Added {num_new_chunks} new text chunks to the knowledge base.")