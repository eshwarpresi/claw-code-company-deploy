import openai
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

user_sessions = {}

# Valid countries list
VALID_COUNTRIES = ['germany', 'usa', 'uk', 'dubai', 'singapore', 'china', 'japan', 'canada', 'australia', 'france', 'italy', 'spain']

# Country mapping
COUNTRY_MAP = {
    'hamburg': 'Germany', 'berlin': 'Germany', 'munich': 'Germany', 'frankfurt': 'Germany',
    'dubai': 'UAE', 'abudhabi': 'UAE', 'sharjah': 'UAE',
    'singapore': 'Singapore', 'tokyo': 'Japan', 'osaka': 'Japan',
    'shanghai': 'China', 'beijing': 'China', 'shenzhen': 'China',
    'newyork': 'USA', 'losangeles': 'USA', 'chicago': 'USA', 'texas': 'USA',
    'toronto': 'Canada', 'vancouver': 'Canada', 'montreal': 'Canada',
    'sydney': 'Australia', 'melbourne': 'Australia', 'perth': 'Australia'
}

def calculate_price(weight_kg, mode, cargo_type="general"):
    if mode == "air":
        if cargo_type == "electronics":
            rate = 420
        elif cargo_type == "dangerous":
            rate = 550
        else:
            rate = 320
        days = "3-5 days"
    else:
        if weight_kg > 1000:
            rate = 60
        elif weight_kg > 500:
            rate = 80
        else:
            rate = 120
        days = "22-30 days"
    total = weight_kg * rate
    return total, rate, days

def is_valid_destination(dest):
    if not dest:
        return False
    dest_lower = dest.lower()
    return dest_lower in VALID_COUNTRIES or dest_lower in [c.lower() for c in COUNTRY_MAP.keys()]

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Aisea - PAS Freight AI</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f7fb; }
        
        #chat-btn {
            position: fixed; bottom: 24px; right: 24px; width: 56px; height: 56px;
            background: linear-gradient(135deg, #1e3c72, #2a5298); border-radius: 50%;
            cursor: pointer; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            display: flex; align-items: center; justify-content: center;
            transition: all 0.2s; border: none; z-index: 9999;
        }
        #chat-btn:hover { transform: scale(1.05); }
        .chat-icon { font-size: 26px; color: white; }
        
        #chat-window {
            position: fixed; bottom: 90px; right: 24px; width: 380px; height: 520px;
            background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            display: none; z-index: 9998; flex-direction: column; overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #1e3c72, #2a5298); color: white;
            padding: 12px 16px; display: flex; justify-content: space-between; align-items: center;
        }
        .chat-header h3 { font-size: 15px; }
        .close-btn {
            background: none; border: none; color: white; font-size: 18px;
            cursor: pointer; width: 28px; height: 28px; border-radius: 50%;
        }
        .close-btn:hover { background: rgba(255,255,255,0.2); }
        
        .chat-messages {
            flex: 1; overflow-y: auto; padding: 16px; background: #f7f9fc;
        }
        
        .message { margin-bottom: 12px; display: flex; }
        .user-message { justify-content: flex-end; }
        .bot-message { justify-content: flex-start; }
        
        .bubble {
            max-width: 80%; padding: 8px 12px; border-radius: 18px; font-size: 13px; line-height: 1.4;
            white-space: pre-line;
        }
        .user-message .bubble {
            background: #2a5298; color: white; border-bottom-right-radius: 4px;
        }
        .bot-message .bubble {
            background: white; color: #333; border: 1px solid #e0e0e0; border-bottom-left-radius: 4px;
        }
        
        .quick-buttons {
            display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;
        }
        .quick-btn {
            background: #f0f2f5; border: none; padding: 6px 12px; border-radius: 20px;
            font-size: 11px; cursor: pointer;
        }
        .quick-btn:hover { background: #2a5298; color: white; }
        
        .chat-input {
            padding: 12px; background: white; border-top: 1px solid #e0e0e0;
            display: flex; gap: 8px;
        }
        .chat-input input {
            flex: 1; padding: 10px 12px; border: 1px solid #ddd; border-radius: 25px;
            font-size: 13px; outline: none;
        }
        .chat-input button {
            background: #2a5298; color: white; border: none; width: 38px; height: 38px;
            border-radius: 50%; cursor: pointer; font-size: 16px;
        }
        
        .typing {
            display: inline-flex; gap: 4px; padding: 4px 0;
        }
        .typing span {
            width: 6px; height: 6px; background: #999; border-radius: 50%;
            animation: typingBounce 1.4s infinite;
        }
        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }
        
        @media (max-width: 500px) {
            #chat-window { width: 100%; height: 100%; bottom: 0; right: 0; border-radius: 0; }
            #chat-btn { bottom: 16px; right: 16px; }
        }
    </style>
