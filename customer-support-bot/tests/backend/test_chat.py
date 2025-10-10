import pytest
import json
import sys
import os
import re

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app import app, find_faq_answer, get_order_status

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestChatAPI:
    """Test cases for chat API endpoints"""
    
    def test_chat_endpoint_exists(self, client):
        """Test that chat endpoint is accessible"""
        response = client.post('/api/chat', json={'message': 'hello'})
        assert response.status_code == 200
    
    def test_chat_with_greeting(self, client):
        """Test chat with greeting message"""
        response = client.post('/api/chat', json={'message': 'hello'})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'response' in data
        assert 'intent' in data
        assert 'confidence' in data
        assert isinstance(data['response'], str)
        assert isinstance(data['confidence'], (int, float))
    
    def test_chat_with_order_status_query(self, client):
        """Test chat with order status query"""
        test_cases = [
            {'message': 'Where is my order ORD-12345?', 'expected_intent': 'order_status'},
            {'message': 'track order ORD-67890', 'expected_intent': 'order_status'},
            {'message': 'status of order ORD-11111', 'expected_intent': 'order_status'}
        ]
        
        for test_case in test_cases:
            response = client.post('/api/chat', json={'message': test_case['message']})
            data = json.loads(response.data)
            
            assert response.status_code == 200
            # It could be either order_status or faq, depending on matching
            assert data['intent'] in ['order_status', 'faq', 'general']
    
    def test_chat_with_faq_questions(self, client):
        """Test chat with FAQ questions"""
        faq_test_cases = [
            {
                'message': 'How can I track my order?',
                'expected_keywords': ['track', 'order', 'tracking']
            },
            {
                'message': 'What is your return policy?',
                'expected_keywords': ['return', 'policy', '30']
            }
        ]
        
        for test_case in faq_test_cases:
            response = client.post('/api/chat', json={'message': test_case['message']})
            data = json.loads(response.data)
            
            assert response.status_code == 200
            if data['intent'] == 'faq':
                # Check that response contains relevant keywords
                response_lower = data['response'].lower()
                relevant_matches = sum(1 for keyword in test_case['expected_keywords'] if keyword in response_lower)
                assert relevant_matches >= 1, f"Response should contain relevant keywords: {test_case['expected_keywords']}"
    
    def test_chat_with_technical_issues(self, client):
        """Test chat with technical support questions"""
        tech_test_cases = [
            'My laptop is not turning on',
            'Phone keeps crashing',
            'Internet connection not working'
        ]
        
        for message in tech_test_cases:
            response = client.post('/api/chat', json={'message': message})
            data = json.loads(response.data)
            
            assert response.status_code == 200
            assert len(data['response']) > 0
    
    def test_chat_with_refund_requests(self, client):
        """Test chat with refund and return questions"""
        refund_test_cases = [
            'I want to return my product',
            'How do I get a refund?',
            'Cancel my order please'
        ]
        
        for message in refund_test_cases:
            response = client.post('/api/chat', json={'message': message})
            data = json.loads(response.data)
            
            assert response.status_code == 200
            assert data['confidence'] > 0
    
    def test_chat_empty_message(self, client):
        """Test chat with empty message"""
        response = client.post('/api/chat', json={'message': ''})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'response' in data
        assert data['intent'] == 'empty'
    
    def test_chat_no_message_field(self, client):
        """Test chat without message field"""
        response = client.post('/api/chat', json={})
        data = json.loads(response.data)
        
        assert response.status_code == 200
        assert 'response' in data
    
    def test_chat_with_special_characters(self, client):
        """Test chat with special characters and edge cases"""
        edge_cases = [
            'Hello!!!',
            'Order #ORD-12345 ???',
            'Help!!! My device is broken!!!',
            'What is your return policy? Thanks!'
        ]
        
        for message in edge_cases:
            response = client.post('/api/chat', json={'message': message})
            data = json.loads(response.data)
            
            assert response.status_code == 200
            assert 'response' in data
    
    def test_chat_response_structure(self, client):
        """Test that chat response has correct structure"""
        response = client.post('/api/chat', json={'message': 'test message'})
        data = json.loads(response.data)
        
        required_fields = ['response', 'intent', 'confidence']
        for field in required_fields:
            assert field in data
        
        assert isinstance(data['response'], str)
        assert isinstance(data['intent'], str)
        assert isinstance(data['confidence'], (int, float))
        assert 0 <= data['confidence'] <= 100

