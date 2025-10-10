// Enhanced NLP Processing Module
class NLPProcessor {
    static processMessage(message) {
        const intent = Helpers.detectIntent(message);
        const entities = this.extractEntities(message, intent);
        const response = this.generateResponse(message, intent, entities);
        const confidence = this.calculateConfidence(message, intent, entities);
        
        return {
            intent: intent,
            response: response,
            confidence: confidence,
            entities: entities,
            suggested_actions: this.getSuggestedActions(intent, entities)
        };
    }

    static generateResponse(message, intent, entities) {
        let baseResponse = Helpers.getRandomResponse(intent);
        
        // Enhance response based on entities
        if (entities.product) {
            const productInfo = this.getProductInfo(entities.product);
            if (productInfo) {
                baseResponse += `\n\nAbout ${productInfo.name}: ${this.formatProductInfo(productInfo)}`;
            }
        }
        
        if (entities.orderNumber) {
            baseResponse += `\n\nI see you mentioned order ${entities.orderNumber}. `;
            baseResponse += "I can look up the specific details once we're connected to our backend system.";
        }
        
        // Add troubleshooting steps for technical issues
        if (intent === 'technical') {
            const issue = this.identifyTechnicalIssue(message);
            if (issue && TROUBLESHOOTING_GUIDES[issue]) {
                baseResponse += `\n\nFor ${issue}, try these steps:\n• ${TROUBLESHOOTING_GUIDES[issue].join('\n• ')}`;
            }
        }
        
        return baseResponse;
    }

    static calculateConfidence(message, intent, entities) {
        let confidence = 0;
        const keywords = INTENT_KEYWORDS[intent] || [];
        const messageLower = message.toLowerCase();
        
        // Base confidence from keyword matches
        const matches = keywords.filter(keyword => 
            messageLower.includes(keyword)
        ).length;
        
        confidence = Math.min((matches / Math.max(keywords.length, 1)) * 80, 80);
        
        // Boost confidence if entities found
        if (Object.keys(entities).length > 0) {
            confidence += 15;
        }
        
        // Specific patterns boost confidence
        if (messageLower.match(/order\s*(number)?\s*[#]?[a-z0-9-]+/i)) {
            confidence += 10;
        }
        
        return Math.min(confidence, 100);
    }

    static extractEntities(message, intent) {
        const entities = {};
        const messageLower = message.toLowerCase();
        
        // Extract order numbers (various formats)
        const orderMatch = messageLower.match(/(?:order|ord|#)?\s*([a-z0-9]{3,}-?\d+)/i);
        if (orderMatch) entities.orderNumber = orderMatch[1].toUpperCase();
        
        // Extract email addresses
        const emailMatch = message.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/);
        if (emailMatch) entities.email = emailMatch[0];
        
        // Extract product names
        for (const [productKey, productInfo] of Object.entries(PRODUCT_DATABASE)) {
            if (messageLower.includes(productKey)) {
                entities.product = productKey;
                entities.productDetails = productInfo;
                break;
            }
            
            // Check for model numbers
            for (const modelKey of Object.keys(productInfo.models)) {
                if (messageLower.includes(modelKey)) {
                    entities.product = productKey;
                    entities.model = modelKey;
                    entities.productDetails = productInfo;
                    break;
                }
            }
        }
        
        // Extract specific technical issues
        const technicalIssue = this.identifyTechnicalIssue(message);
        if (technicalIssue) {
            entities.technicalIssue = technicalIssue;
        }
        
        // Extract urgency indicators
        const urgencyWords = ['urgent', 'asap', 'emergency', 'immediately', 'right away'];
        if (urgencyWords.some(word => messageLower.includes(word))) {
            entities.urgent = true;
        }
        
        return entities;
    }

    static identifyTechnicalIssue(message) {
        const messageLower = message.toLowerCase();
        
        if (messageLower.match(/(won't|wont|not|doesn't).*turn on|power|start|boot/)) 
            return "wont turn on";
        if (messageLower.match(/(slow|lag|freez|unresponsive|performance)/)) 
            return "slow performance";
        if (messageLower.match(/(wifi|wireless|internet|connection|network).*(problem|issue|not work)/)) 
            return "wifi issues";
        if (messageLower.match(/(battery|charge|power).*(drain|die|empty|last)/)) 
            return "battery drain";
        if (messageLower.match(/(screen|display).*(crack|broken|damage|not work)/)) 
            return "screen damage";
            
        return null;
    }

    static getProductInfo(productName) {
        return PRODUCT_DATABASE[productName.toLowerCase()];
    }

    static formatProductInfo(productInfo) {
        if (!productInfo) return "";
        
        let info = `Available models: ${Object.keys(productInfo.models).join(', ')}. `;
        info += `Key features: ${productInfo.features.slice(0, 3).join(', ')}. `;
        info += `Warranty: ${productInfo.warranty}.`;
        
        return info;
    }

    static getSuggestedActions(intent, entities) {
        const actions = [];
        
        switch(intent) {
            case 'order_status':
                actions.push('Check order status in system');
                if (!entities.orderNumber) {
                    actions.push('Request order number from customer');
                }
                break;
            case 'technical':
                actions.push('Provide troubleshooting steps');
                if (entities.urgent) {
                    actions.push('Flag as high priority');
                }
                break;
            case 'refund':
                actions.push('Check return eligibility');
                actions.push('Explain return process');
                break;
        }
        
        return actions;
    }
}