</head>
<body>
    <button id="chat-btn"><span class="chat-icon">💬</span></button>
    
    <div id="chat-window">
        <div class="chat-header">
            <h3>📦 Aisea - Logistics AI</h3>
            <button class="close-btn" id="close-btn">✕</button>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="bubble">Hi, I'm Aisea. Share your shipment details (weight, destination, cargo) for instant quotes.</div>
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="e.g., 500 kg garments to Dubai" autocomplete="off">
            <button id="send-btn">➤</button>
        </div>
    </div>

    <script>
        const chatBtn = document.getElementById('chat-btn');
        const chatWindow = document.getElementById('chat-window');
        const closeBtn = document.getElementById('close-btn');
        const messagesDiv = document.getElementById('chatMessages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('send-btn');
        
        let sessionId = 'session_' + Date.now();
        let isOpen = false;
        
        chatBtn.onclick = () => {
            if (isOpen) {
                chatWindow.style.display = 'none';
                isOpen = false;
            } else {
                chatWindow.style.display = 'flex';
                isOpen = true;
            }
        };
        
        closeBtn.onclick = () => {
            chatWindow.style.display = 'none';
            isOpen = false;
        };
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            div.innerHTML = `<div class="bubble">${text}</div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
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
        
        sendBtn.onclick = sendMessage;
        userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendMessage(); });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '').lower()
    session_id = data.get('session_id', 'default')
    
    if session_id not in user_sessions:
        user_sessions[session_id] = {'weight': None, 'destination': None, 'cargo': 'general', 'phone': None, 'country': None}
    
    session_data = user_sessions[session_id]
    
    # ========== SPECIAL HANDLERS ==========
    
    if 'lithium' in user_msg or 'battery' in user_msg:
        reply = "⚠️ Lithium batteries are classified as dangerous goods.\n\nShipping requires:\n• UN-certified packaging\n• MSDS documentation\n• Airline approval\n\nShare battery type for compliance check."
        return jsonify({'reply': reply})
    
    if 'why choose' in user_msg or 'why should i choose' in user_msg:
        reply = "✅ Best rates in industry\n✅ 8+ years experience\n✅ WCA & GLA certified\n✅ 24/7 support\n✅ Door-to-door tracking\n\nWant a quote to compare?"
        return jsonify({'reply': reply})
    
    if 'contract' in user_msg or 'regular shipment' in user_msg:
        reply = "📋 We offer contract pricing for regular shipments.\n\nShare your monthly volume & destinations—our team will prepare a custom rate sheet."
        return jsonify({'reply': reply})
    
    # Extract weight
    weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilogram)', user_msg)
    if weight_match:
        weight = float(weight_match.group(1))
        if weight > 10000:
            reply = "📦 For bulk shipments over 10,000 kg, please contact our team directly for special pricing.\n\n📞 Call +91 90361 01201"
            return jsonify({'reply': reply})
        session_data['weight'] = weight
    
    # Extract destination
    dest_match = None
    for city, country in COUNTRY_MAP.items():
        if city in user_msg:
            dest_match = city
            session_data['destination'] = city.title()
            session_data['country'] = country
            break
    
    if not dest_match:
        for country in VALID_COUNTRIES:
            if country in user_msg:
                session_data['destination'] = country.title()
                session_data['country'] = country.title()
                break
    
    # Extract cargo
    cargo_types = ['electronics', 'garments', 'clothes', 'machinery', 'documents', 'furniture', 'pharma']
    for cargo in cargo_types:
        if cargo in user_msg:
            session_data['cargo'] = cargo
            break
    
    # Extract phone
    phone_match = re.search(r'\d{10}', user_msg)
    if phone_match:
        session_data['phone'] = phone_match.group(0)
    
    # Validate destination
    if session_data['destination'] and not is_valid_destination(session_data['destination'].lower()):
        session_data['destination'] = None
        reply = "🌍 Please enter a valid destination (Germany, USA, UK, Dubai, Singapore, Canada, etc.)"
        return jsonify({'reply': reply})
    
    # ========== QUOTE LOGIC ==========
    
    has_weight = session_data['weight'] is not None
    has_dest = session_data['destination'] is not None
    cargo = session_data.get('cargo', 'general')
    
    if has_weight and has_dest:
        weight = session_data['weight']
        dest = session_data['destination']
        
        air_total, air_rate, air_days = calculate_price(weight, "air", cargo)
        sea_total, sea_rate, sea_days = calculate_price(weight, "sea", cargo)
        
        reply = f"✅ Got it — {int(weight)} kg {cargo} to {dest}\n\n"
        reply += f"✈️ Air: ₹{air_rate}/kg → ₹{int(air_total):,} ({air_days})\n"
        reply += f"🚢 Sea: ₹{sea_rate}/kg → ₹{int(sea_total):,} ({sea_days})\n\n"
        
        if cargo == 'electronics':
            reply += "📱 For electronics, air freight is recommended for safety.\n\n"
        elif cargo == 'garments' or cargo == 'clothes':
            reply += "👕 Sea freight is economical for garments.\n\n"
        
        reply += "Share your phone number for best rates."
        return jsonify({'reply': reply})
    
    # ========== MISSING INFO ==========
    
    if user_msg.strip() in ['rate', 'price', 'cost', 'quote']:
        if has_weight and has_dest:
            weight = session_data['weight']
            dest = session_data['destination']
            total = weight * 320
            return jsonify({'reply': f"💰 {int(weight)} kg to {dest}: ₹{int(total):,} (air estimate). Want sea option?"})
        else:
            missing = []
            if not has_weight: missing.append("weight")
            if not has_dest: missing.append("destination")
            return jsonify({'reply': f"Share your {', '.join(missing)} for a quick quote."})
    
    if 'service' in user_msg:
        reply = """📦 Our services:\n• Air Freight (3-5 days)\n• Sea Freight (22-30 days)\n• Customs Clearance\n• Door-to-Door Delivery\n• Warehousing\n\nWhich service do you need?"""
        return jsonify({'reply': reply})
    
    if 'contact' in user_msg or 'phone' in user_msg:
        reply = "📞 Call: +91 90361 01201\n✉️ Email: shivu@pasfreight.com\n📍 Bangalore, India\n⏰ Available 24/7"
        return jsonify({'reply': reply})
    
    if 'address' in user_msg:
        reply = "📍 PAS Freight Services\nSite No:171, Arkavathey Layout, Jakkur-BDA\nBangalore - 560092, India"
        return jsonify({'reply': reply})
    
    if 'about' in user_msg or 'company' in user_msg:
        reply = "🏢 PAS Freight Services Pvt Ltd\n\n✅ WCA & GLA Certified\n🌟 8+ years experience\n🌍 Serving 50+ countries\n📦 10,000+ shipments delivered\n\nNeed a quote?"
        return jsonify({'reply': reply})
    
    missing = []
    if not has_weight:
        missing.append("weight")
    if not has_dest:
        missing.append("destination")
    
    if missing:
        reply = f"Got it. Just need your {', '.join(missing)} to give you an instant quote."
    else:
        reply = "Share your shipment details (weight, destination, cargo type) for an instant quote."
    
    return jsonify({'reply': reply})

if __name__ == '__main__':
    print("=" * 60)
    print("✨ Aisea - 9/10 SaaS Logistics Assistant")
    print("📱 Open: http://localhost:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
