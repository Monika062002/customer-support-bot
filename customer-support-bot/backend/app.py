from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import re
import random
import os

app = Flask(__name__)
CORS(app)

# Base directory for backend
base_dir = os.path.dirname(__file__)
knowledge_base_path = os.path.join(base_dir, 'data', 'knowledge_base.json')
faqs_path = os.path.join(base_dir, 'data', 'faqs.json')

# Load enhanced datasets using absolute paths
try:
    with open(knowledge_base_path, 'r') as f:
        knowledge_base = json.load(f)
    print("✅ Knowledge base loaded successfully")
except FileNotFoundError:
    print("❌ knowledge_base.json not found")
    knowledge_base = {}

try:
    with open(faqs_path, 'r') as f:
        faqs = json.load(f)
    print("✅ FAQs loaded successfully")
except FileNotFoundError:
    print("❌ faqs.json not found")
    faqs = {}

# Sample order database (in real app, this would be a real database)
sample_orders = {
    "ORD-12345": {
        "status": "shipped",
        "product": "TechBook Pro TB2024",
        "carrier": "UPS",
        "tracking_number": "1Z999AA10123456784",
        "estimated_delivery": "2024-01-15",
        "shipping_address": "123 Main St, City, State 12345"
    },
    "ORD-67890": {
        "status": "delivered", 
        "product": "SmartPhone X SPX13",
        "carrier": "FedEx",
        "tracking_number": "789012345678",
        "delivery_date": "2024-01-10",
        "shipping_address": "456 Oak Ave, City, State 12345"
    },
    "ORD-11111": {
        "status": "processing",
        "product": "Wireless Earbuds WE300",
        "carrier": "USPS",
        "estimated_delivery": "2024-01-18",
        "shipping_address": "789 Pine Rd, City, State 12345"
    }
}

def find_faq_answer(message):
    """Find the best FAQ match for a user message"""
    message_lower = message.lower().strip()
    
    # Don't match very short or generic messages
    if len(message_lower) < 3 or message_lower in ['hello', 'hi', 'hey']:
        return None
    
    best_match = None
    highest_score = 0
    
    for category, questions in faqs.items():
        for faq in questions:
            score = 0
            
            # Check for exact phrase matches (higher weight)
            question_words = faq['question'].lower().split()
            if len(question_words) > 3:
                # Check if significant portion of question is in message
                matching_words = sum(1 for word in question_words[:5] if word in message_lower)
                if matching_words >= 2:
                    score += 3
            
            # Check keyword matches
            keyword_matches = 0
            for keyword in faq.get('keywords', []):
                if keyword in message_lower:
                    keyword_matches += 1
                    score += 1
            
            # Boost score if we have multiple keyword matches
            if keyword_matches >= 2:
                score += 2
            
            # Penalize if message is very different from question
            question_similarity = len(set(message_lower.split()) & set(faq['question'].lower().split()))
            if question_similarity < 1:
                score -= 2
            
            if score > highest_score and score >= 2:  # Minimum threshold
                highest_score = score
                best_match = faq
    
    return best_match

def get_order_status(order_number):
    """Get order status from database"""
    if not order_number:
        return None
        
    # Clean and normalize order number
    clean_order = order_number.upper().strip()
    
    # Remove common prefixes and clean up
    clean_order = re.sub(r'^(ORDER|ORD|#)\s*', '', clean_order)
    clean_order = clean_order.replace(' ', '')
    
    # Ensure it has the ORD- prefix
    if not clean_order.startswith('ORD-'):
        # If it's just numbers, add ORD- prefix
        if clean_order.isdigit():
            clean_order = f"ORD-{clean_order}"
        else:
            # If it has numbers but no prefix, try to format it
            match = re.search(r'(\d+)', clean_order)
            if match:
                clean_order = f"ORD-{match.group(1)}"
            else:
                # If no numbers found, it's invalid
                return None
    
    return sample_orders.get(clean_order, None)

# ========== ROUTES ==========

@app.route('/')
def home():
    """Root endpoint - shows API is working"""
    return jsonify({
        'message': '🤖 Customer Support Bot API is running!',
        'status': 'active',
        'endpoints': {
            'test': '/api/test (GET)',
            'chat': '/api/chat (POST)',
            'analytics': '/api/analytics (GET)',
            'order': '/api/order/<order_number> (GET)'
        },
        'example_usage': {
            'chat': 'POST /api/chat with {"message": "your question"}',
            'test_order': 'GET /api/order/ORD-12345'
        }
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        'status': 'success',
        'message': '✅ Backend API is working correctly!',
        'timestamp': '2024-01-10 01:29:22'
    })

