import openai
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "priya.c@pasfreight.com",
    "sender_password": "fgph mosx qknt nwvr",
    "receiver_email": "priya.c@pasfreight.com"
}

def send_lead_email(name, email, phone, quote_details):
    try:
        subject = f"New Quote Request from {name}"
        body = f"""New Quote Request from PAS Freight Chatbot

Name: {name}
Email: {email}
Phone: {phone}
Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Quote Details:
{quote_details}

Please follow up with this lead."""
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['receiver_email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'].replace(' ', ''))
        server.send_message(msg)
        server.quit()
        print(f"✓ Email sent for {name}")
        return True
    except Exception as e:
        print(f"✗ Email error: {e}")
        return False

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
        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; display: flex; justify-content: center; align-items: center; }
        
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
            background: #ffffff;
            border-radius: 24px;
            box-shadow: 0 24px 48px rgba(0,0,0,0.3);
            display: none;
            z-index: 999998;
            border: none;
            overflow: hidden;
            flex-direction: column;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            padding: 16px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #e0e0e0;
        }
        .header-info { display: flex; align-items: center; gap: 10px; }
        .avatar { width: 40px; height: 40px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 20px; color: white; }
        .header-text h3 { font-size: 18px; font-weight: 600; color: white; }
        .header-text p { font-size: 11px; color: rgba(255,255,255,0.8); margin-top: 2px; }
        .close-chat { background: rgba(255,255,255,0.1); border: none; color: white; font-size: 18px; cursor: pointer; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
        .close-chat:hover { background: rgba(255,255,255,0.2); transform: scale(1.05); }
        
        .chat-messages { flex: 1; overflow-y: auto; padding: 20px; background: #f7f9fc; }
        .message { margin-bottom: 20px; display: flex; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .user-message { justify-content: flex-end; }
        .bot-message { justify-content: flex-start; }
        .bubble { max-width: 80%; padding: 12px 16px; border-radius: 20px; font-size: 14px; line-height: 1.45; }
        .user-message .bubble { background: #2a5298; color: white; border-bottom-right-radius: 4px; }
        .bot-message .bubble { background: white; color: #1a202c; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        
        .quick-reply {
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
            justify-content: center;
            padding: 16px;
            background: #ffffff;
            border-top: 1px solid #e2e8f0;
        }
        .quick-btn {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 30px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 600;
            flex: 1;
            max-width: 140px;
        }
        .quick-btn:hover { transform: scale(0.98); opacity: 0.9; }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.7);
            z-index: 1000000;
            justify-content: center;
            align-items: center;
        }
        .modal-content {
            background: white;
            border-radius: 24px;
            padding: 32px;
            width: 90%;
            max-width: 400px;
            animation: slideUp 0.3s ease;
        }
        @keyframes slideUp { from { transform: translateY(50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .modal-content h3 { font-size: 24px; margin-bottom: 8px; color: #1e3c72; }
        .modal-content p { color: #666; margin-bottom: 24px; font-size: 14px; }
        .modal-content input { width: 100%; padding: 12px 16px; margin: 8px 0; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 14px; outline: none; }
        .modal-content input:focus { border-color: #2a5298; }
        .modal-content button { width: 100%; padding: 14px; margin-top: 16px; background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; border: none; border-radius: 12px; font-size: 16px; font-weight: 600; cursor: pointer; }
        .close-modal { position: absolute; top: 16px; right: 20px; font-size: 24px; cursor: pointer; color: #999; }
        
        .chat-input { padding: 16px; background: white; border-top: 1px solid #e2e8f0; display: flex; gap: 10px; }
        .chat-input input { flex: 1; padding: 12px 16px; border: 1px solid #e2e8f0; border-radius: 28px; font-size: 14px; outline: none; font-family: 'Inter', sans-serif; }
        .chat-input input:focus { border-color: #2a5298; }
        .chat-input button { background: #2a5298; color: white; border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; font-size: 18px; transition: all 0.2s; }
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
                    <p>PAS Freight AI • 24/7</p>
                </div>
            </div>
            <button class="close-chat" id="closeChatBtn">✕</button>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="bubble">Hi, I'm Aisea 👋<br><br>Tell me what you're shipping and where - I'll help you choose the best option.</div>
            </div>
        </div>
        
        <div class="quick-reply">
            <button class="quick-btn" id="getQuoteBtn">💰 Get Quote</button>
            <button class="quick-btn" id="trackShipmentBtn">📍 Track Shipment</button>
            <button class="quick-btn" id="talkToExpertBtn">🎧 Talk to Expert</button>
        </div>
        
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Ask me anything..." autocomplete="off">
            <button id="sendBtn">➤</button>
        </div>
    </div>
    
    <div id="quoteModal" class="modal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal()">&times;</span>
            <h3>💰 Get a Quote</h3>
            <p>Share your details and our team will send you the best rates within 10 minutes.</p>
            <input type="text" id="quoteName" placeholder="Your Full Name" required>
            <input type="email" id="quoteEmail" placeholder="Email Address" required>
            <input type="tel" id="quotePhone" placeholder="WhatsApp Number" required>
            <textarea id="quoteDetails" rows="3" placeholder="Shipment details (weight, destination, cargo type...)" style="width:100%; padding:12px; border:1px solid #e2e8f0; border-radius:12px; font-size:14px; margin-top:8px;"></textarea>
            <button onclick="submitQuote()">Submit Request →</button>
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
        const quoteModal = document.getElementById('quoteModal');
        
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
        
        function closeModal() { quoteModal.style.display = 'none'; }
        
        async function submitQuote() {
            const name = document.getElementById('quoteName').value.trim();
            const email = document.getElementById('quoteEmail').value.trim();
            const phone = document.getElementById('quotePhone').value.trim();
            const details = document.getElementById('quoteDetails').value.trim();
            
            if (!name || !email || !phone) { alert('Please fill in all fields'); return; }
            
            closeModal();
            addMessage(`Quote request submitted`, true);
            addMessage("✅ Thank you! Our team will send you the best rates within 10 minutes on WhatsApp.", false);
            
            await fetch('/send_quote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, phone, details })
            });
        }
        
        document.getElementById('getQuoteBtn').addEventListener('click', function() { quoteModal.style.display = 'flex'; });
        
        document.getElementById('trackShipmentBtn').addEventListener('click', function() {
            addMessage("Track Shipment", true);
            addMessage("Please share your tracking ID - I'll check the status for you.", false);
        });
        
        document.getElementById('talkToExpertBtn').addEventListener('click', function() {
            addMessage("Talk to Expert", true);
            window.open('https://wa.me/919036101201?text=Hi!%20I%20need%20assistance%20with%20my%20shipment.', '_blank');
            addMessage("📱 Opening WhatsApp. Our expert is online now.", false);
        });
        
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
    </script>
</body>
</html>
'''

def update_context(user_msg, ctx):
    msg_lower = user_msg.lower()
    
    # Remove uncertainty - replace "none" with proper handling
    if 'none' in msg_lower or 'unclear' in msg_lower or 'maybe' in msg_lower:
        if not ctx.get('destination'):
            ctx['destination'] = 'your destination'
        if not ctx.get('weight'):
            ctx['weight'] = 'your'
    
    weight_match = re.search(r'(\d+)\s*(?:kg|kgs|kilo|kilogram)', msg_lower)
    if weight_match:
        ctx['weight'] = weight_match.group(1)
    
    change_match = re.search(r'(?:change to|update to|switch to|now to)\s+([A-Z][a-z]+|[A-Z]+)', msg_lower)
    if change_match:
        ctx['destination'] = change_match.group(1).title()
    else:
        dest_match = re.search(r'(?:to|for)\s+([A-Z][a-z]+|[A-Z]+)', msg_lower)
        if dest_match and not ctx.get('destination'):
            ctx['destination'] = dest_match.group(1).title()
    
    if 'urgent' in msg_lower or 'fast' in msg_lower or 'quick' in msg_lower:
        ctx['urgency'] = 'urgent'
    elif 'not urgent' in msg_lower or 'no rush' in msg_lower:
        ctx['urgency'] = 'not urgent'
    
    cargo_map = {'electronics': 'electronics', 'garments': 'garments', 'medicine': 'medicine',
                 'machinery': 'machinery', 'furniture': 'furniture', 'fragile': 'fragile'}
    for key, value in cargo_map.items():
        if key in msg_lower:
            ctx['cargo_type'] = value
            break
    
    # Detect buying intent - strong closing trigger
    if any(word in msg_lower for word in ['confirm', 'works', 'ready', 'go ahead', 'let\'s do', 'proceed', 'yes']):
        ctx['buying_intent'] = True
    
    return ctx

def get_sales_response(ctx, user_msg):
    """PAS Freight first, strong closing, no uncertainty"""
    msg_lower = user_msg.lower()
    weight = ctx.get('weight', 'your')
    dest = ctx.get('destination', 'your destination')
    cargo = ctx.get('cargo_type', 'goods')
    urgency = ctx.get('urgency', '')
    
    # Handle competitor mentions - put PAS Freight first
    if 'dhl' in msg_lower or 'fedex' in msg_lower:
        return f"PAS Freight offers competitive rates with personalized support. For {weight}kg {cargo} to {dest}, we can match or beat DHL/FedEx pricing. Want me to check our current rate for you?"
    
    # STRONG CLOSING - when user shows buying intent
    if ctx.get('buying_intent') or 'confirm' in msg_lower or 'works' in msg_lower:
        return f"Perfect 👍 I'll take this forward right now.\n\nJust share your WhatsApp number and we'll lock the best option for you.\n\nWhat's the best number to reach you?"
    
    # Handle "to none" or uncertainty - replace with structured response
    if dest == 'your destination' or 'none' in msg_lower:
        return f"Got it. Let me help you with your shipment to {dest}. For {weight}kg {cargo}, PAS Freight recommends {'air freight for faster delivery' if urgency == 'urgent' else 'sea freight for best value'}. What's your delivery timeline?"
    
    # Direct PAS Freight recommendation
    if weight != 'your' and dest != 'your destination' and cargo != 'goods':
        if urgency == 'urgent':
            return f"PAS Freight recommends air freight for your {weight}kg {cargo} to {dest}. 3-5 days delivery. Ready to proceed with a quote?"
        else:
            return f"PAS Freight recommends sea freight for your {weight}kg {cargo} to {dest}. Saves 60-70% vs air. Takes 20-30 days. Want me to check current rates?"
    
    return None

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/send_quote', methods=['POST'])
def send_quote():
    data = request.get_json()
    send_lead_email(data.get('name', ''), data.get('email', ''), data.get('phone', ''), data.get('details', ''))
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if session_id not in session_memory:
        session_memory[session_id] = {'cargo_type': None, 'destination': None, 'weight': None, 'urgency': None, 'buying_intent': False}
    
    ctx = session_memory[session_id]
    ctx = update_context(user_msg, ctx)
    
    # Try sales response first
    sales_response = get_sales_response(ctx, user_msg)
    if sales_response:
        session_memory[session_id] = ctx
        return jsonify({'reply': sales_response})
    
    # Fallback to AI with PAS Freight branding
    system_prompt = f"""You are Aisea, a sales assistant for PAS Freight Services (WCA & GLA certified, 8+ years in logistics).

Current context:
- Weight: {ctx.get('weight', 'your')}kg
- Destination: {ctx.get('destination', 'your destination')}
- Cargo: {ctx.get('cargo_type', 'goods')}

CRITICAL RULES:
1. ALWAYS mention PAS Freight first - never suggest DHL/FedEx as first option
2. When user shows buying intent, IMMEDIATELY ask for WhatsApp number
3. Never use words like "none", "maybe", "unclear" - be direct
4. Keep responses short and sales-focused
5. Close strongly when user is ready

Be confident, direct, and focused on converting the sale."""
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=120,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        session_memory[session_id] = ctx
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': "Tell me your shipment details - weight, destination, and cargo type. PAS Freight will give you the best rate."})

if __name__ == '__main__':
    print("=" * 60)
    print("Aisea - 10/10 Sales-Ready Chatbot")
    print("Open: http://localhost:5001")
    print("Fixed: PAS Freight first | Strong closing | No uncertainty")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
