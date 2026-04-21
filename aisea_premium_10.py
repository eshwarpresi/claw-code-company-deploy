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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #343541; height: 100vh; display: flex; justify-content: center; align-items: center; }
        
        #pasfreight-chat-btn {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 56px;
            height: 56px;
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
        
        #pasfreight-chat-window {
            position: fixed;
            bottom: 90px;
            right: 24px;
            width: 420px;
            height: 620px;
            background: #343541;
            border-radius: 24px;
            box-shadow: 0 24px 48px rgba(0,0,0,0.3);
            display: none;
            z-index: 999998;
            border: none;
            overflow: hidden;
            flex-direction: column;
        }
        
        .chat-header {
            background: #202123;
            padding: 16px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #4a4b53;
        }
        .header-info { display: flex; align-items: center; gap: 10px; }
        .avatar { width: 36px; height: 36px; background: #2a5298; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; }
        .header-text h3 { font-size: 16px; font-weight: 600; color: #ececec; }
        .header-text p { font-size: 10px; color: #8e8ea0; margin-top: 2px; }
        .close-chat { background: none; border: none; color: #8e8ea0; font-size: 18px; cursor: pointer; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
        .close-chat:hover { background: #40414f; color: white; }
        
        .service-buttons {
            padding: 12px;
            background: #40414f;
            border-top: 1px solid #4a4b53;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            justify-content: center;
        }
        .service-btn {
            background: #2a5298;
            color: white;
            border: none;
            padding: 8px 14px;
            border-radius: 25px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }
        .service-btn:hover { background: #1e3c72; transform: scale(0.98); }
        
        .sub-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 8px;
            justify-content: center;
        }
        .sub-btn {
            background: #1e3c72;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .sub-btn:hover { background: #2a5298; }
        
        .chat-messages { flex: 1; overflow-y: auto; padding: 20px; background: #343541; }
        .message { margin-bottom: 20px; display: flex; }
        .user-message { justify-content: flex-end; }
        .bot-message { justify-content: flex-start; }
        .bubble { max-width: 80%; padding: 10px 14px; border-radius: 20px; font-size: 13px; line-height: 1.45; }
        .user-message .bubble { background: #2a5298; color: white; border-bottom-right-radius: 4px; }
        .bot-message .bubble { background: #444654; color: #ececec; border-bottom-left-radius: 4px; }
        .contact-info { background: #2a2a2a; padding: 10px; border-radius: 12px; margin-top: 6px; font-size: 12px; }
        
        .chat-input { padding: 16px; background: #40414f; border-top: 1px solid #4a4b53; display: flex; gap: 10px; }
        .chat-input input { flex: 1; padding: 12px 16px; background: #40414f; border: 1px solid #565869; border-radius: 28px; font-size: 13px; color: white; outline: none; font-family: 'Inter', sans-serif; }
        .chat-input input::placeholder { color: #8e8ea0; }
        .chat-input input:focus { border-color: #10a37f; }
        .chat-input button { background: #10a37f; color: white; border: none; width: 42px; height: 42px; border-radius: 50%; cursor: pointer; font-size: 18px; transition: all 0.2s; }
        .chat-input button:hover { background: #1a7f64; transform: scale(1.02); }
        
        .typing { display: inline-flex; gap: 5px; padding: 6px 0; }
        .typing span { width: 7px; height: 7px; background: #8e8ea0; border-radius: 50%; animation: typingBounce 1.4s infinite; }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typingBounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-8px); } }
        
        .chat-messages::-webkit-scrollbar { width: 5px; }
        .chat-messages::-webkit-scrollbar-track { background: #40414f; }
        .chat-messages::-webkit-scrollbar-thumb { background: #565869; border-radius: 5px; }
        
        @media (max-width: 500px) {
            #pasfreight-chat-window { width: 100%; height: 100%; bottom: 0; right: 0; border-radius: 0; }
            #pasfreight-chat-btn { bottom: 16px; right: 16px; }
        }
    </style>
</head>
<body>
    <button id="pasfreight-chat-btn">
        <span class="chat-icon">💬</span>
        <span class="notification-badge" id="notificationBadge" style="display: none;">1</span>
    </button>
    
    <div id="pasfreight-chat-window">
        <div class="chat-header">
            <div class="header-info">
                <div class="avatar">📦</div>
                <div class="header-text">
                    <h3>Aisea</h3>
                    <p>PAS Freight AI • 24/7</p>
                </div>
            </div>
            <button class="close-chat" id="closeChatBtn">✕</button>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="bubble">Hi, I'm Aisea - your logistics consultant. Tell me what you'd like to ship, and I'll help you figure out the best way.</div>
            </div>
        </div>
        
        <div class="service-buttons">
            <button class="service-btn" onclick="showImportMenu()">📥 IMPORT</button>
            <button class="service-btn" onclick="showExportMenu()">📤 EXPORT</button>
            <button class="service-btn" onclick="showCustoms()">📋 CUSTOMS</button>
            <button class="service-btn" onclick="showCargo()">🚚 CARGO</button>
            <button class="service-btn" onclick="showContact()">📞 CONTACT</button>
            <button class="service-btn" onclick="showAbout()">🏢 ABOUT</button>
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
        const closeChatBtn = document.getElementById('closeChatBtn');
        const notificationBadge = document.getElementById('notificationBadge');
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
        
        closeChatBtn.addEventListener('click', function() {
            chatWindow.style.display = 'none';
            isOpen = false;
        });
        
        setTimeout(function() {
            if (!isOpen && !notified) {
                notificationBadge.style.display = 'flex';
            }
        }, 30000);
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            div.innerHTML = `<div class="bubble">${text}</div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        }
        
        function addContactInfo(title, numbers, emails) {
            let html = `<div class="contact-info"><strong>${title}</strong><br>`;
            if (numbers && numbers.length) {
                numbers.forEach(num => { html += `📞 ${num}<br>`; });
            }
            if (emails && emails.length) {
                emails.forEach(email => { html += `✉️ ${email}<br>`; });
            }
            html += `</div>`;
            addMessage(html, false);
        }
        
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
        
        function showImportMenu() {
            addMessage("IMPORT", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📥 <strong>IMPORT - Select Mode:</strong><br>
                <div class="sub-buttons">
                    <button class="sub-btn" onclick="showImportAir()">✈️ AIR</button>
                    <button class="sub-btn" onclick="showImportSea()">🚢 SEA</button>
                </div>
            </div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        }
        
        function showImportAir() {
            addMessage("IMPORT - AIR", true);
            addContactInfo("IMPORT AIR FREIGHT", 
                ["+91 99869 42772", "+91 63615 21413"],
                ["gj@pasfreight.com", "rachana@pasfreight.com"]);
        }
        
        function showImportSea() {
            addMessage("IMPORT - SEA", true);
            addContactInfo("IMPORT SEA FREIGHT (FCL/LCL)", 
                ["+91 93648 81371", "+91 63615 21413"],
                ["vinodh@pasfreight.com", "gj@pasfreight.com"]);
        }
        
        function showExportMenu() {
            addMessage("EXPORT", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📤 <strong>EXPORT - Select Mode:</strong><br>
                <div class="sub-buttons">
                    <button class="sub-btn" onclick="showExportAir()">✈️ AIR</button>
                    <button class="sub-btn" onclick="showExportSea()">🚢 SEA</button>
                </div>
            </div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        }
        
        function showExportAir() {
            addMessage("EXPORT - AIR", true);
            addContactInfo("EXPORT AIR FREIGHT", 
                ["+91 93648 81371", "+91 63615 26659"],
                ["vinodh@pasfreight.com", "kavan@pasfreight.com"]);
        }
        
        function showExportSea() {
            addMessage("EXPORT - SEA", true);
            addContactInfo("EXPORT SEA FREIGHT", 
                ["+91 93648 81371", "+91 63615 26659"],
                ["vinodh@pasfreight.com", "kavan@pasfreight.com"]);
        }
        
        function showCustoms() {
            addMessage("CUSTOMS CLEARANCE", true);
            addContactInfo("CUSTOMS CLEARANCE", 
                ["+91 63615 26664"],
                ["ajith@pasfreight.com", "edi.blr@pasfreight.com"]);
        }
        
        function showCargo() {
            addMessage("CARGO", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">🚚 <strong>CARGO - Select Type:</strong><br>
                <div class="sub-buttons">
                    <button class="sub-btn" onclick="showDomesticCargo()">🇮🇳 DOMESTIC</button>
                    <button class="sub-btn" onclick="showInternationalCargo()">🌍 INTERNATIONAL</button>
                </div>
            </div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        }
        
        function showDomesticCargo() {
            addMessage("DOMESTIC CARGO", true);
            addContactInfo("DOMESTIC CARGO", 
                ["+91 63615 26659"],
                ["kavan@pasfreight.com", "info@pasfreight.com"]);
        }
        
        function showInternationalCargo() {
            addMessage("INTERNATIONAL CARGO", true);
            addContactInfo("INTERNATIONAL CARGO", 
                ["+91 63615 26659"],
                ["kavan@pasfreight.com", "info@pasfreight.com"]);
        }
        
        function showContact() {
            addMessage("CONTACT", true);
            addContactInfo("PAS FREIGHT CONTACT", 
                ["+91 90361 01201"],
                ["shivu@pasfreight.com", "info@pasfreight.com"]);
        }
        
        function showAbout() {
            addMessage("ABOUT", true);
            addMessage("🏢 <strong>PAS Freight Services Pvt Ltd</strong><br><br>📍 Jakkur-BDA, Bangalore<br>📞 +91 90361 01201<br>✉️ shivu@pasfreight.com<br>✅ WCA & GLA Certified<br>🌟 8+ years experience", false);
        }
        
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
        window.showCargo = showCargo;
        window.showDomesticCargo = showDomesticCargo;
        window.showInternationalCargo = showInternationalCargo;
        window.showContact = showContact;
        window.showAbout = showAbout;
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
    
    # Electronics (but check context)
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
    
    # Extract shipment details - one at a time, not all at once
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
    print("Aisea - 10/10 Premium Logistics Consultant")
    print("Open: http://localhost:5001")
    print("Features: Intent-accurate | Strong conversion | Premium enterprise replies")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
