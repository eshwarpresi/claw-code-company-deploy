import openai
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

session_memory = {}

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Aisea - PAS Freight AI</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        /* Floating Chat Button */
        #pasfreight-chat-btn {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            border: none;
            z-index: 999999;
        }
        #pasfreight-chat-btn:hover { transform: scale(1.08); box-shadow: 0 12px 32px rgba(0,0,0,0.25); }
        .chat-icon { font-size: 28px; color: white; }
        
        .notification-badge {
            position: absolute;
            top: -4px;
            right: -4px;
            background: #ef4444;
            color: white;
            border-radius: 50%;
            width: 18px;
            height: 18px;
            font-size: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            animation: blink 1s infinite;
        }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        /* Main Chat Window */
        #pasfreight-chat-window {
            position: fixed;
            bottom: 90px;
            right: 24px;
            width: 420px;
            height: 620px;
            background: white;
            border-radius: 24px;
            box-shadow: 0 24px 48px rgba(0,0,0,0.3);
            display: none;
            z-index: 999998;
            border: none;
            overflow: hidden;
            flex-direction: column;
        }
        
        /* Header */
        .chat-header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-header h3 {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .chat-header p {
            font-size: 12px;
            opacity: 0.8;
        }
        
        /* Service Buttons - 4 main services */
        .service-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin: 16px 0;
            justify-content: center;
        }
        .service-btn {
            background: linear-gradient(135deg, #f1f5f9, #ffffff);
            border: 1px solid #e2e8f0;
            padding: 10px 16px;
            border-radius: 40px;
            font-size: 13px;
            cursor: pointer;
            color: #1e3c72;
            font-weight: 600;
            transition: all 0.2s;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        .service-btn:hover {
            background: linear-gradient(135deg, #2a5298, #1e3c72);
            color: white;
            border-color: #2a5298;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        /* Messages Area */
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 20px;
            display: flex;
            animation: fadeInUp 0.3s ease;
        }
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .user-message {
            justify-content: flex-end;
        }
        .bot-message {
            justify-content: flex-start;
        }
        
        .bubble {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 20px;
            font-size: 13px;
            line-height: 1.45;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        .user-message .bubble {
            background: #2a5298;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .bot-message .bubble {
            background: white;
            color: #1a202c;
            border: 1px solid #e2e8f0;
            border-bottom-left-radius: 4px;
        }
        
        /* Typing Animation */
        .typing {
            display: inline-flex;
            gap: 4px;
            padding: 8px 0;
        }
        .typing span {
            width: 8px;
            height: 8px;
            background: #cbd5e0;
            border-radius: 50%;
            animation: typingBounce 1.4s infinite;
        }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-8px); }
        }
        
        /* Sub Buttons for Air/Sea */
        .sub-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }
        .sub-btn {
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            padding: 8px 14px;
            border-radius: 30px;
            font-size: 12px;
            cursor: pointer;
            color: #1e3c72;
            font-weight: 500;
            transition: all 0.2s;
        }
        .sub-btn:hover {
            background: #2a5298;
            color: white;
            border-color: #2a5298;
        }
        
        /* Contact Card - Light and clean */
        .contact-card {
            background: #f8fafc;
            border-radius: 16px;
            padding: 16px;
            margin-top: 12px;
            border: 1px solid #e2e8f0;
        }
        .contact-card h4 {
            font-size: 14px;
            font-weight: 600;
            color: #1e3c72;
            margin-bottom: 12px;
        }
        .contact-item {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
            font-size: 12px;
            color: #334155;
        }
        .contact-item:last-child { margin-bottom: 0; }
        
        /* Input Area */
        .chat-input {
            padding: 16px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 12px;
        }
        .chat-input input {
            flex: 1;
            padding: 12px 16px;
            background: #f8f9fa;
            border: 1px solid #e2e8f0;
            border-radius: 30px;
            font-size: 13px;
            outline: none;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s;
        }
        .chat-input input:focus {
            border-color: #2a5298;
            box-shadow: 0 0 0 3px rgba(42,82,152,0.1);
        }
        .chat-input input::placeholder {
            color: #94a3b8;
        }
        .chat-input button {
            background: #2a5298;
            color: white;
            border: none;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .chat-input button:hover {
            background: #1e3c72;
            transform: scale(1.02);
        }
        
        /* Scrollbar */
        .chat-messages::-webkit-scrollbar {
            width: 5px;
        }
        .chat-messages::-webkit-scrollbar-track {
            background: #e2e8f0;
            border-radius: 10px;
        }
        .chat-messages::-webkit-scrollbar-thumb {
            background: #cbd5e0;
            border-radius: 10px;
        }
        
        /* WhatsApp Floating Button */
        .whatsapp-float {
            position: fixed;
            bottom: 90px;
            right: 24px;
            width: 50px;
            height: 50px;
            background: #25D366;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            z-index: 999997;
            transition: all 0.3s ease;
        }
        .whatsapp-float:hover {
            transform: scale(1.1);
        }
        
        @media (max-width: 500px) {
            #pasfreight-chat-window {
                width: 100%;
                height: 100%;
                bottom: 0;
                right: 0;
                border-radius: 0;
            }
            #pasfreight-chat-btn {
                bottom: 16px;
                right: 16px;
            }
            .whatsapp-float {
                bottom: 16px;
                right: 80px;
            }
        }
    </style>
