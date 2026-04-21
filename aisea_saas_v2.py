import openai
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

user_sessions = {}

# Country mapping
country_map = {
    'hamburg': 'Germany', 'berlin': 'Germany', 'munich': 'Germany', 'frankfurt': 'Germany',
    'dubai': 'UAE', 'abudhabi': 'UAE', 'sharjah': 'UAE',
    'singapore': 'Singapore', 'tokyo': 'Japan', 'osaka': 'Japan',
    'shanghai': 'China', 'beijing': 'China', 'shenzhen': 'China',
    'newyork': 'USA', 'losangeles': 'USA', 'chicago': 'USA', 'texas': 'USA'
}

def calculate_price(weight_kg, mode, cargo_type="", destination=""):
    if mode == "air":
        rate = 420 if cargo_type == "electronics" else 320
        days = "3-5 days"
    else:
        rate = 80 if weight_kg > 500 else 120
        days = "22-30 days"
    total = weight_kg * rate
    return total, rate, days

def extract_shipments(text):
    pattern = r'(\d+)\s*kg\s*(?:to\s*)?([a-zA-Z\s]+?)(?=\d+kg|$|\.|\,)'
    matches = re.findall(pattern, text.lower())
    shipments = []
    for weight, dest in matches:
        dest = dest.strip()
        country = country_map.get(dest, dest.title())
        shipments.append({'weight': int(weight), 'destination': dest, 'country': country})
    return shipments

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
            <input type="text" id="userInput" placeholder="e.g., 280 kg electronics to Hamburg" autocomplete="off">
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
        user_sessions[session_id] = {'weight': None, 'destination': None, 'cargo': None, 'phone': None, 'country': None}
    
    session_data = user_sessions[session_id]
    
    # Handle urgency
    urgency_keywords = ['urgent', 'fast', 'quick', 'asap', 'emergency', 'next friday', 'this week']
    if any(word in user_msg for word in urgency_keywords):
        reply = "🚀 For urgent delivery, air freight is best (3-5 days). Share weight & destination to lock fastest option."
        return jsonify({'reply': reply})
    
    # Extract multiple shipments
    shipments = extract_shipments(user_msg)
    if len(shipments) > 1:
        total_cost = 0
        breakdown = []
        for s in shipments:
            cost = s['weight'] * 320  # air rate
            total_cost += cost
            breakdown.append(f"• {s['weight']} kg to {s['destination']}: ₹{cost:,}")
        reply = "📦 Multiple shipments detected:\n\n" + "\n".join(breakdown)
        reply += f"\n\n💰 Total estimated air cost: ₹{total_cost:,}\n\nWant cheapest option breakdown?"
        return jsonify({'reply': reply})
    
    # Extract single shipment details
    weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilogram)', user_msg)
    if weight_match:
        session_data['weight'] = float(weight_match.group(1))
    
    # Extract destination with mapping
    dest_match = None
    for city, country in country_map.items():
        if city in user_msg:
            dest_match = city
            session_data['destination'] = city.title()
            session_data['country'] = country
            break
    
    if not dest_match:
        for country in ['germany', 'usa', 'uk', 'dubai', 'singapore', 'china', 'japan', 'australia']:
            if country in user_msg:
                session_data['destination'] = country.title()
                session_data['country'] = country.title()
                break
    
    # Extract cargo
    cargo_types = ['electronics', 'clothes', 'machinery', 'documents', 'spare parts', 'furniture', 'food']
    for cargo in cargo_types:
        if cargo in user_msg:
            session_data['cargo'] = cargo
            break
    
    # Extract phone
    phone_match = re.search(r'\d{10}', user_msg)
    if phone_match:
        session_data['phone'] = phone_match.group(0)
    
    # Check if we have all data
    has_weight = session_data['weight'] is not None
    has_dest = session_data['destination'] is not None
    
    # Smart response based on available data
    if has_weight and has_dest:
        weight = session_data['weight']
        dest = session_data['destination']
        country = session_data.get('country', dest)
        cargo = session_data.get('cargo', 'general cargo')
        
        air_total, air_rate, air_days = calculate_price(weight, "air", cargo, country)
        sea_total, sea_rate, sea_days = calculate_price(weight, "sea", cargo, country)
        
        reply = f"✅ Got it — {int(weight)} kg {cargo} to {dest}\n\n"
        reply += f"✈️ Air: ₹{air_rate}/kg → ₹{int(air_total):,} ({air_days})\n"
        reply += f"🚢 Sea: ₹{sea_rate}/kg → ₹{int(sea_total):,} ({sea_days})\n\n"
        
        if cargo == 'electronics':
            reply += "📱 For electronics, air freight is safer & faster.\n\n"
        
        reply += "Want me to lock the best rate? Share your phone number."
        
        # Add customs note if mentioned
        if 'customs' in user_msg:
            reply += "\n\n📋 Customs clearance can be arranged. Add ~₹5,000-15,000 depending on value."
        
        return jsonify({'reply': reply})
    
    elif has_weight and not has_dest:
        reply = f"📦 {int(session_data['weight'])} kg — got it. Where are you shipping to?"
        return jsonify({'reply': reply})
    
    elif has_dest and not has_weight:
        reply = f"📍 Shipping to {session_data['destination']}. What's the weight?"
        return jsonify({'reply': reply})
    
    # Handle "rate" / "price" quick query
    if user_msg.strip() in ['rate', 'price', 'cost', 'quote']:
        if has_weight and has_dest:
            weight = session_data['weight']
            dest = session_data['destination']
            total = weight * 320
            return jsonify({'reply': f"💰 {int(weight)} kg to {dest}: ₹{int(total):,} (air estimate). Want sea option too?"})
        else:
            missing = []
            if not has_weight: missing.append("weight")
            if not has_dest: missing.append("destination")
            return jsonify({'reply': f"Share your {', '.join(missing)} for a quick quote."})
    
    # Handle services
    if 'service' in user_msg:
        reply = """📦 Our services:
• Air Freight (3-5 days)
• Sea Freight (22-30 days)
• Customs Clearance
• Door-to-Door Delivery
• Warehousing

Which service do you need?"""
        return jsonify({'reply': reply})
    
    # Handle contact
    if 'contact' in user_msg or 'phone' in user_msg:
        reply = "📞 Call: +91 90361 01201\n✉️ Email: shivu@pasfreight.com\n📍 Bangalore, India\nAvailable 24/7"
        return jsonify({'reply': reply})
    
    # Default - ask intelligently
    missing = []
    if not has_weight:
        missing.append("weight")
    if not has_dest:
        missing.append("destination")
    
    if missing:
        reply = f"Got your request. Just need your {', '.join(missing)} to give you an instant quote."
    else:
        reply = "Share your shipment details (weight, destination, cargo type) for an instant quote."
    
    return jsonify({'reply': reply})

if __name__ == '__main__':
    print("=" * 60)
    print("✨ Aisea - SaaS Level Logistics Assistant")
    print("📱 Open: http://localhost:5001")
    print("🚀 Features: Multi-shipment | Urgency detection | Smart extraction")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