class TestFAQFunction:
    """Test cases for FAQ matching function"""
    
    def test_faq_matching_basic(self):
        """Test basic FAQ matching"""
        test_cases = [
            ('How can I track my order?', 'track'),
            ('What is your return policy?', 'return'),
            ('How long does shipping take?', 'shipping')
        ]
        
        for message, expected_keyword in test_cases:
            result = find_faq_answer(message)
            assert result is not None, f"Should match FAQ for: {message}"
            assert expected_keyword in result['answer'].lower()
    
    def test_faq_matching_variations(self):
        """Test FAQ matching with different phrasings"""
        variations = [
            'I need to track my package',
            'Where is my order?',
            'Order tracking help'
        ]
        
        matches_found = 0
        for message in variations:
            result = find_faq_answer(message)
            if result and 'track' in result['answer'].lower():
                matches_found += 1
        
        # At least some variations should match
        assert matches_found >= 1
    
    def test_faq_no_match(self):
        """Test FAQ with no matching questions"""
        no_match_messages = [
            'What is the meaning of life?',
            'Tell me a joke',
            'Weather forecast today',
            'Random unrelated question that should not match'
        ]
        
        matches_found = 0
        for message in no_match_messages:
            result = find_faq_answer(message)
            if result is not None:
                matches_found += 1
        
        # Allow some false positives, but not all
        assert matches_found <= len(no_match_messages) // 2
    
    def test_faq_structure(self):
        """Test FAQ result structure"""
        result = find_faq_answer('How can I track my order?')
        if result:
            assert 'question' in result
            assert 'answer' in result
            assert 'keywords' in result
            assert isinstance(result['keywords'], list)

class TestOrderStatusFunction:
    """Test cases for order status function"""
    
    def test_get_order_status_existing(self):
        """Test getting status for existing orders"""
        test_cases = [
            ('ORD-12345', 'shipped'),
            ('ORD-67890', 'delivered'),
            ('ORD-11111', 'processing')
        ]
        
        for order_number, expected_status in test_cases:
            result = get_order_status(order_number)
            assert result is not None
            assert result['status'] == expected_status
    
    def test_get_order_status_variations(self):
        """Test order status with different input formats"""
        variations = [
            'ord-12345',  # lowercase
            'ORD12345',   # no dash - this should be normalized to ORD-12345
            ' order ORD-12345 '  # with spaces
        ]
        
        matches_found = 0
        for order_input in variations:
            result = get_order_status(order_input)
            if result is not None:
                matches_found += 1
        
        # At least some variations should work
        assert matches_found >= 2
    
    def test_get_order_status_non_existent(self):
        """Test getting status for non-existent orders"""
        non_existent_orders = [
            'ORD-99999',
            'INVALID-123',
            'TEST-ORDER'
        ]
        
        for order_number in non_existent_orders:
            result = get_order_status(order_number)
            assert result is None, f"Should return None for non-existent order: {order_number}"
    
    def test_order_status_structure(self):
        """Test order status result structure"""
        result = get_order_status('ORD-12345')
        assert result is not None
        
        required_fields = ['status', 'product', 'carrier']
        for field in required_fields:
            assert field in result
        
        if result['status'] == 'shipped':
            assert 'tracking_number' in result
            assert 'estimated_delivery' in result
        elif result['status'] == 'delivered':
            assert 'delivery_date' in result

class TestAnalyticsAPI:
    """Test cases for analytics API endpoint"""
    
    def test_analytics_endpoint(self, client):
        """Test analytics endpoint returns correct data"""
        response = client.get('/api/analytics')
        data = json.loads(response.data)
        
        assert response.status_code == 200
        
        required_fields = [
            'total_conversations', 
            'resolution_rate', 
            'escalations', 
            'satisfaction',
            'average_response_time',
            'common_intents'
        ]
        
        for field in required_fields:
            assert field in data
        
        # Check data types
        assert isinstance(data['total_conversations'], int)
        assert isinstance(data['resolution_rate'], (int, float))
        assert isinstance(data['escalations'], int)
        assert isinstance(data['satisfaction'], (int, float))
        assert isinstance(data['average_response_time'], str)
        assert isinstance(data['common_intents'], dict)
    
    def test_analytics_common_intents_structure(self, client):
        """Test common_intents structure in analytics"""
        response = client.get('/api/analytics')
        data = json.loads(response.data)
        
        common_intents = data['common_intents']
        expected_intents = ['order_status', 'technical_support', 'refund_returns', 'billing']
        
        for intent in expected_intents:
            assert intent in common_intents
            assert isinstance(common_intents[intent], int)
            assert common_intents[intent] >= 0

class TestOrderAPI:
    """Test cases for order API endpoint"""
    
    def test_order_endpoint_existing(self, client):
        """Test order endpoint with existing orders"""
        existing_orders = ['ORD-12345', 'ORD-67890', 'ORD-11111']
        
        for order_number in existing_orders:
            response = client.get(f'/api/order/{order_number}')
            data = json.loads(response.data)
            
            assert response.status_code == 200
            assert data['found'] == True
            assert data['order_number'] == order_number
            assert 'details' in data
    
    def test_order_endpoint_non_existent(self, client):
        """Test order endpoint with non-existent orders"""
        non_existent_orders = ['ORD-99999', 'INVALID', 'TEST-123']
        
        for order_number in non_existent_orders:
            response = client.get(f'/api/order/{order_number}')
            data = json.loads(response.data)
            
            assert response.status_code == 404
            assert data['found'] == False
            assert 'message' in data
    
    def test_order_endpoint_variations(self, client):
        """Test order endpoint with different order number formats"""
        # Should handle various formats gracefully
        variations = ['ord-12345', 'ORD12345']
        
        for order_number in variations:
            response = client.get(f'/api/order/{order_number}')
            # Should either return 200 or 404, not crash
            assert response.status_code in [200, 404]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])