import openai
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

user_sessions = {}

VALID_COUNTRIES = ['germany', 'usa', 'uk', 'dubai', 'singapore', 'china', 'japan', 'canada', 'australia', 'france', 'italy', 'spain']

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

def get_recommendation(weight, cargo, is_urgent=False, want_cheap=False):
    """Intelligent recommendation based on user needs"""
    if is_urgent:
        return "air", "For urgent delivery, air freight is your only option. It reaches in 3-5 days."
    elif want_cheap:
        return "sea", "For cost savings, sea freight is better. It saves about 60-70% compared to air."
    elif cargo == "electronics":
        return "air", "For electronics, air freight is recommended due to safety and handling requirements."
    elif cargo in ["garments", "clothes", "furniture"]:
        return "sea", "For garments/furniture, sea freight is economical. Air is faster but costs significantly more."
    elif weight > 500:
        return "sea", f"For {int(weight)} kg, sea freight is more economical. Air would cost significantly more."
    else:
        return None, "What's your priority - speed or cost savings?"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Aisea - Smart Logistics Advisor</title>
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
            <h3>📦 Aisea - Smart Logistics Advisor</h3>
            <button class="close-btn" id="close-btn">✕</button>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="bubble">Hi, I'm Aisea - your smart logistics advisor. Share your shipment details, and I'll help you choose the best option.</div>
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="e.g., 400 kg to USA or I don't know where to start" autocomplete="off">
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
        let showPhonePrompt = false;
        let phoneAskedCount = 0;
        
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
                    body: JSON.stringify({ message: text, session_id: sessionId, show_phone: showPhonePrompt, phone_count: phoneAskedCount })
                });
                const data = await response.json();
                hideTyping();
                addMessage(data.reply, false);
                showPhonePrompt = data.show_phone || false;
                phoneAskedCount = data.phone_count || 0;
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
    show_phone_prompt = data.get('show_phone', False)
    phone_asked_count = data.get('phone_count', 0)
    
    if session_id not in user_sessions:
        user_sessions[session_id] = {'weight': None, 'destination': None, 'cargo': None, 'phone': None, 'country': None}
    
    session_data = user_sessions[session_id]
    
    # ========== HANDLE CORRECTIONS ==========
    if 'actually' in user_msg or 'correction' in user_msg or 'instead' in user_msg:
        # Clear and re-extract
        session_data['weight'] = None
        session_data['destination'] = None
        session_data['cargo'] = None
    
    # Extract weight
    weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilogram)', user_msg)
    if weight_match:
        new_weight = float(weight_match.group(1))
        old_weight = session_data['weight']
        session_data['weight'] = new_weight
        if old_weight and old_weight != new_weight:
            return jsonify({'reply': f"✅ Updated to {int(new_weight)} kg. What else? Share destination.", 'show_phone': False, 'phone_count': 0})
    
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
    
    # Extract cargo - ONLY if user explicitly mentions
    cargo_types = ['electronics', 'garments', 'clothes', 'machinery', 'documents', 'furniture', 'pharma']
    cargo_mentioned = False
    for cargo in cargo_types:
        if cargo in user_msg:
            session_data['cargo'] = cargo
            cargo_mentioned = True
            break
    
    # Extract phone
    phone_match = re.search(r'\d{10}', user_msg)
    if phone_match:
        session_data['phone'] = phone_match.group(0)
        return jsonify({'reply': "✅ Thanks! Our team will call you within 10 minutes with the best rates.", 'show_phone': False, 'phone_count': 0})
    
    # ========== SPECIAL HANDLERS ==========
    
    # Beginner guide
    if 'dont know' in user_msg or "don't know" in user_msg or "no idea" in user_msg:
        reply = "No problem — I'll guide you. 📦\n\nDo you want:\n• Fastest delivery (3-5 days)\n• Cheapest option (22-30 days)\n\nOr tell me your weight and destination."
        return jsonify({'reply': reply, 'show_phone': False, 'phone_count': 0})
    
    # Decision questions
    if 'worth it' in user_msg or 'should i choose' in user_msg or 'is air worth' in user_msg or 'is sea worth' in user_msg:
        if session_data['weight'] and session_data['destination']:
            weight = session_data['weight']
            dest = session_data['destination']
            cargo = session_data.get('cargo', 'general')
            
            air_total, air_rate, air_days = calculate_price(weight, "air", cargo)
            sea_total, sea_rate, sea_days = calculate_price(weight, "sea", cargo)
            
            diff = air_total - sea_total
            reply = f"📊 For {int(weight)} kg to {dest}:\n\n"
            reply += f"✈️ Air: ₹{int(air_total):,} | {air_days}\n"
            reply += f"🚢 Sea: ₹{int(sea_total):,} | {sea_days}\n\n"
            reply += f"💰 Difference: ₹{int(diff):,} (air costs {int((diff/sea_total)*100)}% more)\n\n"
            
            if cargo == 'electronics':
                reply += "📱 For electronics, air is safer despite higher cost.\n"
            else:
                reply += "If not urgent, sea saves you significant money.\n\n"
            reply += "What's your priority - speed or savings?"
            return jsonify({'reply': reply, 'show_phone': False, 'phone_count': 0})
    
    # Urgency detection
    is_urgent = any(word in user_msg for word in ['urgent', 'fast', 'quick', 'asap', 'immediate'])
    want_cheap = any(word in user_msg for word in ['cheap', 'save', 'budget', 'economical', 'low cost'])
    
    # ========== QUOTE WITH RECOMMENDATION ==========
    
    has_weight = session_data['weight'] is not None
    has_dest = session_data['destination'] is not None
    
    if has_weight and has_dest:
        weight = session_data['weight']
        dest = session_data['destination']
        cargo = session_data.get('cargo', 'general') if cargo_mentioned else None
        
        air_total, air_rate, air_days = calculate_price(weight, "air", cargo or 'general')
        sea_total, sea_rate, sea_days = calculate_price(weight, "sea", cargo or 'general')
        
        recommended_mode, recommendation_text = get_recommendation(weight, cargo or 'general', is_urgent, want_cheap)
        
        reply = f"📦 {int(weight)} kg to {dest}\n\n"
        reply += f"✈️ Air: ₹{int(air_total):,} ({air_days})\n"
        reply += f"🚢 Sea: ₹{int(sea_total):,} ({sea_days})\n\n"
        
        if cargo:
            reply += f"📦 Cargo: {cargo.title()}\n\n"
        
        if recommendation_text:
            reply += f"💡 Recommendation: {recommendation_text}\n\n"
        
        if cargo is None and not cargo_mentioned:
            reply += "❓ What type of goods are you shipping? (electronics, garments, machinery, etc.)\n\n"
        
        # Only ask for phone after 2 interactions or if user shows intent
        if 'book' in user_msg or 'lock' in user_msg or 'confirm' in user_msg or phone_asked_count >= 1:
            reply += "Share your phone number and I'll have our team call you with the best locked rate."
            show_phone = True
            phone_asked_count += 1
        else:
            reply += "Would you like me to lock this rate for you?"
            show_phone = False
        
        return jsonify({'reply': reply, 'show_phone': show_phone, 'phone_count': phone_asked_count})
    
    # ========== MISSING INFO ==========
    
    if 'rate' in user_msg or 'price' in user_msg or 'cost' in user_msg:
        if has_weight and has_dest:
            weight = session_data['weight']
            dest = session_data['destination']
            total = weight * 320
            return jsonify({'reply': f"💰 {int(weight)} kg to {dest}: approx ₹{int(total):,} by air. Want me to compare with sea?", 'show_phone': False, 'phone_count': 0})
        else:
            missing = []
            if not has_weight: missing.append("weight")
            if not has_dest: missing.append("destination")
            return jsonify({'reply': f"Share your {', '.join(missing)} for a quote.", 'show_phone': False, 'phone_count': 0})
    
    if 'service' in user_msg:
        reply = "📦 Our services:\n• Air Freight (3-5 days)\n• Sea Freight (22-30 days)\n• Customs Clearance\n• Door-to-Door Delivery\n\nWhich one do you need?"
        return jsonify({'reply': reply, 'show_phone': False, 'phone_count': 0})
    
    if 'contact' in user_msg or 'phone' in user_msg:
        reply = "📞 Call: +91 90361 01201\n✉️ Email: shivu@pasfreight.com\n📍 Bangalore, India\n⏰ Available 24/7"
        return jsonify({'reply': reply, 'show_phone': False, 'phone_count': 0})
    
    if 'address' in user_msg:
        reply = "📍 PAS Freight Services\nSite No:171, Arkavathey Layout, Jakkur-BDA\nBangalore - 560092, India"
        return jsonify({'reply': reply, 'show_phone': False, 'phone_count': 0})
    
    if 'about' in user_msg:
        reply = "🏢 PAS Freight Services Pvt Ltd\n\n✅ WCA & GLA Certified\n🌟 8+ years experience\n🌍 Serving 50+ countries\n\nNeed a quote or advice?"
        return jsonify({'reply': reply, 'show_phone': False, 'phone_count': 0})
    
    # Smart ask for missing info
    missing = []
    if not has_weight:
        missing.append("weight")
    if not has_dest:
        missing.append("destination")
    
    if missing:
        reply = f"Got it. I need your {', '.join(missing)} to help you choose the best shipping option."
    else:
        reply = "Share your shipment details (weight, destination, cargo type) and I'll help you choose the best option."
    
    return jsonify({'reply': reply, 'show_phone': False, 'phone_count': 0})

if __name__ == '__main__':
    print("=" * 60)
    print("✨ Aisea - Smart Logistics Advisor (9/10)")
    print("📱 Open: http://localhost:5001")
    print("✅ Features: Decision advisor | Correction handling | Smart recommendations")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
