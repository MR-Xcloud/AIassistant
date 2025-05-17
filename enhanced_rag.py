"""
Enhanced RAG (Retrieval-Augmented Generation) implementation.
This module combines multiple data sources for better answer generation.
"""

import os
import requests
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
from company_facts import COMPANY_FACTS
from company_products import COMPANY_PRODUCTS, get_product_info, get_project_info, get_all_products_summary

# Groq API credentials
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class EnhancedRAG:
    def __init__(self, texts=None, model=None):
        """Initialize the RAG engine with texts and model"""
        self.texts = texts or []
        self.model = model or SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = None
        self.index = None
        
        # If texts are provided, compute embeddings
        if self.texts:
            self._compute_embeddings()
    
    def _compute_embeddings(self):
        """Compute embeddings for all texts"""
        if not self.texts:
            return
        
        print("Computing embeddings for RAG engine...")
        self.embeddings = self.model.encode(self.texts, show_progress_bar=True)
        
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(self.embeddings)
        
        print(f"Computed embeddings for {len(self.texts)} texts")
    
    def set_texts(self, texts):
        """Set or update the texts and recompute embeddings"""
        self.texts = texts
        self._compute_embeddings()
    
    def _search_person_info(self, name):
        """Search for information about a specific person in the texts"""
        if not self.texts or not self.embeddings is not None or not self.index:
            return None
            
        # Create a query to search for the person
        query = f"Who is {name}? What is {name}'s role?"
        
        # Encode the query
        query_embedding = self.model.encode([query])
        
        # Search in the index
        distances, indices = self.index.search(query_embedding, 5)  # Get top 5 results
        
        # Get the most relevant texts
        relevant_texts = [self.texts[i] for i in indices[0] if i < len(self.texts)]
        
        # Filter texts that mention the person
        person_texts = []
        for text in relevant_texts:
            if name.lower() in text.lower():
                person_texts.append(text)
        
        if person_texts:
            # Extract the most relevant information
            for text in person_texts:
                # Look for sentences containing the person's name
                sentences = text.split('.')
                for sentence in sentences:
                    if name.lower() in sentence.lower():
                        # Clean up the sentence
                        clean_sentence = sentence.strip()
                        if clean_sentence:
                            return clean_sentence
            
            # If no good sentence found, return the first text
            return person_texts[0]
        
        return None
    
    def _get_direct_answer(self, query):
        """Get direct answer for specific questions"""
        query_lower = query.lower().strip()
        
        # Person-specific questions
        if "ajay saraswat" in query_lower:
            return f"{COMPANY_FACTS['CEO']} is the CEO and Founder of WebMobril."
        
        if "jay saraswat" in query_lower:
            # Search for information about Jay Saraswat in the texts
            jay_info = self._search_person_info("Jay Saraswat")
            if jay_info:
                return jay_info
            return "Jay Saraswat is the Founder & CEO at WebMobril."
        
        if "ravi saraswat" in query_lower:
            return f"Ravi Saraswat is the {COMPANY_FACTS['COO']} (Chief Operating Officer) at WebMobril."
        
        # Leadership questions
        if "who is the ceo" in query_lower or "ceo name" in query_lower or "chief executive" in query_lower:
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
        if ("where" in query_lower and ("company" in query_lower or "located" in query_lower)) or "headquarters" in query_lower or "address" in query_lower:
            return f"WebMobril is headquartered in {COMPANY_FACTS['Headquarters']} with offices in {', '.join(COMPANY_FACTS['Offices'])}. The full address is {COMPANY_FACTS['Address']}."
        
        # Services questions
        if "what services" in query_lower or ("what does" in query_lower and "do" in query_lower):
            services = ", ".join(COMPANY_FACTS['Services'])
            return f"WebMobril offers {services}."
        
        # Product questions
        if "what products" in query_lower or "products developed" in query_lower or "products created" in query_lower:
            products = get_all_products_summary()
            return f"WebMobril has developed products including: {products}."
        
        # Check for specific product questions
        for product in COMPANY_PRODUCTS["Products"]:
            if product["name"].lower() in query_lower:
                return f"{product['name']} is a {product['type']} developed by WebMobril for the {product['industry']} industry. {product['description']}"
        
        # No direct answer found
        return None
    
    def retrieve(self, query, top_k=5):
        """Retrieve the most relevant texts for a query"""
        # First check for hardcoded answers
        direct_answer = self._get_direct_answer(query)
        if direct_answer:
            return direct_answer
        
        if not self.texts or not self.embeddings is not None or not self.index:
            return "I don't have enough information to answer that question."
        
        # Encode the query
        query_embedding = self.model.encode([query])
        
        # Calculate cosine similarity
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Get top-k indices
        top_indices = indices[0]
        
        # Get the most relevant texts
        relevant_texts = [self.texts[i] for i in top_indices if i < len(self.texts)]
        
        # Process the retrieved texts to generate a coherent answer
        return self._generate_answer(query, relevant_texts)
    
    def _generate_answer(self, query, relevant_texts):
        """Generate an answer using Groq or fallback to simple extraction"""
        if not relevant_texts:
            return "I don't have information on that topic."
            
        try:
            return self._generate_with_groq(query, relevant_texts)
        except Exception as e:
            print(f"Error generating with Groq: {e}")
            # Fallback to simple extraction
            return self._simple_extract_answer(query, relevant_texts)
    
    def _generate_with_groq(self, query, relevant_texts):
        """Generate an answer using Groq API with retrieved context"""
        try:
            # Prepare context from retrieved texts
            context = "\n\n".join(relevant_texts)
            
            # Prepare the prompt
            prompt = f"""Answer the following question based on the provided context. 
            Be concise and direct. If the answer is not in the context, say "I don't have information on that topic."
            
            Context:
            {context}
            
            Question: {query}
            
            Answer:"""
            
            # Prepare the API request
            headers = {
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "llama3-8b-8192",  # Using Llama 3 8B model
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that provides concise, accurate answers based on the given context."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "max_tokens": 150
            }
            
            # Make the API request
            response = requests.post(GROQ_API_URL, headers=headers, data=json.dumps(data))
            response.raise_for_status()
            
            # Extract the answer
            result = response.json()
            answer = result["choices"][0]["message"]["content"].strip()
            
            return answer
            
        except Exception as e:
            print(f"Error generating answer with Groq: {e}")
            raise e
    
    def _simple_extract_answer(self, query, relevant_texts):
        """Simple answer extraction as fallback"""
        # Check if query is about a specific person
        query_lower = query.lower()
        for name in ["jay saraswat", "ajay saraswat", "ravi saraswat"]:
            if name in query_lower:
                # Look for sentences containing the person's name
                for text in relevant_texts:
                    sentences = text.split('.')
                    for sentence in sentences:
                        if name in sentence.lower():
                            clean_sentence = sentence.strip()
                            if clean_sentence:
                                return clean_sentence
        
        # Just return the most relevant text
        best_text = relevant_texts[0]
        
        # If the text is too long, try to extract the most relevant sentence
        if len(best_text) > 150:
            sentences = [s.strip() for s in best_text.split('.') if len(s.strip()) > 10]
            
            # Try to find a sentence that contains keywords from the query
            query_keywords = set(query.lower().split())
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(keyword in sentence_lower for keyword in query_keywords):
                    return sentence + "."
            
            # If no good match, return the first substantial sentence
            if sentences:
                return sentences[0] + "."
        
        return best_text

def load_enhanced_rag(texts):
    """Load and initialize the enhanced RAG engine with texts"""
    rag = EnhancedRAG()
    rag.set_texts(texts)
    return rag