@app.route('/api/chat', methods=['POST', 'GET'])
def chat():
    """Main chat endpoint - handles user messages"""
    if request.method == 'GET':
        return jsonify({
            'message': 'Use POST method to send chat messages',
            'example': 'POST /api/chat with {"message": "Hello"}'
        })
    
    data = request.get_json()
    if not data:
        return jsonify({
            'response': 'Please provide JSON data with a message',
            'intent': 'error',
            'confidence': 0
        })
    
    user_message = data.get('message', '').strip()
    
    # Don't process empty messages
    if not user_message:
        return jsonify({
            'response': 'Please type a message so I can help you.',
            'intent': 'empty',
            'confidence': 0
        })
    
    # Check for order status query first (before FAQ)
    order_match = re.search(r'(?:order|ord)\s*(?:number)?\s*[#]?\s*([a-z0-9]{3,}-?[a-z0-9]+)', user_message, re.IGNORECASE)
    if order_match:
        order_number = order_match.group(1)
        order_info = get_order_status(order_number)
        if order_info:
            if order_info['status'] == 'shipped':
                response_text = f"Order {order_number} is shipped via {order_info['carrier']}. "
                response_text += f"Tracking: {order_info['tracking_number']}. "
                response_text += f"Estimated delivery: {order_info['estimated_delivery']}."
            elif order_info['status'] == 'delivered':
                response_text = f"Order {order_number} was delivered on {order_info['delivery_date']}. "
                response_text += f"Product: {order_info['product']}"
            else:
                response_text = f"Order {order_number} is {order_info['status']}. "
                response_text += f"Estimated delivery: {order_info['estimated_delivery']}."
            
            response = {
                'response': response_text,
                'intent': 'order_status',
                'confidence': 90,
                'order_info': order_info
            }
            return jsonify(response)
    
    # Try to find FAQ match
    faq_match = find_faq_answer(user_message)
    if faq_match:
        response = {
            'response': faq_match['answer'],
            'intent': 'faq',
            'confidence': 85,
            'source': 'faq_database',
            'faq_question': faq_match['question']
        }
        return jsonify(response)
    
    # Default AI response for unrecognized messages
    responses = [
        "I understand you're asking about something. I can help you with order status, returns, technical issues, or general questions. Could you provide more details?",
        "I'd love to help! I'm best at assisting with order tracking, returns, technical problems, or product questions. What specific issue can I help with?",
        "I'm here to help with customer support questions. Could you tell me more about what you need assistance with?"
    ]
    
    response = {
        'response': random.choice(responses),
        'intent': 'general',
        'confidence': 50
    }
    
    return jsonify(response)

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Analytics endpoint - returns bot usage statistics"""
    return jsonify({
        'total_conversations': 1247,
        'resolution_rate': 89,
        'escalations': 137,
        'satisfaction': 4.7,
        'average_response_time': '2.3s',
        'common_intents': {
            'order_status': 45,
            'technical_support': 30,
            'refund_returns': 15,
            'billing': 10
        }
    })

@app.route('/api/order/<order_number>', methods=['GET'])
def get_order(order_number):
    """Order lookup endpoint - returns order status"""
    order_info = get_order_status(order_number)
    if order_info:
        return jsonify({
            'found': True,
            'order_number': order_number,
            'details': order_info
        })
    else:
        return jsonify({
            'found': False,
            'message': 'Order not found. Try ORD-12345, ORD-67890, or ORD-11111'
        }), 404

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'service': 'customer-support-bot'})

if __name__ == '__main__':
    print("🚀 Customer Support Bot Backend Starting...")
    print("📍 API available at: http://localhost:5000")
    print("🔗 Test these URLs in your browser:")
    print("   • http://localhost:5000/")
    print("   • http://localhost:5000/api/test") 
    print("   • http://localhost:5000/api/analytics")
    print("   • http://localhost:5000/api/order/ORD-12345")
    print("   • http://localhost:5000/health")
    print("\n💡 For frontend: cd ../frontend && python -m http.server 3000")
    app.run(debug=True, port=5000, host='0.0.0.0')