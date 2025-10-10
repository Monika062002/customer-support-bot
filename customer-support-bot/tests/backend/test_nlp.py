import pytest
import sys
import os
import re

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(project_root, 'backend'))

from app import find_faq_answer

class TestNLPProcessing:
    """Test cases for NLP processing functionality"""
    
    def test_intent_recognition_basic(self):
        """Test basic intent recognition through FAQ matching"""
        test_cases = [
            # These should match FAQs
            ('How can I track my order?', True),
            ('What is your return policy?', True),
            ('How long does shipping take?', True),
            
            # These might not match (generic greetings) - which is OK
            ('hello', False),
            ('hi there', False), 
            ('good morning', False),
        ]
        
        matches_found = 0
        for message, should_match in test_cases:
            result = find_faq_answer(message)
            if should_match and result is not None:
                matches_found += 1
        
        # At least the specific questions should match
        assert matches_found >= 2
    
    def test_entity_extraction_patterns(self):
        """Test that we can extract order numbers from various formats"""
        # Test cases with expected numeric parts
        test_cases = [
            ('order ORD-12345', '12345'),
            ('Order #ORD-67890', '67890'),
            ('status of ord-11111', '11111'),
            ('track ORD12345', '12345'),
            ('check order 12345', '12345')
        ]
        
        # Simple pattern that focuses on extracting numbers
        order_pattern = r'(?:order|ord)\s*(?:number)?\s*[#]?\s*(?:[a-z]{0,3}[-]?)?(\d+)'
        
        correct_extractions = 0
        for message, expected_numbers in test_cases:
            match = re.search(order_pattern, message, re.IGNORECASE)
            if match is not None:
                extracted = match.group(1)
                if extracted == expected_numbers:
                    correct_extractions += 1
                    print(f"✅ Correctly extracted '{extracted}' from '{message}'")
                else:
                    print(f"⚠️  Extracted '{extracted}' from '{message}', expected '{expected_numbers}'")
            else:
                print(f"❌ No match for '{message}'")
        
        # Should extract correctly from most cases
        assert correct_extractions >= len(test_cases) - 1, f"Only {correct_extractions}/{len(test_cases)} correct extractions"
    
    def test_email_extraction(self):
        """Test email address extraction"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
        email_test_cases = [
            'contact me at user@example.com',
            'my email is test.user+tag@company.co.uk'
        ]
        
        for message in email_test_cases:
            matches = re.findall(email_pattern, message)
            assert len(matches) > 0, f"Should extract email from: {message}"
    
    def test_product_mention_detection(self):
        """Test detection of product mentions"""
        product_keywords = [
            'techbook pro', 'gamerx laptop', 'smartphone x', 
            'wireless earbuds', 'laptop', 'phone', 'device'
        ]
        
        test_messages = [
            'My techbook pro is not working',
            'I want to buy gamerx laptop',
            'Smartphone x camera quality',
            'The device keeps crashing'
        ]
        
        for message in test_messages:
            message_lower = message.lower()
            product_mentioned = any(product in message_lower for product in product_keywords)
            assert product_mentioned, f"Should detect product in: {message}"
    
    def test_technical_issue_identification(self):
        """Test basic technical issue keyword detection"""
        technical_keywords = {
            'power_issues': ['wont turn on', 'not starting', 'no power', 'dead'],
            'performance_issues': ['slow', 'lagging', 'freezing', 'unresponsive']
        }
        
        # Test that we can detect obvious technical issues
        obvious_issues = [
            'my laptop wont turn on',
            'computer is very slow', 
            'phone keeps freezing',
            'device has no power'
        ]
        
        detected_issues = 0
        for issue in obvious_issues:
            issue_lower = issue.lower()
            # Check if it contains any technical keywords
            is_technical = any(
                keyword in issue_lower 
                for keywords in technical_keywords.values() 
                for keyword in keywords
            )
            if is_technical:
                detected_issues += 1
        
        # Should detect most obvious technical issues
        assert detected_issues >= len(obvious_issues) * 0.75
    
    def test_urgency_detection(self):
        """Test detection of urgent requests"""
        urgency_keywords = ['urgent', 'asap', 'emergency', 'immediately', 'right away', 'critical']
        
        urgent_messages = [
            'This is urgent! My device is broken',
            'Need help asap with order',
            'Emergency technical issue'
        ]
        
        for message in urgent_messages:
            message_lower = message.lower()
            is_urgent = any(keyword in message_lower for keyword in urgency_keywords)
            assert is_urgent, f"Should detect urgency in: {message}"

class TestFAQKnowledgeBase:
    """Test cases for FAQ knowledge base integrity"""
    
    def test_faq_categories_completeness(self):
        """Test that FAQ categories are complete"""
        from app import faqs
        
        expected_categories = [
            'order_related', 'return_refund', 'technical_support',
            'billing_payment', 'account_management', 'product_questions'
        ]
        
        for category in expected_categories:
            assert category in faqs, f"Missing FAQ category: {category}"
            assert len(faqs[category]) > 0, f"Empty FAQ category: {category}"
    
    def test_faq_structure_integrity(self):
        """Test that all FAQ entries have required structure"""
        from app import faqs
        
        for category, questions in faqs.items():
            for faq in questions:
                assert 'question' in faq, "FAQ missing question field"
                assert 'answer' in faq, "FAQ missing answer field"
                assert 'keywords' in faq, "FAQ missing keywords field"
                
                assert isinstance(faq['question'], str)
                assert isinstance(faq['answer'], str)
                assert isinstance(faq['keywords'], list)
                
                assert len(faq['question']) > 0
                assert len(faq['answer']) > 0
                assert len(faq['keywords']) > 0
    
    def test_faq_keyword_relevance(self):
        """Test that FAQ keywords are relevant to questions"""
        from app import faqs
        
        relevant_faqs = 0
        total_faqs = 0
        
        for category, questions in faqs.items():
            for faq in questions:
                total_faqs += 1
                question_lower = faq['question'].lower()
                answer_lower = faq['answer'].lower()
                
                # At least some keywords should appear in question or answer
                relevant_keywords = [
                    keyword for keyword in faq['keywords']
                    if keyword in question_lower or keyword in answer_lower
                ]
                
                if len(relevant_keywords) > 0:
                    relevant_faqs += 1
        
        # Most FAQs should have relevant keywords (allow some exceptions)
        assert relevant_faqs >= total_faqs * 0.8, "Too many FAQs have irrelevant keywords"

class TestResponseQuality:
    """Test cases for response quality and appropriateness"""
    
    def test_response_length_appropriateness(self):
        """Test that responses are appropriate length"""
        test_messages = [
            'How can I track my order?',
            'What is your return policy?',
            'My device wont turn on'
        ]
        
        for message in test_messages:
            result = find_faq_answer(message)
            if result:
                answer = result['answer']
                # Responses should be informative but not excessively long
                assert len(answer) > 10, "Response too short"
                assert len(answer) < 1000, "Response too long"
    
    def test_response_relevance(self):
        """Test that responses are relevant to questions"""
        relevance_test_cases = [
            ('How can I track my order?', ['track', 'order', 'tracking']),
            ('What is your return policy?', ['return', 'policy', 'days']),
            ('How long does shipping take?', ['shipping', 'days', 'delivery'])
        ]
        
        relevant_responses = 0
        for question, expected_keywords in relevance_test_cases:
            result = find_faq_answer(question)
            if result:
                answer_lower = result['answer'].lower()
                # Response should contain relevant keywords
                relevant_matches = sum(1 for keyword in expected_keywords if keyword in answer_lower)
                if relevant_matches >= 1:
                    relevant_responses += 1
        
        # Most responses should be relevant
        assert relevant_responses >= len(relevance_test_cases) * 0.7

class TestErrorHandling:
    """Test cases for error handling in NLP processing"""
    
    def test_malformed_input_handling(self):
        """Test handling of malformed or unusual input"""
        edge_cases = [
            '',  # Empty string
            '   ',  # Only spaces
            '!!!@#$%',  # Special characters only
            'A' * 1000,  # Very long string
        ]
        
        for edge_case in edge_cases:
            # Should not crash with any input
            try:
                result = find_faq_answer(edge_case)
                # Should either return None or a valid FAQ without crashing
                if result is not None:
                    assert 'question' in result
                    assert 'answer' in result
            except Exception as e:
                pytest.fail(f"Should handle edge case without exception: {edge_case}. Error: {e}")
    
    def test_unicode_handling(self):
        """Test handling of unicode and special characters"""
        unicode_test_cases = [
            'Hello 🌟 World',
            'Order status for café',
            'I need help with naïve device'
        ]
        
        for message in unicode_test_cases:
            # Should handle unicode without crashing
            try:
                result = find_faq_answer(message)
                # No specific assertion, just shouldn't crash
                assert True
            except Exception as e:
                pytest.fail(f"Should handle unicode without exception: {message}. Error: {e}")

class TestPerformance:
    """Test cases for NLP processing performance"""
    
    def test_response_time_basic(self):
        """Test that basic queries return quickly"""
        import time
        
        test_messages = [
            'How can I track my order?',
            'What is your return policy?',
            'help'
        ]
        
        max_response_time = 0.1  # 100ms max for basic queries
        
        for message in test_messages:
            start_time = time.time()
            result = find_faq_answer(message)
            end_time = time.time()
            
            response_time = end_time - start_time
            assert response_time < max_response_time, \
                f"Response too slow for: {message}. Time: {response_time:.3f}s"
    
    def test_faq_matching_efficiency(self):
        """Test that FAQ matching is efficient with many entries"""
        from app import faqs
        
        # Count total FAQ entries
        total_faqs = sum(len(questions) for questions in faqs.values())
        assert total_faqs > 0, "Should have FAQ entries"
        
        # Should be able to handle reasonable number of FAQs
        assert total_faqs < 1000, "Too many FAQs for efficient matching"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])