</head>
<body>
    <button id="pasfreight-chat-btn">
        <span class="chat-icon">💬</span>
        <span class="notification-badge" id="notificationBadge" style="display: none;">1</span>
    </button>
    
    <div class="whatsapp-float" onclick="window.open('https://wa.me/919036101201', '_blank')">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28" fill="white">
            <path d="M12.031 6.172c-3.181 0-5.767 2.586-5.768 5.766-.001 1.298.38 2.27 1.019 3.287l-.582 2.128 2.182-.573c.978.596 2.059.914 3.149.915h.003c3.181 0 5.767-2.586 5.768-5.766.001-3.181-2.585-5.767-5.767-5.767zm3.392 8.244c-.144.405-.837.774-1.17.824-.299.045-.677.063-1.092-.135-.414-.198-1.189-.583-2.082-1.258-.937-.705-1.614-1.516-1.767-1.847-.153-.331-.123-.614.032-.842.147-.216.333-.479.45-.718.117-.239.156-.479.028-.718-.129-.239-.595-1.176-.814-1.591-.213-.4-.46-.412-.609-.412-.154 0-.33-.01-.507-.01-.283 0-.74.105-1.147.598-.425.514-1.6 1.596-1.6 3.791 0 2.195 1.576 4.319 1.8 4.618.224.299 1.436 2.261 3.517 3.084.5.197.915.31 1.241.397.522.153 1.012.121 1.388.073.424-.054 1.173-.479 1.338-.943.165-.464.165-.863.115-.943-.049-.08-.183-.129-.382-.225-.198-.096-1.171-.578-1.352-.644-.18-.066-.312-.096-.444.096-.131.192-.511.644-.626.776-.115.132-.23.148-.429.052-.198-.096-.836-.308-1.592-1.018-.587-.552-1.02-1.293-1.138-1.512-.118-.219-.013-.338.089-.447.091-.098.203-.255.305-.382.102-.128.136-.224.203-.374.067-.15.034-.28-.017-.392-.05-.112-.444-1.072-.609-1.469-.16-.384-.323-.332-.435-.338-.109-.006-.234-.006-.36-.006-.274 0-.718.103-1.095.507z"/>
        </svg>
    </div>
    
    <div id="pasfreight-chat-window">
        <div class="chat-header">
            <h3>✨ Aisea</h3>
            <p>PAS Freight AI • 24/7 Support</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="bubble">Hi, I'm Aisea 👋<br><br>Need help with shipping? Select a service below or ask me anything.</div>
            </div>
            <div class="message bot-message">
                <div class="bubble">
                    <div class="service-buttons">
                        <button class="service-btn" onclick="showImportMenu()">📥 IMPORT</button>
                        <button class="service-btn" onclick="showExportMenu()">📤 EXPORT</button>
                        <button class="service-btn" onclick="showCustoms()">📋 CUSTOMS</button>
                        <button class="service-btn" onclick="showCourier()">📮 COURIER</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Ask me anything..." autocomplete="off">
            <button id="sendBtn">➤</button>
        </div>
    </div>

    <script>
        let sessionId = 'session_' + Date.now();
        let isOpen = false;
        let notified = false;
        
        const chatBtn = document.getElementById('pasfreight-chat-btn');
        const chatWindow = document.getElementById('pasfreight-chat-window');
        const messagesDiv = document.getElementById('chatMessages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        
        chatBtn.addEventListener('click', function() {
            if (isOpen) {
                chatWindow.style.display = 'none';
                isOpen = false;
            } else {
                chatWindow.style.display = 'flex';
                isOpen = true;
                notificationBadge.style.display = 'none';
                notified = true;
            }
        });
        
        // Close button
        const closeBtn = document.querySelector('.chat-header').nextElementSibling;
        
        function showTyping() {
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.id = 'typing';
            div.innerHTML = '<div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        }
        
        function hideTyping() {
            const typing = document.getElementById('typing');
            if (typing) typing.remove();
        }
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            div.innerHTML = `<div class="bubble">${text}</div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        }
        
        function addContactInfo(title, numbers, emails) {
            let html = `<div class="contact-card"><h4>${title}</h4>`;
            if (numbers && numbers.length) {
                numbers.forEach(num => { html += `<div class="contact-item">📞 ${num}</div>`; });
            }
            if (emails && emails.length) {
                emails.forEach(email => { html += `<div class="contact-item">✉️ ${email}</div>`; });
            }
            html += `</div>`;
            addMessage(html, false);
        }
        
        // IMPORT Menu
        window.showImportMenu = function() {
            addMessage("IMPORT", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📥 <strong>Select Mode:</strong><br>
                <div class="sub-buttons">
                    <button class="sub-btn" onclick="showImportAir()">✈️ AIR</button>
                    <button class="sub-btn" onclick="showImportSea()">🚢 SEA</button>
                </div>
            </div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        };
        
        window.showImportAir = function() {
            addMessage("IMPORT - AIR", true);
            addContactInfo("IMPORT AIR FREIGHT", 
                ["+91 99869 42772", "+91 63615 21413"],
                ["gj@pasfreight.com", "rachana@pasfreight.com"]);
        };
        
        window.showImportSea = function() {
            addMessage("IMPORT - SEA", true);
            addContactInfo("IMPORT SEA FREIGHT (FCL/LCL)", 
                ["+91 93648 81371", "+91 63615 21413"],
                ["vinodh@pasfreight.com", "gj@pasfreight.com"]);
        };
        
        // EXPORT Menu
        window.showExportMenu = function() {
            addMessage("EXPORT", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📤 <strong>Select Mode:</strong><br>
                <div class="sub-buttons">
                    <button class="sub-btn" onclick="showExportAir()">✈️ AIR</button>
                    <button class="sub-btn" onclick="showExportSea()">🚢 SEA</button>
                </div>
            </div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        };
        
        window.showExportAir = function() {
            addMessage("EXPORT - AIR", true);
            addContactInfo("EXPORT AIR FREIGHT", 
                ["+91 93648 81371", "+91 63615 26659"],
                ["vinodh@pasfreight.com", "kavan@pasfreight.com"]);
        };
        
        window.showExportSea = function() {
            addMessage("EXPORT - SEA", true);
            addContactInfo("EXPORT SEA FREIGHT", 
                ["+91 93648 81371", "+91 63615 26659"],
                ["vinodh@pasfreight.com", "kavan@pasfreight.com"]);
        };
        
        // CUSTOMS
        window.showCustoms = function() {
            addMessage("CUSTOMS CLEARANCE", true);
            addContactInfo("CUSTOMS CLEARANCE", 
                ["+91 63615 26664"],
                ["ajith@pasfreight.com", "edi.blr@pasfreight.com"]);
        };
        
        // COURIER (renamed from CARGO)
        window.showCourier = function() {
            addMessage("COURIER", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📮 <strong>Select Type:</strong><br>
                <div class="sub-buttons">
                    <button class="sub-btn" onclick="showDomesticCourier()">🇮🇳 DOMESTIC</button>
                    <button class="sub-btn" onclick="showInternationalCourier()">🌍 INTERNATIONAL</button>
                </div>
            </div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        };
        
        window.showDomesticCourier = function() {
            addMessage("DOMESTIC COURIER", true);
            addContactInfo("DOMESTIC COURIER", 
                ["+91 63615 26659"],
                ["kavan@pasfreight.com", "info@pasfreight.com"]);
        };
        
        window.showInternationalCourier = function() {
            addMessage("INTERNATIONAL COURIER", true);
            addContactInfo("INTERNATIONAL COURIER", 
                ["+91 63615 26659"],
                ["kavan@pasfreight.com", "info@pasfreight.com"]);
        };
        
        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;
            userInput.value = '';
            addMessage(text, true);
            showTyping();
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, session_id: sessionId })
                });
                const data = await response.json();
                hideTyping();
                addMessage(data.reply, false);
            } catch(error) {
                hideTyping();
                addMessage('Call +91 90361 01201 for assistance.', false);
            }
        }
        
        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', function(e) { if (e.key === 'Enter') sendMessage(); });
        
        window.showImportMenu = showImportMenu;
        window.showImportAir = showImportAir;
        window.showImportSea = showImportSea;
        window.showExportMenu = showExportMenu;
        window.showExportAir = showExportAir;
        window.showExportSea = showExportSea;
        window.showCustoms = showCustoms;
        window.showCourier = showCourier;
        window.showDomesticCourier = showDomesticCourier;
        window.showInternationalCourier = showInternationalCourier;
    </script>
</body>
</html>
'''

# Premium intent detection with memory
def detect_intent(user_msg, ctx):
    msg_lower = user_msg.lower()
    
    # Show interest / ready to book
    if any(word in msg_lower for word in ['ready', 'book', 'make it simple', 'proceed', 'finalize', 'go ahead', 'yes let\'s', 'sounds good', 'perfect']):
        return 'convert'
    
    # Not urgent, balanced approach
    if ('not urgent' in msg_lower or 'not in a hurry' in msg_lower or 'no rush' in msg_lower):
        return 'balanced'
    
    # Negotiation / match price
    if any(word in msg_lower for word in ['match', 'negotiate', 'can you do better', 'discount', 'competitive']):
        return 'negotiate'
    
    # Responsibility / liability
    if any(word in msg_lower for word in ['responsible', 'liable', 'accountable', 'claim', 'damage coverage']):
        return 'responsibility'
    
    # Guarantee / timeline
    if any(word in msg_lower for word in ['guarantee', 'delivery by', 'by date', 'by friday', 'exact timeline']):
        return 'guarantee'
    
    # High value / trust
    if any(word in msg_lower for word in ['high value', 'expensive', 'costly', 'worth', 'lakh', 'crore']):
        return 'trust_premium'
    
    # Cost priority
    if any(word in msg_lower for word in ['cheapest', 'budget', 'save money', 'low cost', 'affordable', 'economical']):
        return 'cost'
    
    # Urgent
    if any(word in msg_lower for word in ['urgent', 'fast', 'quick', 'express', 'asap', 'immediate']):
        return 'urgent'
    
    # Bulk / regular
    if any(word in msg_lower for word in ['bulk', 'monthly', 'weekly', 'regular', 'volume', 'frequent', 'recurring']):
        return 'bulk'
    
    # Customs
    if any(word in msg_lower for word in ['customs', 'clearance', 'duty', 'tax', 'documentation']):
        return 'customs'
    
    # Track shipment
    if 'track' in msg_lower:
        return 'track'
    
    # Electronics
    if 'electronics' in msg_lower:
        return 'electronics'
    
    return 'general'

# Premium response generator
def get_premium_response(intent, ctx, user_msg):
    weight = ctx.get('weight', 'your')
    dest = ctx.get('destination', 'destination')
    cargo = ctx.get('cargo_type', 'goods')
    
    # CONVERSION - Strong, confident closing
    if intent == 'convert':
        return f"""Perfect 👍 I'll arrange this for you right away.

Just share your name and WhatsApp number so our team can confirm the best option and handle everything from pickup to delivery.

What's the best number to reach you?"""
    
    # TRACK SHIPMENT
    if intent == 'track':
        return """Please share your shipment tracking ID or reference number, and I'll check the status for you right away."""
    
    # BALANCED - Not urgent, value-conscious
    elif intent == 'balanced':
        return f"""I understand 👍 You want reliability without overspending.

For {weight}kg {cargo} to {dest}:
• Economy Air: 7-10 days, moderate cost, safer handling
• Sea (with insurance): 20-30 days, best cost savings

Since time isn't urgent, sea freight gives you maximum value. Would you like me to check the exact sea freight option for you?"""
    
    # NEGOTIATION - Confident deal-making
    elif intent == 'negotiate':
        return f"""I appreciate your directness 👍

Let me check what's the best possible rate for your {weight}kg shipment to {dest}.

What price point would work for you? If I can match it, we can proceed immediately."""
    
    # RESPONSIBILITY - Premium enterprise answer
    elif intent == 'responsibility':
        return f"""Excellent question 👍 That's how we differentiate.

We provide:
• Clear INCOTERMS agreement before shipment
• Full insurance coverage options
• Real-time tracking portal access
• Dedicated resolution manager for any issues

For high-value shipments, we assign a single point of contact. Would you like me to explain our claim process?"""
    
    # GUARANTEE - Realistic but confident
    elif intent == 'guarantee':
        return f"""For {weight}kg to {dest}, here's what I can guarantee:

• Express air: 3-5 days (carrier permitting)
• Standard air: 7-10 days
• Sea: 20-30 days

While exact dates depend on carrier schedules, we only share timelines we're confident about. Want me to check current availability for your fastest option?"""
    
    # TRUST PREMIUM - High value shipments
    elif intent == 'trust_premium':
        return f"""For a shipment of this value, we take extra precautions:

✓ White-glove handling
✓ Priority security screening
✓ Enhanced insurance coverage
✓ Direct carrier relationship
✓ Real-time GPS tracking

Your shipment won't just be delivered - it will be protected throughout. Shall I prepare a premium service plan for you?"""
    
    # COST - Value-focused
    elif intent == 'cost':
        return f"""For {weight}kg to {dest}, sea freight saves 60-70% compared to air.

Sea: 20-30 days | Air: 3-7 days

Given your focus on budget, I recommend sea freight with proper packing. Want me to get you the current sea freight rate?"""
    
    # URGENT - Action-oriented
    elif intent == 'urgent':
        return f"""For urgent delivery to {dest}:

✓ Express air: 3-5 days
✓ Priority handling
✓ Real-time tracking
✓ Direct flight routing

I can check immediate flight availability. Shall I proceed?"""
    
    # BULK - Strategic partnership
    elif intent == 'bulk':
        return f"""For regular shipments, we offer:

✓ Volume discounts (tiered pricing)
✓ Dedicated account manager
✓ Fixed weekly schedules
✓ Priority space allocation

What's your estimated monthly volume? I'll prepare a customized pricing proposal for you."""
    
    # CUSTOMS - Expert guidance
    elif intent == 'customs':
        return f"""Customs clearance is our expertise 👍

We handle:
✓ Document preparation (commercial invoice, packing list, etc.)
✓ HS code classification
✓ Duty calculation and payment
✓ Compliance verification

Our team proactively reviews documents to avoid delays. Need help with a specific shipment?"""
    
    # ELECTRONICS - Specialized handling
    elif intent == 'electronics':
        return f"""Electronics require special handling 👍

For {weight}kg to {dest}:
✓ ESD-safe packaging available
✓ Anti-static handling
✓ Climate-controlled options
✓ Reduced insurance rates for certified shippers

Air freight is recommended for electronics safety. Shall I check the air freight option for you?"""
    
    # GENERAL - AI fallback
    else:
        return None

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if session_id not in session_memory:
        session_memory[session_id] = {'cargo_type': None, 'destination': None, 'weight': None, 'origin': None, 'intent': None}
    
    ctx = session_memory[session_id]
    
    # Extract shipment details
    weight_match = re.search(r'(\d+)\s*(?:kg|kgs|kilo|kilogram)', user_msg, re.IGNORECASE)
    if weight_match and not ctx.get('weight'):
        ctx['weight'] = weight_match.group(1)
    
    dest_match = re.search(r'(?:to|for)\s+([A-Z][a-z]+|[A-Z]+)', user_msg)
    if dest_match and not ctx.get('destination'):
        ctx['destination'] = dest_match.group(1).title()
    
    cargo_map = {
        'electronics': 'electronics', 'garments': 'garments', 'medicine': 'medicine',
        'machinery': 'machinery', 'furniture': 'furniture', 'spare parts': 'spare parts',
        'chemicals': 'chemicals', 'food': 'food'
    }
    for key, value in cargo_map.items():
        if key in user_msg.lower() and not ctx.get('cargo_type'):
            ctx['cargo_type'] = value
            break
    
    # Detect intent
    intent = detect_intent(user_msg, ctx)
    ctx['intent'] = intent
    
    # Get premium response
    premium_response = get_premium_response(intent, ctx, user_msg)
    
    if premium_response:
        session_memory[session_id] = ctx
        return jsonify({'reply': premium_response})
    
    # Fallback to AI for other queries
    system_prompt = """You are Aisea, a premium logistics consultant for PAS Freight.

Guidelines:
- Be conversational and solution-driven
- Never ask for information already provided
- Build trust first, then ask for details
- Use premium, confident language
- Sound like an expert, not a robot

Company: PAS Freight (WCA & GLA Certified, 8+ years)
Contact: +91 90361 01201

Be helpful, confident, and premium."""
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=150,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        session_memory[session_id] = ctx
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': "Tell me what you'd like to ship - I'll help you figure out the best solution."})

if __name__ == '__main__':
    print("=" * 60)
    print("Aisea - Final UI with Service Buttons")
    print("Open: http://localhost:5001")
    print("Services: IMPORT | EXPORT | CUSTOMS | COURIER")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
