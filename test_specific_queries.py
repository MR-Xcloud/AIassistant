"""
Test script for specific query types to verify the improved answer extraction.
This script tests the get_answer function with various specific query types
to ensure it returns concise, relevant answers.
"""

from chatbot import get_answer, load_data

def test_queries():
    """Test various specific query types"""
    print("=" * 60)
    print("🧪 TESTING SPECIFIC QUERY TYPES")
    print("=" * 60)
    
    # Make sure data is loaded
    load_data()
    
    # Define test queries
    test_cases = [
        {
            "category": "CEO Questions",
            "queries": [
                "Who is the CEO?",
                "What is the name of the CEO?",
                "Who is the Chief Executive Officer?",
                "Tell me about the CEO"
            ]
        },
        {
            "category": "Founder Questions",
            "queries": [
                "Who founded the company?",
                "Who is the founder?",
                "When was the company founded?",
                "Tell me about the founder"
            ]
        },
        {
            "category": "Location Questions",
            "queries": [
                "Where is the company located?",
                "What is the company's address?",
                "Where are the headquarters?",
                "Where is the office?"
            ]
        },
        {
            "category": "Service Questions",
            "queries": [
                "What services do you offer?",
                "What does the company do?",
                "Tell me about your services",
                "What solutions do you provide?"
            ]
        }
    ]
    
    # Test each query and print results
    for case in test_cases:
        print(f"\n📋 {case['category']}:")
        print("-" * 60)
        
        for query in case["queries"]:
            print(f"Q: {query}")
            answer = get_answer(query)
            print(f"A: {answer}")
            print("-" * 60)
    
    print("\n✅ Testing completed!")

if __name__ == "__main__":
    test_queries()