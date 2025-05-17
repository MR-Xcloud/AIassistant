import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import os
import time
import pickle

# File to save/load scraped data
DATA_CACHE_FILE = "scraped_data_cache.pkl"

# Initialize variables
texts = ["This is a placeholder text for testing purposes."]
model = None
index = None

def get_internal_links(base_url, max_pages=50):
    """Crawl a website to find internal links"""
    print(f"🔍 Starting to crawl {base_url} (max {max_pages} pages)...")
    visited = set()
    to_visit = [base_url]
    internal_links = set()

    while to_visit and len(visited) < max_pages:
        url = to_visit.pop()
        if url in visited:
            continue
        
        visited.add(url)
        print(f"Visiting: {url} ({len(visited)}/{max_pages})")
        
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/90.0.4430.93 Safari/537.36"}
            response = requests.get(url, timeout=10, headers=headers)

            if response.status_code != 200:
                print(f"⚠️ Status code {response.status_code} for {url}")
                continue
                
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                full_url = urljoin(base_url, href)
                if urlparse(full_url).netloc == urlparse(base_url).netloc:
                    if full_url not in visited and full_url not in to_visit:
                        to_visit.append(full_url)
                        internal_links.add(full_url)
            
            # Small delay to be respectful to the server
            time.sleep(0.5)
            
        except Exception as e:
            print(f"⚠️ Error accessing {url}: {e}")
    
    print(f"🔗 Found {len(internal_links)} internal links")
    return list(internal_links)

def load_data(base_url='https://www.webmobril.com/', max_pages=30, force_reload=False):
    """Load data from website or cache"""
    global texts, model, index
    
    # Check if we have cached data
    if os.path.exists(DATA_CACHE_FILE) and not force_reload:
        try:
            print("📂 Loading data from cache...")
            with open(DATA_CACHE_FILE, 'rb') as f:
                data = pickle.load(f)
                texts = data['texts']
                model = data['model']
                index = data['index']
            print(f"✅ Loaded {len(texts)} text chunks from cache")
            return True
        except Exception as e:
            print(f"⚠️ Error loading cache: {e}")
            print("Will scrape fresh data instead.")
    
    try:
        print("🌐 Scraping website data...")
        # Step 1: Crawl internal links
        urls = get_internal_links(base_url, max_pages)
        
        # Import these only when needed
        try:
            from langchain_community.document_loaders import WebBaseLoader
            from langchain.text_splitter import RecursiveCharacterTextSplitter
            
            # Step 2: Load pages using LangChain
            print("📥 Loading page content...")
            loader = WebBaseLoader(urls)
            docs = loader.load()
            docs = [doc for doc in docs if len(doc.page_content.strip()) > 100]  # Filter empty docs
            
            # Step 3: Split into chunks
            print("✂️ Splitting content into chunks...")
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
            chunks = splitter.split_documents(docs)
            texts = [chunk.page_content for chunk in chunks]
            print(f"📄 Total chunks: {len(texts)}")
            
            # Step 4: Create embeddings
            print("🧠 Creating embeddings...")
            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = model.encode(texts, show_progress_bar=True)
            embeddings = np.array(embeddings)
            
            # Step 5: Create FAISS index
            print("🔍 Building search index...")
            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)
            
            # Save to cache
            print("💾 Saving data to cache...")
            with open(DATA_CACHE_FILE, 'wb') as f:
                pickle.dump({
                    'texts': texts,
                    'model': model,
                    'index': index
                }, f)
            
            print("✅ Website data loaded successfully!")
            return True
            
        except ImportError as e:
            print(f"❌ Missing required packages: {e}")
            print("Please install with: pip install langchain langchain-community")
            initialize_with_placeholder()
            return False
            
    except Exception as e:
        print(f"❌ Error loading website data: {e}")
        initialize_with_placeholder()
        return False

