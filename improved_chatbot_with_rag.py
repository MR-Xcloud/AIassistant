"""
Improved chatbot with RAG (Retrieval-Augmented Generation) using Groq.
This module enhances the original chatbot with better answer generation.
"""

import os
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from rag_groq import RAGGroq, load_rag_engine
from company_facts import COMPANY_FACTS

# File to save/load scraped data
DATA_CACHE_FILE = "scraped_data_cache.pkl"

# Initialize variables
texts = ["This is a placeholder text for testing purposes."]
model = None
index = None
rag_engine = None

def load_data(force_reload=False):
    """Load data from cache and initialize RAG engine"""
    global texts, model, index, rag_engine
    
    # Check if we have cached data
    if os.path.exists(DATA_CACHE_FILE) and not force_reload:
        try:
            print("Loading data from cache...")
            with open(DATA_CACHE_FILE, 'rb') as f:
                data = pickle.load(f)
                texts = data['texts']
                model = data['model']
                index = data['index']
            print(f"Loaded {len(texts)} text chunks from cache")
            
            # Initialize RAG engine with loaded texts
            print("Initializing RAG engine with Groq...")
            rag_engine = load_rag_engine(texts)
            print("RAG engine initialized")
            
            return True
        except Exception as e:
            print(f"Error loading cache: {e}")
            print("Will use placeholder data instead.")
            initialize_with_placeholder()
            return False
    else:
        initialize_with_placeholder()
        return True

def initialize_with_placeholder():
    """Initialize with placeholder data"""
    global texts, model, index, rag_engine
    
    print("Using placeholder data")
    try:
        texts = [
            "WebMobril is a leading web and mobile app development company.",
            "We specialize in custom software development, UI/UX design, and digital marketing.",
            "Our team of experts delivers high-quality solutions for businesses of all sizes.",
            "Contact us for your next digital project and experience excellence in service.",
            "WebMobril was founded by Ajay Saraswat in 2014.",
            "The company is headquartered in Noida, India with offices in the USA and UK.",
            "Ajay Saraswat is the CEO and Founder of WebMobril.",
            "WebMobril offers web development, mobile app development, UI/UX design, digital marketing, and enterprise solutions."
        ]
        model = SentenceTransformer("all-MiniLM-L6-v2")
        embeddings = model.encode(texts)
        embeddings = np.array(embeddings)
        
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        # Initialize RAG engine with placeholder texts
        rag_engine = load_rag_engine(texts)
        
        print("Initialized with placeholder data")
        return True
    except Exception as e:
        print(f"Error initializing placeholder data: {e}")
        return False

def get_direct_answer(query):
    """Get direct answer for specific questions"""
    query_lower = query.lower().strip()
    
    # CEO questions - handle both "Ajay" and "Jay" variations
    if any(name in query_lower for name in ["ajay saraswat", "jay saraswat"]):
        return f"{COMPANY_FACTS['CEO']} is the CEO and Founder of WebMobril."
    
    if "who is the ceo" in query_lower or "ceo name" in query_lower or "chief executive" in query_lower or "who ceo" in query_lower:
        return f"The CEO of WebMobril is {COMPANY_FACTS['CEO']}."
    
    # Founder questions
    if "who is the founder" in query_lower or "founder name" in query_lower:
        return f"The founder of WebMobril is {COMPANY_FACTS['Founder']}."
    
    if "who founded" in query_lower or "who started" in query_lower:
        return f"WebMobril was founded by {COMPANY_FACTS['Founder']}."
    
    # Company information
    if "when was" in query_lower and ("founded" in query_lower or "started" in query_lower):
        return f"WebMobril was founded in {COMPANY_FACTS['Founded']}."
    
    if "how old" in query_lower and "company" in query_lower:
        return f"WebMobril has been in business since {COMPANY_FACTS['Founded']}."
    
    # Location questions
    if ("where" in query_lower and ("company" in query_lower or "located" in query_lower)) or "headquarters" in query_lower:
        return f"WebMobril is headquartered in {COMPANY_FACTS['Headquarters']} with offices in {', '.join(COMPANY_FACTS['Offices'])}."
    
    # Services questions
    if "what services" in query_lower or ("what does" in query_lower and "do" in query_lower):
        services = ", ".join(COMPANY_FACTS['Services'])
        return f"WebMobril offers {services}."
    
    # No direct answer found
    return None

def get_answer(query, top_k=3):
    """Get answer for a query using direct answers, RAG with Groq, or semantic search"""
    # First try to get a direct answer
    direct_answer = get_direct_answer(query)
    if direct_answer:
        return direct_answer
    
    # If RAG engine is available, use it
    global rag_engine
    if rag_engine:
        try:
            print("Using RAG with Groq to generate answer...")
            rag_answer = rag_engine.retrieve(query, top_k=top_k)
            if rag_answer and len(rag_answer) > 10:  # Ensure we got a meaningful answer
                return rag_answer
        except Exception as e:
            print(f"Error using RAG engine: {e}")
            print("Falling back to semantic search...")
    
    # If RAG failed or is not available, fall back to semantic search
    if model is None or index is None:
        load_data()
    
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
    
    # Format the answer
    if results:
        # Get the most relevant result only
        best_result = results[0]["text"]
        
        # Clean up the text - remove extra whitespace and newlines
        best_result = ' '.join(best_result.split())
        
        # If the result contains "Jay Saraswat" or "Ajay Saraswat" and is about CEO/founder
        if ("jay saraswat" in best_result.lower() or "ajay saraswat" in best_result.lower()) and \
           ("ceo" in best_result.lower() or "founder" in best_result.lower()):
            return f"{COMPANY_FACTS['CEO']} is the CEO and Founder of WebMobril."
        
        return best_result
    else:
        return "I don't have information on that topic."

# Initialize when imported
load_data()