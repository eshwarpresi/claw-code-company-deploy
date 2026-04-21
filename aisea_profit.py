import openai
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re
import json

app = Flask(__name__)
CORS(app)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

session_memory = {}

# Business intelligence constants
AIR_COST_PER_KG = 400
SEA_COST_PER_KG = 120
AIR_DAYS = 5
SEA_DAYS = 30
OPPORTUNITY_COST_PER_DAY = 2.5  # Rs per kg per day

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Aisea - PAS Freight Profit AI</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
        
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
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
            width: 20px;
            height: 20px;
            font-size: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            animation: blink 1s infinite;
        }
        @keyframes blink { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.7; transform: scale(1.1); } }
        
        #pasfreight-chat-window {
            position: fixed;
            bottom: 90px;
            right: 24px;
            width: 420px;
            height: 620px;
            background: white;
            border-radius: 24px;
            box-shadow: 0 24px 48px rgba(0,0,0,0.25);
            display: none;
            z-index: 999998;
            border: none;
            overflow: hidden;
            flex-direction: column;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 16px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header-info { display: flex; align-items: center; gap: 10px; }
        .avatar { width: 40px; height: 40px; background: rgba(255,255,255,0.15); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; }
        .header-text h3 { font-size: 16px; font-weight: 600; letter-spacing: -0.3px; }
        .header-text p { font-size: 10px; opacity: 0.8; margin-top: 2px; }
        .close-chat { background: rgba(255,255,255,0.1); border: none; color: white; font-size: 18px; cursor: pointer; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
        .close-chat:hover { background: rgba(255,255,255,0.2); transform: scale(1.05); }
        
        .chat-messages { flex: 1; overflow-y: auto; padding: 16px; background: #f7f9fc; }
        .message { margin-bottom: 16px; display: flex; animation: slideIn 0.3s ease; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
        .user-message { justify-content: flex-end; }
        .bot-message { justify-content: flex-start; }
        .bubble { max-width: 85%; padding: 10px 14px; border-radius: 20px; font-size: 13px; line-height: 1.45; font-weight: 400; }
        .user-message .bubble { background: #2a5298; color: white; border-bottom-right-radius: 5px; }
        .bot-message .bubble { background: white; color: #1a202c; border: 1px solid #e2e8f0; border-bottom-left-radius: 5px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        
        .suggestion-buttons { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
        .suggestion-btn { background: #f1f5f9; border: 1px solid #e2e8f0; padding: 6px 12px; border-radius: 20px; font-size: 11px; cursor: pointer; color: #1e3c72; font-weight: 500; transition: all 0.2s; }
        .suggestion-btn:hover { background: #2a5298; color: white; border-color: #2a5298; }
        
        .main-buttons { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
        .main-btn { background: #f1f5f9; color: #1e293b; border: none; padding: 8px 14px; border-radius: 24px; cursor: pointer; font-size: 12px; font-weight: 500; transition: all 0.2s; }
        .main-btn:hover { background: #2a5298; color: white; transform: translateY(-1px); }
        
        .sub-buttons { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px; }
        .sub-btn { background: #e9ecef; color: #495057; border: none; padding: 6px 12px; border-radius: 20px; cursor: pointer; font-size: 11px; font-weight: 500; transition: all 0.2s; }
        .sub-btn:hover { background: #2a5298; color: white; }
        
        .contact-info { background: #f8fafc; padding: 10px; border-radius: 12px; margin-top: 6px; font-size: 11px; border: 1px solid #e2e8f0; }
        
        .chat-input { padding: 12px 16px; background: white; border-top: 1px solid #e2e8f0; display: flex; gap: 10px; }
        .chat-input input { flex: 1; padding: 10px 16px; border: 1px solid #e2e8f0; border-radius: 28px; font-size: 13px; outline: none; font-family: 'Inter', sans-serif; transition: all 0.2s; }
        .chat-input input:focus { border-color: #2a5298; box-shadow: 0 0 0 3px rgba(42,82,152,0.1); }
        .chat-input button { background: #2a5298; color: white; border: none; width: 40px; height: 40px; border-radius: 50%; cursor: pointer; font-size: 18px; transition: all 0.2s; display: flex; align-items: center; justify-content: center; }
        .chat-input button:hover { background: #1e3c72; transform: scale(1.02); }
        
        .typing { display: inline-flex; gap: 5px; padding: 6px 0; }
        .typing span { width: 7px; height: 7px; background: #94a3b8; border-radius: 50%; animation: typingBounce 1.4s infinite; }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typingBounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-8px); } }
        
        .chat-messages::-webkit-scrollbar { width: 5px; }
        .chat-messages::-webkit-scrollbar-track { background: #e2e8f0; border-radius: 10px; }
        .chat-messages::-webkit-scrollbar-thumb { background: #94a3b8; border-radius: 10px; }
        
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
                    <p>PAS Freight Profit AI • 24/7</p>
                </div>
            </div>
            <button class="close-chat" id="closeChatBtn">✕</button>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="bubble">Hi, I'm Aisea - profit-first logistics advisor. Share your shipment details and margin for optimized strategy.</div>
            </div>
            <div class="message bot-message">
                <div class="bubble">
                    <div class="main-buttons">
                        <button class="main-btn" onclick="showImportOptions()">📥 IMPORT</button>
                        <button class="main-btn" onclick="showExportOptions()">📤 EXPORT</button>
                        <button class="main-btn" onclick="showCustoms()">📋 CUSTOMS</button>
                        <button class="main-btn" onclick="showCargo()">🚚 CARGO</button>
                        <button class="main-btn" onclick="showContact()">📞 CONTACT</button>
                        <button class="main-btn" onclick="showAbout()">🏢 ABOUT</button>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Ask Aisea about profit-optimized shipping..." autocomplete="off">
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
        
        function addSuggestionButtons() {
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">
                <div class="suggestion-buttons">
                    <button class="suggestion-btn" onclick="sendQuick('Optimize my profit')">💰 Optimize Profit</button>
                    <button class="suggestion-btn" onclick="sendQuick('Air vs sea math')">📊 Cost Math</button>
                    <button class="suggestion-btn" onclick="sendQuick('Scaling strategy')">📈 Scale</button>
                </div>
            </div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        }
        
        function sendQuick(text) {
            userInput.value = text;
            sendMessage();
        }
        
        function addContactInfo(title, numbers, emails) {
            let html = `<div class="contact-info"><strong>${title}</strong><br>`;
            if (numbers && numbers.length) numbers.forEach(num => { html += `📞 ${num}<br>`; });
            if (emails && emails.length) emails.forEach(email => { html += `✉️ ${email}<br>`; });
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
        
        window.showImportOptions = function() {
            addMessage("IMPORT", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📥 <strong>IMPORT - Select Mode:</strong><br>
                <div class="sub-buttons">
                    <button class="sub-btn" onclick="showImportAir()">✈️ AIR (3-7 days)</button>
                    <button class="sub-btn" onclick="showImportSea()">🚢 SEA (20-35 days)</button>
                </div>
            </div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        };
        
        window.showImportAir = function() { addMessage("IMPORT - AIR", true); addContactInfo("IMPORT AIR FREIGHT", ["+91 99869 42772", "+91 63615 21413"], ["gj@pasfreight.com", "rachana@pasfreight.com"]); };
        window.showImportSea = function() { addMessage("IMPORT - SEA", true); addContactInfo("IMPORT SEA FREIGHT", ["+91 93648 81371", "+91 63615 21413"], ["vinodh@pasfreight.com", "gj@pasfreight.com"]); };
        window.showExportOptions = function() { addMessage("EXPORT", true); const div = document.createElement('div'); div.className = 'message bot-message'; div.innerHTML = `<div class="bubble">📤 <strong>EXPORT - Select Mode:</strong><br><div class="sub-buttons"><button class="sub-btn" onclick="showExportAir()">✈️ AIR (3-7 days)</button><button class="sub-btn" onclick="showExportSea()">🚢 SEA (20-35 days)</button></div></div>`; messagesDiv.appendChild(div); div.scrollIntoView({ behavior: 'smooth' }); };
        window.showExportAir = function() { addMessage("EXPORT - AIR", true); addContactInfo("EXPORT AIR FREIGHT", ["+91 93648 81371", "+91 63615 26659"], ["vinodh@pasfreight.com", "kavan@pasfreight.com"]); };
        window.showExportSea = function() { addMessage("EXPORT - SEA", true); addContactInfo("EXPORT SEA FREIGHT", ["+91 93648 81371", "+91 63615 26659"], ["vinodh@pasfreight.com", "kavan@pasfreight.com"]); };
        window.showCustoms = function() { addMessage("CUSTOMS CLEARANCE", true); addContactInfo("CUSTOMS CLEARANCE", ["+91 63615 26664"], ["ajith@pasfreight.com", "edi.blr@pasfreight.com"]); };
        window.showCargo = function() { addMessage("CARGO", true); const div = document.createElement('div'); div.className = 'message bot-message'; div.innerHTML = `<div class="bubble">🚚 <strong>CARGO - Select Type:</strong><br><div class="sub-buttons"><button class="sub-btn" onclick="showDomesticCargo()">🇮🇳 DOMESTIC</button><button class="sub-btn" onclick="showInternationalCargo()">🌍 INTERNATIONAL</button></div></div>`; messagesDiv.appendChild(div); div.scrollIntoView({ behavior: 'smooth' }); };
        window.showDomesticCargo = function() { addMessage("DOMESTIC CARGO", true); addContactInfo("DOMESTIC CARGO", ["+91 63615 26659"], ["kavan@pasfreight.com", "info@pasfreight.com"]); };
        window.showInternationalCargo = function() { addMessage("INTERNATIONAL CARGO", true); addContactInfo("INTERNATIONAL CARGO", ["+91 63615 26659"], ["kavan@pasfreight.com", "info@pasfreight.com"]); };
        window.showContact = function() { addMessage("CONTACT", true); addContactInfo("PAS FREIGHT CONTACT", ["+91 90361 01201"], ["shivu@pasfreight.com", "info@pasfreight.com"]); };
        window.showAbout = function() { addMessage("ABOUT", true); addMessage("🏢 <strong>PAS Freight Services Pvt Ltd</strong><br><br>📍 Jakkur-BDA, Bangalore<br>📞 +91 90361 01201<br>✅ WCA & GLA Certified<br>🌟 8+ years experience", false); };
        
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
                addSuggestionButtons();
            } catch(error) {
                hideTyping();
                addMessage('Call +91 90361 01201 for assistance.', false);
            }
        }
        
        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', function(e) { if (e.key === 'Enter') sendMessage(); });
    </script>
</body>
</html>
'''

def calculate_profit_math(margin, weight, days_saved=None):
    """Calculate profit impact of shipping decisions"""
    air_profit = margin - AIR_COST_PER_KG
    sea_profit = margin - SEA_COST_PER_KG
    
    if days_saved:
        opportunity_saved = days_saved * OPPORTUNITY_COST_PER_DAY
        air_profit += opportunity_saved
    
    return {
        'air_profit': air_profit,
        'sea_profit': sea_profit,
        'air_viable': air_profit > 0,
        'sea_viable': sea_profit > 0,
        'better_option': 'air' if air_profit > sea_profit else 'sea',
        'loss_air': air_profit < 0,
        'loss_amount_air': abs(air_profit) if air_profit < 0 else 0
    }

def detect_intent(user_msg):
    msg_lower = user_msg.lower()
    
    dangerous = ['lithium', 'battery', 'chemical', 'acid', 'flammable', 'explosive', 'hazardous']
    for d in dangerous:
        if d in msg_lower:
            return 'compliance'
    
    profit_keywords = ['profit', 'margin', 'optimize', 'maximize', 'roi', 'money', 'cost vs benefit']
    for p in profit_keywords:
        if p in msg_lower:
            return 'profit'
    
    strategy = ['strategy', 'scale', 'monthly', 'weekly', 'regular', 'optimize', 'reduce cost', 'save money']
    for s in strategy:
        if s in msg_lower:
            return 'strategy'
    
    quote = ['quote', 'price', 'cost', 'rate', 'how much', 'expensive', 'cheap', 'pricing']
    for q in quote:
        if q in msg_lower:
            return 'quote'
    
    beginner = ["don't know", "no idea", "first time", "new to", "help me", "guide me"]
    for b in beginner:
        if b in msg_lower:
            return 'beginner'
    
    return 'advisor'

def update_context(user_msg, ctx):
    new_ctx = ctx.copy()
    
    weight_match = re.search(r'(\d+)\s*(?:kg|kgs|kilogram|kilo|ton)', user_msg, re.IGNORECASE)
    if weight_match:
        new_ctx['weight'] = int(weight_match.group(1))
    
    dest_match = re.search(r'(?:to|for|from|change to)\s+([A-Z][a-z]+|[A-Z]{2})', user_msg, re.IGNORECASE)
    if dest_match:
        new_ctx['destination'] = dest_match.group(1)
    
    if 'urgent' in user_msg.lower():
        new_ctx['urgency'] = 'urgent'
    
    cargo_types = ['electronics', 'garments', 'medicine', 'food', 'machinery']
    for ct in cargo_types:
        if ct in user_msg.lower():
            new_ctx['cargo'] = ct
    
    margin_match = re.search(r'margin[:\s]*([0-9]+)', user_msg, re.IGNORECASE)
    if margin_match:
        new_ctx['margin'] = int(margin_match.group(1))
    
    if 'weekly' in user_msg.lower():
        new_ctx['frequency'] = 'weekly'
    elif 'monthly' in user_msg.lower():
        new_ctx['frequency'] = 'monthly'
    
    return new_ctx

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if session_id not in session_memory:
        session_memory[session_id] = {'weight': None, 'destination': None, 'cargo': None, 'urgency': None, 'margin': None, 'frequency': None}
    
    session_memory[session_id] = update_context(user_msg, session_memory[session_id])
    ctx = session_memory[session_id]
    intent = detect_intent(user_msg)
    
    # Calculate profit math if margin exists
    profit_math = None
    if ctx.get('margin'):
        weight = ctx.get('weight', 1)
        profit_math = calculate_profit_math(ctx['margin'], weight)
    
    context_display = f"Weight: {ctx.get('weight', '?')}kg, Destination: {ctx.get('destination', '?')}, Cargo: {ctx.get('cargo', 'general')}"
    if ctx.get('margin'):
        context_display += f", Margin: Rs.{ctx['margin']}/kg"
        if profit_math and profit_math['loss_air']:
            context_display += f" ⚠️ AIR WOULD LOSE Rs.{profit_math['loss_amount_air']}/kg"
    if ctx.get('frequency'):
        context_display += f", Frequency: {ctx['frequency']}"
    
    if intent == 'profit' and ctx.get('margin'):
        profit_advice = ""
        if profit_math['loss_air']:
            profit_advice = f"CRITICAL: Your margin (Rs.{ctx['margin']}/kg) is LOWER than air cost (Rs.{AIR_COST_PER_KG}/kg). Air freight would LOSE Rs.{profit_math['loss_amount_air']}/kg. Sea freight gives profit Rs.{profit_math['sea_profit']}/kg. Recommend: 100% sea freight OR negotiate air rates OR increase selling price."
        else:
            profit_advice = f"Air profit: Rs.{profit_math['air_profit']}/kg, Sea profit: Rs.{profit_math['sea_profit']}/kg. Recommended: {profit_math['better_option'].upper()} freight for higher profit."
        
        prompt = f"""You are Aisea, profit-optimizing logistics advisor.

{profit_advice}

Current: {context_display}

Give ONE clear profit-maximizing recommendation. Be direct. Use numbers."""
    
    elif intent == 'strategy':
        prompt = f"""You are Aisea, logistics strategist.

User wants strategy for: {context_display}

Think like a business consultant:
- If weekly shipments: suggest consolidation and contract rates
- If scaling: recommend 70/30 split based on demand pattern
- Consider inventory cycles and cash flow

Give specific percentages and reasoning. Keep response short (3-4 lines)."""
    
    elif intent == 'quote':
        prompt = f"""You are Aisea, logistics advisor.

Current: {context_display}

Give estimated pricing with profit impact if margin known.
Keep SHORT (3 lines max)."""
    
    elif intent == 'beginner':
        prompt = f"""You are Aisea, logistics expert.

User is new to shipping.

Guide them with 3 simple questions:
1. What are you sending?
2. Approx weight?
3. Where to?

Keep response warm and short (2-3 lines)."""
    
    elif intent == 'compliance':
        prompt = f"""You are Aisea, logistics expert.

DANGEROUS GOODS detected.

Do NOT give pricing. Explain restrictions. Ask for MSDS and UN packaging.

Keep response short (3 lines max)."""
    
    else:
        prompt = f"""You are Aisea, profit-first logistics advisor.

Current: {context_display}

Give decision advice with profit reasoning. Keep SHORT (3 lines max).

If margin is lower than air cost, clearly state air is NOT viable.
Recommend specific split percentages when relevant.
Be confident and direct."""

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=180,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'Call +91 90361 01201. Error: {str(e)}'})

if __name__ == '__main__':
    print("=" * 60)
    print("Aisea - Profit-Optimized Logistics AI (10/10 Target)")
    print("Open: http://localhost:5001")
    print("Features: Margin-aware | Profit math | Split recommendations")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
