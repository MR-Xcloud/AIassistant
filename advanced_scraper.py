"""
Advanced scraper using Selenium to extract product details from the Work page.
This script navigates to product pages and extracts detailed information.
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pickle
import os
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

# File to save/load scraped data
DATA_CACHE_FILE = "scraped_data_cache.pkl"

def scrape_product_details():
    """Scrape product details from the Work page using Selenium"""
    print("Setting up Chrome WebDriver...")
    
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    # Set up Chrome WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
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
    
    try:
        # First, visit the main website to find all relevant links
        print("Navigating to the main website...")
        driver.get("https://www.webmobril.com/")
        
        # Wait for the page to load
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        
        # Find all links on the main page
        all_links = []
        links = driver.find_elements(By.TAG_NAME, "a")
        for link in links:
            try:
                href = link.get_attribute("href")
                if href and "webmobril.com" in href and href not in all_links:
                    all_links.append(href)
            except:
                pass
        
        print(f"Found {len(all_links)} links on the main website")
        
        # Filter links that might contain product information
        product_links = []
        for link in all_links:
            if any(keyword in link.lower() for keyword in ["work", "portfolio", "project", "case-study", "product"]):
                product_links.append(link)
        
        # Add the main work page
        if "https://www.webmobril.com/work/" not in product_links:
            product_links.append("https://www.webmobril.com/work/")
        
        print(f"Filtered {len(product_links)} potential product links")
        
        # Visit each potential product page
        visited_links = set()
        for i, link in enumerate(product_links):
            if link in visited_links:
                continue
                
            visited_links.add(link)
            
            try:
                print(f"Visiting link {i+1}/{len(product_links)}: {link}")
                driver.get(link)
                
                # Wait for the page to load
                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                
                # Extract page title
                title = driver.title
                
                # Add to new texts
                new_texts.append(f"Page title from {link}: {title}")
                
                # Extract all text from the page
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Split page text into paragraphs
                paragraphs = page_text.split('\n')
                for paragraph in paragraphs:
                    if len(paragraph.strip()) > 50:  # Only add substantial paragraphs
                        new_texts.append(f"Content from {link}: {paragraph.strip()}")
                
                # Extract specific elements
                try:
                    # Try to find headings
                    headings = driver.find_elements(By.CSS_SELECTOR, "h1, h2, h3")
                    for heading in headings:
                        heading_text = heading.text.strip()
                        if heading_text:
                            new_texts.append(f"Heading from {link}: {heading_text}")
                    
                    # Try to find paragraphs
                    paragraphs = driver.find_elements(By.TAG_NAME, "p")
                    for paragraph in paragraphs:
                        paragraph_text = paragraph.text.strip()
                        if paragraph_text and len(paragraph_text) > 50:
                            new_texts.append(f"Paragraph from {link}: {paragraph_text}")
                            
                    # Try to find project items
                    project_items = []
                    selectors = [
                        ".project-item", ".portfolio-item", ".work-item", ".case-study", 
                        ".col-md-4", ".col-md-6", ".col-lg-4", "article"
                    ]
                    
                    for selector in selectors:
                        try:
                            items = driver.find_elements(By.CSS_SELECTOR, selector)
                            if items:
                                project_items.extend(items)
                        except:
                            pass
                    
                    # Extract information from project items
                    for item in project_items:
                        try:
                            item_text = item.text.strip()
                            if item_text and len(item_text) > 20:
                                new_texts.append(f"Project item from {link}: {item_text}")
                                
                            # Try to find links within the project item
                            item_links = item.find_elements(By.TAG_NAME, "a")
                            for item_link in item_links:
                                try:
                                    href = item_link.get_attribute("href")
                                    if href and "webmobril.com" in href and href not in visited_links:
                                        product_links.append(href)
                                except:
                                    pass
                        except:
                            pass
                except Exception as e:
                    print(f"Error extracting elements from {link}: {e}")
                
                # Be respectful to the server
                time.sleep(1)
            except Exception as e:
                print(f"Error processing link {link}: {e}")
        
        print(f"Extracted {len(new_texts)} new text chunks")
        
    except Exception as e:
        print(f"Error during scraping: {e}")
    
    finally:
        # Close the browser
        driver.quit()
    
    # Add new texts to the existing texts
    texts.extend(new_texts)
    print(f"Total texts: {len(texts)}")
    
    # Create embeddings for all texts
    if new_texts:
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
    num_new_chunks = scrape_product_details()
    print(f"Advanced scraping completed. Added {num_new_chunks} new text chunks to the knowledge base.")