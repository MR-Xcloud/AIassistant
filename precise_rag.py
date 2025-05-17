"""
Precise RAG (Retrieval-Augmented Generation) implementation.
This module focuses on providing highly relevant answers to specific questions.
"""

import os
import requests
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import re
from company_facts import COMPANY_FACTS
from company_products import COMPANY_PRODUCTS, get_product_info, get_project_info, get_all_products_summary

# Groq API credentials
GROQ_API_KEY = "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"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

class PreciseRAG:
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
    
    def _classify_question(self, query):
        """Classify the question type to determine the best approach"""
        query_lower = query.lower().strip()
        
        # Person questions
        if any(name in query_lower for name in ["ajay saraswat", "jay saraswat", "ravi saraswat"]):
            return "person", re.findall(r'[a-z]+ saraswat', query_lower)[0]
        
        # Leadership questions
        if any(role in query_lower for role in ["ceo", "founder", "chief executive", "president", "director"]):
            return "leadership", None
        
        # Company information
        if "company" in query_lower or "webmobril" in query_lower:
            if "founded" in query_lower or "started" in query_lower:
                return "founding", None
            if "located" in query_lower or "address" in query_lower or "where" in query_lower:
                return "location", None
        
        # Products and services
        if any(term in query_lower for term in ["product", "service", "offer", "develop", "create"]):
            for product in COMPANY_PRODUCTS["Products"]:
                if product["name"].lower() in query_lower:
                    return "specific_product", product["name"]
            return "products_services", None
        
        # General question
        return "general", None
    
    def _get_hardcoded_answer(self, question_type, entity=None):
        """Get hardcoded answers for common questions"""
        if question_type == "person":
            if entity == "ajay saraswat":
                return f"{COMPANY_FACTS['CEO']} is the CEO and Founder of WebMobril."
            elif entity == "jay saraswat":
                return "Jay Saraswat is the Founder & CEO at WebMobril."
            elif entity == "ravi saraswat":
                return f"Ravi Saraswat is the {COMPANY_FACTS['COO']} (Chief Operating Officer) at WebMobril."
        
        elif question_type == "leadership":
            return f"The CEO of WebMobril is {COMPANY_FACTS['CEO']}. The company was founded by {COMPANY_FACTS['Founder']}."
        
        elif question_type == "founding":
            return f"WebMobril was founded in {COMPANY_FACTS['Founded']} by {COMPANY_FACTS['Founder']}."
        
        elif question_type == "location":
            return f"WebMobril is headquartered in {COMPANY_FACTS['Headquarters']} with offices in {', '.join(COMPANY_FACTS['Offices'])}. The full address is {COMPANY_FACTS['Address']}."
        
        elif question_type == "products_services":
            services = ", ".join(COMPANY_FACTS['Services'])
            return f"WebMobril offers {services}."
        
        elif question_type == "specific_product" and entity:
            product = get_product_info(entity)
            if product:
                return f"{product['name']} is a {product['type']} developed by WebMobril for the {product['industry']} industry. {product['description']}"
        
        return None
    
    def _retrieve_relevant_chunks(self, query, question_type, entity=None, top_k=5):
        """Retrieve the most relevant text chunks for a query"""
        if not self.texts or self.embeddings is None or self.index is None:
            return []
        
        # Create a more specific query based on question type
        enhanced_query = query
        if question_type == "person" and entity:
            enhanced_query = f"Who is {entity}? What is {entity}'s role at WebMobril?"
        elif question_type == "leadership":
            enhanced_query = "Who are the leaders of WebMobril? Who is the CEO and founder?"
        elif question_type == "founding":
            enhanced_query = "When was WebMobril founded? Who founded WebMobril?"
        elif question_type == "location":
            enhanced_query = "Where is WebMobril located? What is the address of WebMobril?"
        elif question_type == "products_services":
            enhanced_query = "What products and services does WebMobril offer?"
        elif question_type == "specific_product" and entity:
            enhanced_query = f"What is {entity}? Describe the {entity} product."
        
        # Encode the enhanced query
        query_embedding = self.model.encode([enhanced_query])
        
        # Search in the index
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Get the most relevant chunks
        relevant_chunks = [self.texts[i] for i in indices[0] if i < len(self.texts)]
        
        # Filter chunks based on question type
        filtered_chunks = []
        for chunk in relevant_chunks:
            chunk_lower = chunk.lower()
            
            # For person questions, only include chunks mentioning the person
            if question_type == "person" and entity and entity in chunk_lower:
                filtered_chunks.append(chunk)
            # For leadership questions, only include chunks mentioning leadership roles
            elif question_type == "leadership" and any(role in chunk_lower for role in ["ceo", "founder", "chief", "president", "director"]):
                filtered_chunks.append(chunk)
            # For founding questions, only include chunks mentioning founding
            elif question_type == "founding" and any(term in chunk_lower for term in ["founded", "started", "established", "beginning", "inception"]):
                filtered_chunks.append(chunk)
            # For location questions, only include chunks mentioning location
            elif question_type == "location" and any(term in chunk_lower for term in ["located", "address", "headquarters", "office"]):
                filtered_chunks.append(chunk)
            # For product/service questions, only include chunks mentioning products or services
            elif question_type == "products_services" and any(term in chunk_lower for term in ["product", "service", "offer", "develop", "create"]):
                filtered_chunks.append(chunk)
            # For specific product questions, only include chunks mentioning the product
            elif question_type == "specific_product" and entity and entity.lower() in chunk_lower:
                filtered_chunks.append(chunk)
            # For general questions, include all chunks
            elif question_type == "general":
                filtered_chunks.append(chunk)
        
        # If no chunks passed the filter, fall back to the original chunks
        if not filtered_chunks and relevant_chunks:
            return relevant_chunks[:3]  # Limit to top 3 for relevance
        
        return filtered_chunks[:3]  # Limit to top 3 for relevance
    
    def answer_question(self, query):
        """Answer a question using the precise RAG approach"""
        # Step 1: Classify the question
        question_type, entity = self._classify_question(query)
        print(f"Question type: {question_type}, Entity: {entity}")
        
        # Step 2: Check for hardcoded answers
        hardcoded_answer = self._get_hardcoded_answer(question_type, entity)
        if hardcoded_answer:
            return hardcoded_answer
        
        # Step 3: Retrieve relevant chunks
        relevant_chunks = self._retrieve_relevant_chunks(query, question_type, entity)
        
        if not relevant_chunks:
            return "I don't have information on that topic."
        
        # Step 4: Generate answer using Groq or fallback
        try:
            return self._generate_with_groq(query, relevant_chunks, question_type)
        except Exception as e:
            print(f"Error generating with Groq: {e}")
            return self._extract_precise_answer(query, relevant_chunks, question_type, entity)
    
    def _generate_with_groq(self, query, relevant_chunks, question_type):
        """Generate an answer using Groq API with retrieved context"""
        try:
            # Prepare context from retrieved chunks
            context = "\n\n".join(relevant_chunks)
            
            # Create a prompt based on question type
            system_prompt = "You are a helpful assistant that provides concise, accurate answers based on the given context."
            
            if question_type == "person":
                system_prompt += " Focus only on information about the specific person mentioned in the question."
            elif question_type == "leadership":
                system_prompt += " Focus only on information about the leadership team and their roles."
            elif question_type == "founding":
                system_prompt += " Focus only on information about when and how the company was founded."
            elif question_type == "location":
                system_prompt += " Focus only on information about the company's location and address."
            elif question_type == "products_services":
                system_prompt += " Focus only on information about the company's products and services."
            
            user_prompt = f"""Answer the following question based on the provided context. 
            Be concise and direct. Only include information that directly answers the question.
            If the answer is not in the context, say "I don't have information on that topic."
            
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
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2,  # Lower temperature for more focused answers
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
    
    def _extract_precise_answer(self, query, relevant_chunks, question_type, entity=None):
        """Extract a precise answer from relevant chunks as a fallback"""
        query_lower = query.lower()
        
        # For person questions, look for sentences containing the person's name
        if question_type == "person" and entity:
            for chunk in relevant_chunks:
                sentences = chunk.split('.')
                for sentence in sentences:
                    if entity in sentence.lower():
                        clean_sentence = sentence.strip()
                        if clean_sentence:
                            return clean_sentence + "."
        
        # For other question types, look for sentences containing keywords
        keywords = []
        if question_type == "leadership":
            keywords = ["ceo", "founder", "chief", "president", "director"]
        elif question_type == "founding":
            keywords = ["founded", "started", "established", "beginning", "inception"]
        elif question_type == "location":
            keywords = ["located", "address", "headquarters", "office"]
        elif question_type == "products_services":
            keywords = ["product", "service", "offer", "develop", "create"]
        
        if keywords:
            for chunk in relevant_chunks:
                sentences = chunk.split('.')
                for sentence in sentences:
                    sentence_lower = sentence.lower()
                    if any(keyword in sentence_lower for keyword in keywords):
                        clean_sentence = sentence.strip()
                        if clean_sentence:
                            return clean_sentence + "."
        
        # If no specific sentence found, return the most relevant chunk
        best_chunk = relevant_chunks[0]
        
        # If the chunk is too long, extract the most relevant sentence
        if len(best_chunk) > 150:
            sentences = [s.strip() for s in best_chunk.split('.') if len(s.strip()) > 10]
            
            # Try to find a sentence that contains keywords from the query
            query_words = set(query_lower.split())
            for sentence in sentences:
                sentence_lower = sentence.lower()
                if any(word in sentence_lower for word in query_words if len(word) > 3):
                    return sentence + "."
            
            # If no good match, return the first substantial sentence
            if sentences:
                return sentences[0] + "."
        
        return best_chunk

def load_precise_rag(texts):
    """Load and initialize the precise RAG engine with texts"""
    rag = PreciseRAG()
    rag.set_texts(texts)
    return rag