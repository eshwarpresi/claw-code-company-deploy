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

def detect_intent(user_msg, ctx):
    msg_lower = user_msg.lower()
    
    # Intent: Cost/Cheapest
    if any(word in msg_lower for word in ['cheapest', 'cost', 'budget', 'save money', 'lowest price', 'affordable']):
        return 'cost'
    
    # Intent: Urgent/Fast
    if any(word in msg_lower for word in ['urgent', 'fast', 'quick', '2 days', '3 days', 'express', 'asap']):
        return 'urgent'
    
    # Intent: Bulk/Regular shipments
    if any(word in msg_lower for word in ['bulk', 'monthly', 'weekly', 'regular', 'volume', 'frequent']):
        return 'bulk'
    
    # Intent: Customs/Problem
    if any(word in msg_lower for word in ['customs', 'clearance', 'document', 'duty', 'tax', 'problem', 'stuck', 'delay']):
        return 'customs'
    
    # Intent: Safety/Trust
    if any(word in msg_lower for word in ['safe', 'damage', 'insurance', 'protect', 'reliable', 'trust']):
        return 'trust'
    
    # Intent: Electronics (but with context)
    if 'electronics' in msg_lower:
        if ctx.get('intent') == 'cost':
            return 'electronics_cost'
        elif ctx.get('intent') == 'urgent':
            return 'electronics_urgent'
        else:
            return 'electronics'
    
    return 'general'

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if session_id not in session_memory:
        session_memory[session_id] = {'cargo_type': None, 'destination': None, 'weight': None, 'intent': None}
    
    ctx = session_memory[session_id]
    intent = detect_intent(user_msg, ctx)
    ctx['intent'] = intent
    
    # Extract cargo type if mentioned
    cargo_map = {
        'electronics': 'electronics',
        'garments': 'garments',
        'clothes': 'garments',
        'medicine': 'medicine',
        'food': 'food',
        'machinery': 'machinery'
    }
    for key, value in cargo_map.items():
        if key in user_msg.lower():
            ctx['cargo_type'] = value
            break
    
    # INTENT-BASED RESPONSES
    if intent == 'cost':
        response = """If cost is your priority 👍

🚢 Sea freight is more economical, but takes longer (20-30 days).

Since you mentioned electronics, if they're not urgent, sea can save cost.

If you need a balance, we can also check the best available air option.

What's your approximate weight and destination?"""
    
    elif intent == 'urgent':
        response = """For urgent delivery 👍

We'll need to check express air freight options.

It depends on flight availability and destination, but we can try priority handling.

Let me check what's possible for your route. Can you share the destination and weight?"""
    
    elif intent == 'bulk':
        response = """Yes 👍 we handle regular and bulk shipments.

For monthly shipments, we can offer:
✔️ Better pricing
✔️ Dedicated support
✔️ Priority space planning

Let me understand your volume so I can suggest the best setup. How many kg per month?"""
    
    elif intent == 'customs':
        response = """That's a common concern 👍

We handle customs clearance with proper documentation and compliance to avoid delays.

Our team also guides you on required documents in advance to ensure smooth clearance.

Need help with a specific shipment?"""
    
    elif intent == 'trust':
        response = """Great question 👍

We ensure safety through:
✔️ Real-time tracking
✔️ Insurance coverage
✔️ Proper packaging guidance
✔️ Reliable carriers

Your shipment is fully protected throughout the journey. Would you like to know more?"""
    
    elif intent == 'electronics_cost':
        response = """For electronics on a budget 👍

While air is recommended for electronics safety, sea freight can work if:
• Goods are well-packaged
• Not extremely urgent
• You accept slightly longer transit (20-30 days)

What's your weight and destination? I can check both options for you."""
    
    elif intent == 'electronics_urgent':
        response = """For urgent electronics 👍

✈️ Air freight is definitely the right choice:
• 3-7 days delivery
• Better handling for sensitive goods
• Full tracking

Share your destination and weight - I'll check the best available rates."""
    
    elif intent == 'electronics':
        response = """Electronics need extra care 👍

✈️ Air freight is recommended for electronics because:
• Faster transit (3-7 days)
• Better handling
• Lower risk of damage

What's the approximate weight and destination?"""
    
    else:
        # General response using AI
        system_prompt = """You are Aisea, a logistics consultant for PAS Freight.

Rules:
- Be conversational and helpful
- Understand what user wants to ship
- Suggest air for urgent/valuable items
- Suggest sea for cost-saving/bulk
- Ask for missing details naturally
- Never repeat the same question

Company: PAS Freight, Contact: +91 90361 01201

Be smart, helpful, and conversational."""
        
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
            response = response['choices'][0]['message']['content']
        except Exception as e:
            response = "Tell me what you want to ship - I'll help you figure out the best way."
    
    session_memory[session_id] = ctx
    return jsonify({'reply': response})

if __name__ == '__main__':
    print("=" * 60)
    print("Aisea - Intent-Aware Logistics Consultant")
    print("Open: http://localhost:5001")
    print("Intents: Cost | Urgent | Bulk | Customs | Trust | Electronics")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