def initialize_with_placeholder():
    """Initialize with placeholder data if real data loading fails"""
    global texts, model, index
    
    print("⚠️ Using placeholder data instead")
    try:
        texts = [
            "WebMobril is a leading web and mobile app development company.",
            "We specialize in custom software development, UI/UX design, and digital marketing.",
            "Our team of experts delivers high-quality solutions for businesses of all sizes.",
            "Contact us for your next digital project and experience excellence in service."
        ]
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(texts)
        embeddings = np.array(embeddings)
        
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        print("✅ Initialized with placeholder data")
        return True
    except Exception as e:
        print(f"❌ Error initializing placeholder data: {e}")
        return False

def get_answer(query, top_k=3):
    """Get answer for a query using semantic search with improved precision"""
    if model is None or index is None:
        load_data()
    
    # Process the query to identify specific question types
    query_lower = query.lower()
    
    # Check for specific question types
    is_who_question = any(x in query_lower for x in ["who is", "who's", "who are", "name of"])
    is_ceo_question = "ceo" in query_lower or "chief executive" in query_lower
    is_founder_question = "founder" in query_lower or "started" in query_lower
    is_when_question = any(x in query_lower for x in ["when", "what year", "what date"])
    is_where_question = any(x in query_lower for x in ["where is", "where are", "location"])
    
    # Encode the query
    query_embedding = model.encode([query])
    
    # Search in the index
    distances, indices = index.search(query_embedding, top_k)
    
    # Get the most relevant chunks
    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(texts):
            results.append({
                "text": texts[idx],
                "score": float(distances[0][i])
            })
    
    # Format the answer - more concise version
    if not results:
        return "I don't have information on that topic."
    
    # For CEO or specific person questions, try to extract just the name
    if is_who_question and (is_ceo_question or is_founder_question):
        # Look for patterns like "CEO [Name]" or "[Name] is the CEO"
        for result in results:
            text = result["text"].lower()
            
            # Try to find CEO name patterns
            if is_ceo_question and ("ceo" in text or "chief executive" in text):
                # Extract sentences containing CEO references
                sentences = [s.strip() for s in result["text"].split('.') if "CEO" in s or "Chief Executive" in s or "chief executive" in s]
                if sentences:
                    return sentences[0]
            
            # Try to find founder name patterns
            if is_founder_question and ("founder" in text or "founded by" in text or "started by" in text):
                # Extract sentences containing founder references
                sentences = [s.strip() for s in result["text"].split('.') if "founder" in s.lower() or "founded" in s.lower() or "started" in s.lower()]
                if sentences:
                    return sentences[0]
    
    # For when questions, try to extract dates or years
    if is_when_question:
        for result in results:
            text = result["text"]
            # Extract sentences containing dates or years (4 digit numbers)
            import re
            sentences = [s.strip() for s in text.split('.') if re.search(r'\b(19|20)\d{2}\b', s) or 
                        any(month in s.lower() for month in ["january", "february", "march", "april", "may", "june", 
                                                           "july", "august", "september", "october", "november", "december"])]
            if sentences:
                return sentences[0]
    
    # For where questions, try to extract location information
    if is_where_question:
        for result in results:
            text = result["text"]
            # Extract sentences containing location indicators
            sentences = [s.strip() for s in text.split('.') if "located" in s.lower() or "address" in s.lower() or 
                        "based in" in s.lower() or "headquartered" in s.lower()]
            if sentences:
                return sentences[0]
    
    # Default: return the most relevant result
    best_result = results[0]["text"]
    
    # Clean up the text - remove extra whitespace and newlines
    best_result = ' '.join(best_result.split())
    
    # If the result is too long, try to extract the most relevant sentence
    if len(best_result) > 150:
        sentences = best_result.split('.')
        # Return the first non-empty sentence
        for sentence in sentences:
            if len(sentence.strip()) > 10:  # Ensure it's not just a short fragment
                return sentence.strip() + "."
    
    return best_result

# Load data when this module is imported
if __name__ == "__main__":
    print("🚀 Initializing data loader...")
    load_data()