// Enhanced Response templates and configuration
const RESPONSES = {
    greeting: [
        "Hello! Welcome to TechShop Support. How can I assist you today?",
        "Hi there! I'm your TechShop assistant. What can I help you with?",
        "Welcome to TechShop Customer Support! I'm here to help with orders, returns, technical issues, or any questions you might have."
    ],
    order_status: [
        "I can help you check your order status. Please provide your order number (format: ORD-12345).",
        "To check your order status, I'll need your order number. You can find it in your order confirmation email.",
        "Sure! Let me look up your order status. What's your order number? It usually starts with ORD- followed by numbers."
    ],
    refund: [
        "I can assist with your refund request. Our standard return policy is 30 days. Please provide your order number to get started.",
        "I understand you'd like a refund. Let me check your eligibility. What's your order number and reason for return?",
        "I can help process your refund. Could you share your order information and let me know why you're returning the item?"
    ],
    technical: [
        "I'm sorry you're experiencing technical issues. Let me help troubleshoot. What device are you using and what exactly is happening?",
        "Technical problems can be frustrating. Tell me more about your device and the issue you're facing so I can provide specific solutions.",
        "I can help troubleshoot your technical issue. Please describe the problem in detail, including any error messages you see."
    ],
    billing: [
        "I can help with billing questions. Are you asking about payment methods, charges on your statement, or something else specific?",
        "Let me assist with your billing inquiry. What specific information do you need about payments, charges, or your account?",
        "I can answer your billing questions. Are you looking for information about accepted payment methods, a specific charge, or billing issues?"
    ],
    shipping: [
        "I can help with shipping questions! We offer standard (5-7 days), express (2-3 days), and overnight shipping. What would you like to know?",
        "Shipping information: Standard takes 5-7 business days ($4.99), Express 2-3 days ($12.99), Overnight next business day ($24.99). How can I assist?",
        "I have shipping details! We ship via UPS, FedEx, USPS, and DHL. Free standard shipping on orders over $50. What specific shipping question do you have?"
    ],
    product_info: [
        "I can provide product information! We carry laptops (TechBook Pro, GamerX), smartphones (SmartPhone X), and accessories. What product are you interested in?",
        "Product assistance: Our lineup includes TechBook Pro laptops, GamerX gaming laptops, SmartPhone X, and wireless accessories. Which product would you like to know about?",
        "I can help with product details! We have various models of laptops, smartphones, and accessories. What specific product or feature are you asking about?"
    ],
    account_help: [
        "I can help with account issues. Are you having trouble logging in, need to reset your password, or update your information?",
        "Account assistance: I can help with password resets, profile updates, or account settings. What specific account issue are you experiencing?",
        "I can assist with your account. Are you looking to reset your password, update personal information, or manage your account settings?"
    ],
    escalation: [
        "I'm connecting you with a human agent who can better assist with this complex issue. They'll be with you shortly.",
        "This seems like a situation where our specialized support team can provide better assistance. Let me transfer you now.",
        "I think one of our human agents would be better equipped to help with this. Connecting you with our support specialist team."
    ],
    default: [
        "I'm not sure I understand. Could you rephrase your question? I can help with orders, returns, technical support, billing, shipping, and product information.",
        "I don't have enough information to help with that specific question. Could you provide more details or try asking in a different way?",
        "I'm still learning. Could you try rephrasing your question? I'm best at helping with order status, returns, technical issues, billing, and product questions."
    ]
};

const QUICK_REPLIES = {
    order_status: ["Track my order", "Where is my package?", "Order #ORD-12345 status", "Shipping update"],
    refund: ["I want a refund", "Return my product", "Cancel my order", "Start return process"],
    technical: ["Device not working", "Technical problem", "Setup help needed", "Performance issues"],
    billing: ["Payment question", "Invoice issue", "Billing problem", "Payment methods"],
    shipping: ["Shipping options", "Delivery time", "Track package", "International shipping"],
    product_info: ["Product specifications", "Compare models", "Warranty info", "Compatibility"],
    account_help: ["Reset password", "Update account", "Login issues", "Delete account"]
};

