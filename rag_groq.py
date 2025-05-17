"""
RAG (Retrieval-Augmented Generation) implementation using Groq.
This module enhances answer quality by combining retrieval with Groq's LLM capabilities.
"""

import os
import requests
import json
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
from company_facts import COMPANY_FACTS

# Groq API credentials
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class RAGGroq:
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
    
    def retrieve(self, query, top_k=3):
        """Retrieve the most relevant texts for a query"""
        # Check for direct answers first
        direct_answer = self._get_direct_answer(query)
        if direct_answer:
            return direct_answer
            
        if not self.texts or self.embeddings is None or self.index is None:
            return "I don't have enough information to answer that question."
        
        # Encode the query
        query_embedding = self.model.encode([query])
        
        # Search in the index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Get the most relevant texts
        relevant_texts = [self.texts[i] for i in indices[0] if i < len(self.texts)]
        
        if not relevant_texts:
            return "I don't have information on that topic."
            
        # Generate answer using Groq
        return self._generate_with_groq(query, relevant_texts)
    
    def _get_direct_answer(self, query):
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
            # Fall back to the most relevant text
            return relevant_texts[0] if relevant_texts else "I couldn't generate an answer at this time."

def load_rag_engine(texts):
    """Load and initialize the RAG engine with texts"""
    rag = RAGGroq()
    rag.set_texts(texts)
    return rag