const INTENT_KEYWORDS = {
    greeting: ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'greetings'],
    order_status: ['order', 'status', 'track', 'where is', 'package', 'delivery', 'shipment', 'when arrive'],
    refund: ['refund', 'return', 'cancel', 'money back', 'send back', 'send item back'],
    technical: ['technical', 'issue', 'problem', 'not working', 'error', 'bug', 'crash', 'broken', 'fix'],
    billing: ['bill', 'payment', 'invoice', 'charge', 'billing', 'subscription', 'credit card', 'pay'],
    shipping: ['shipping', 'delivery', 'ship', 'carrier', 'ups', 'fedex', 'mail', 'post'],
    product_info: ['product', 'spec', 'specification', 'feature', 'model', 'compare', 'warranty'],
    account_help: ['account', 'login', 'password', 'profile', 'register', 'sign up', 'delete account'],
    escalation: ['human', 'agent', 'representative', 'person', 'talk to someone', 'real person', 'live agent']
};

// Enhanced product database
const PRODUCT_DATABASE = {
    "techbook pro": {
        name: "TechBook Pro",
        models: {
            "tb2023": { ram: "8GB", storage: "256GB SSD", price: "$999" },
            "tb2024": { ram: "16GB", storage: "512GB SSD", price: "$1299" },
            "tb2024 max": { ram: "32GB", storage: "1TB SSD", price: "$1799" }
        },
        features: ["Retina Display", "12-hour battery", "Thunderbolt 4", "Backlit Keyboard"],
        warranty: "2 years"
    },
    "gamerx laptop": {
        name: "GamerX Laptop", 
        models: {
            "gx15": { ram: "16GB", storage: "512GB SSD", graphics: "RTX 4060", price: "$1499" },
            "gx17": { ram: "32GB", storage: "1TB SSD", graphics: "RTX 4070", price: "$1999" },
            "gx17 pro": { ram: "64GB", storage: "2TB SSD", graphics: "RTX 4080", price: "$2799" }
        },
        features: ["144Hz Display", "RGB Keyboard", "Advanced Cooling", "Gaming-Optimized"],
        warranty: "1 year"
    },
    "smartphone x": {
        name: "SmartPhone X",
        models: {
            "spx12": { storage: "128GB", colors: ["Black", "White"], price: "$799" },
            "spx13": { storage: "256GB", colors: ["Black", "White", "Blue"], price: "$899" },
            "spx13 pro": { storage: "512GB", colors: ["Black", "Silver", "Gold"], price: "$1099" }
        },
        features: ["5G Connectivity", "Triple Camera", "Face ID", "Wireless Charging"],
        warranty: "1 year"
    }
};

// Enhanced troubleshooting guides
const TROUBLESHOOTING_GUIDES = {
    "wont turn on": [
        "Check if the device is properly charged or connected to power",
        "Try a different power outlet and cable", 
        "Perform a hard reset by holding power button for 15 seconds",
        "Check for any visible damage to the device or cables"
    ],
    "slow performance": [
        "Restart your device completely",
        "Clear cache and temporary files",
        "Close unused applications and browser tabs", 
        "Check available storage space (keep at least 10% free)",
        "Update to the latest software version"
    ],
    "wifi issues": [
        "Restart your router and device",
        "Check if other devices can connect to the same network",
        "Move closer to the router or remove obstructions",
        "Forget the network and reconnect with correct password",
        "Check for router firmware updates"
    ],
    "battery drain": [
        "Check battery usage in settings to identify power-hungry apps",
        "Reduce screen brightness and timeout duration",
        "Turn off unnecessary connectivity (Bluetooth, GPS when not needed)",
        "Update to latest software version",
        "Check for background app activity"
    ]
};