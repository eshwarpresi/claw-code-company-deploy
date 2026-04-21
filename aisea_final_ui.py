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

# Email configuration
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
        
        body = f"""
        New Quote Request from PAS Freight Chatbot
        
        Name: {name}
        Email: {email}
        Phone: {phone}
        Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Quote Details:
        {quote_details}
        
        Please follow up with this lead.
        """
        
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
        print(f"✓ Email sent to priya.c@pasfreight.com for {name}")
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
        
        /* Modal Styles */
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
        @keyframes slideUp {
            from { transform: translateY(50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .modal-content h3 {
            font-size: 24px;
            margin-bottom: 8px;
            color: #1e3c72;
        }
        .modal-content p {
            color: #666;
            margin-bottom: 24px;
            font-size: 14px;
        }
        .modal-content input {
            width: 100%;
            padding: 12px 16px;
            margin: 8px 0;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            font-size: 14px;
            outline: none;
        }
        .modal-content input:focus {
            border-color: #2a5298;
        }
        .modal-content button {
            width: 100%;
            padding: 14px;
            margin-top: 16px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
        }
        .close-modal {
            position: absolute;
            top: 16px;
            right: 20px;
            font-size: 24px;
            cursor: pointer;
            color: #999;
        }
        
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
                <div class="bubble">Hi, I'm Aisea 👋<br><br>How can I help you today?</div>
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
    
    <!-- Quote Modal -->
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
        
        function closeModal() {
            quoteModal.style.display = 'none';
        }
        
        async function submitQuote() {
            const name = document.getElementById('quoteName').value.trim();
            const email = document.getElementById('quoteEmail').value.trim();
            const phone = document.getElementById('quotePhone').value.trim();
            const details = document.getElementById('quoteDetails').value.trim();
            
            if (!name || !email || !phone) {
                alert('Please fill in all fields');
                return;
            }
            
            closeModal();
            addMessage(`Name: ${name}\nEmail: ${email}\nPhone: ${phone}\nDetails: ${details}`, true);
            addMessage("✅ Thank you! Our team will send you the best rates within 10 minutes. We'll contact you on WhatsApp shortly.", false);
            
            await fetch('/send_quote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, phone, details })
            });
        }
        
        document.getElementById('getQuoteBtn').addEventListener('click', function() {
            quoteModal.style.display = 'flex';
        });
        
        document.getElementById('trackShipmentBtn').addEventListener('click', function() {
            addMessage("Track Shipment", true);
            addMessage("Please share your tracking ID or reference number, and I'll check the status for you right away.", false);
        });
        
        document.getElementById('talkToExpertBtn').addEventListener('click', function() {
            addMessage("Talk to Expert", true);
            window.open('https://wa.me/919036101201?text=Hi!%20I%20need%20assistance%20with%20my%20shipment.%20Please%20help%20me.', '_blank');
            addMessage("📱 Opening WhatsApp... You can chat directly with our expert at +91 90361 01201", false);
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

def detect_intent(user_msg, ctx):
    msg_lower = user_msg.lower()
    
    if any(word in msg_lower for word in ['ready', 'book', 'proceed', 'finalize', 'go ahead', 'yes let\'s', 'sounds good']):
        return 'convert'
    
    if ('not urgent' in msg_lower or 'not in a hurry' in msg_lower or 'no rush' in msg_lower):
        return 'balanced'
    
    if any(word in msg_lower for word in ['match', 'negotiate', 'can you do better', 'discount']):
        return 'negotiate'
    
    if any(word in msg_lower for word in ['responsible', 'liable', 'accountable', 'claim']):
        return 'responsibility'
    
    if any(word in msg_lower for word in ['guarantee', 'delivery by', 'by date', 'by friday']):
        return 'guarantee'
    
    if any(word in msg_lower for word in ['cheapest', 'budget', 'save money', 'low cost']):
        return 'cost'
    
    if any(word in msg_lower for word in ['urgent', 'fast', 'quick', 'express', 'asap']):
        return 'urgent'
    
    if any(word in msg_lower for word in ['bulk', 'monthly', 'weekly', 'regular', 'volume']):
        return 'bulk'
    
    if any(word in msg_lower for word in ['customs', 'clearance', 'duty', 'tax']):
        return 'customs'
    
    if 'electronics' in msg_lower:
        return 'electronics'
    
    return 'general'

def get_premium_response(intent, ctx, user_msg):
    weight = ctx.get('weight', 'your')
    dest = ctx.get('destination', 'destination')
    cargo = ctx.get('cargo_type', 'goods')
    
    if intent == 'convert':
        return f"""Perfect 👍 I'll arrange this for you right away.

Just click the "💰 Get Quote" button above and share your details - our team will send you the best rates within 10 minutes."""
    
    elif intent == 'balanced':
        return f"""I understand 👍 You want reliability without overspending.

For {weight}kg {cargo} to {dest}:
• Economy Air: 7-10 days, moderate cost
• Sea (with insurance): 20-30 days, best savings

Since time isn't urgent, sea freight gives you maximum value. Click "💰 Get Quote" for exact rates."""
    
    elif intent == 'negotiate':
        return f"""I appreciate your directness 👍

Let me check what's the best possible rate for your shipment. Click "💰 Get Quote" and share your details - our team will get back to you with the best competitive rate."""
    
    elif intent == 'responsibility':
        return f"""Excellent question 👍

We provide:
• Clear shipping terms before shipment
• Full insurance coverage options
• Real-time tracking portal access
• Dedicated support for any issues

Click "💰 Get Quote" to discuss your specific requirements."""
    
    elif intent == 'guarantee':
        return f"""For {weight}kg to {dest}:
• Express air: 3-5 days
• Standard air: 7-10 days
• Sea: 20-30 days

Click "💰 Get Quote" for exact timeline based on current carrier schedules."""
    
    elif intent == 'cost':
        return f"""For {weight}kg to {dest}, sea freight saves 60-70% compared to air.

Sea: 20-30 days | Air: 3-7 days

Click "💰 Get Quote" for current sea freight rates."""
    
    elif intent == 'urgent':
        return f"""For urgent delivery to {dest}:
✓ Express air: 3-5 days
✓ Priority handling

Click "💰 Get Quote" - I'll check immediate flight availability."""
    
    elif intent == 'bulk':
        return f"""For regular shipments, we offer volume discounts and dedicated support.

Click "💰 Get Quote" and share your monthly volume - our team will prepare a custom pricing proposal."""
    
    elif intent == 'customs':
        return f"""Customs clearance is our expertise 👍

We handle documentation, HS code classification, duty calculation, and compliance.

Click "💰 Get Quote" for expert assistance with your shipment."""
    
    elif intent == 'electronics':
        return f"""Electronics require special handling 👍

Air freight is recommended for safety. Click "💰 Get Quote" for rates and handling options."""
    
    return None

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/send_quote', methods=['POST'])
def send_quote():
    data = request.get_json()
    name = data.get('name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    details = data.get('details', '')
    
    quote_details = f"Name: {name}\nEmail: {email}\nPhone: {phone}\nShipment Details: {details}"
    send_lead_email(name, email, phone, quote_details)
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if session_id not in session_memory:
        session_memory[session_id] = {'cargo_type': None, 'destination': None, 'weight': None, 'origin': None, 'intent': None}
    
    ctx = session_memory[session_id]
    
    weight_match = re.search(r'(\d+)\s*(?:kg|kgs|kilo|kilogram)', user_msg, re.IGNORECASE)
    if weight_match and not ctx.get('weight'):
        ctx['weight'] = weight_match.group(1)
    
    dest_match = re.search(r'(?:to|for)\s+([A-Z][a-z]+|[A-Z]+)', user_msg)
    if dest_match and not ctx.get('destination'):
        ctx['destination'] = dest_match.group(1).title()
    
    cargo_map = {
        'electronics': 'electronics', 'garments': 'garments', 'medicine': 'medicine',
        'machinery': 'machinery', 'furniture': 'furniture'
    }
    for key, value in cargo_map.items():
        if key in user_msg.lower() and not ctx.get('cargo_type'):
            ctx['cargo_type'] = value
            break
    
    intent = detect_intent(user_msg, ctx)
    ctx['intent'] = intent
    
    premium_response = get_premium_response(intent, ctx, user_msg)
    
    if premium_response:
        session_memory[session_id] = ctx
        return jsonify({'reply': premium_response})
    
    system_prompt = """You are Aisea, a premium logistics consultant for PAS Freight.

Guidelines:
- Be conversational and solution-driven
- Never ask for information already provided
- Build trust first
- Use premium, confident language

Company: PAS Freight (WCA & GLA Certified)
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
    print("Aisea - Premium UI with Form + WhatsApp")
    print("Open: http://localhost:5001")
    print("Features: Get Quote Form | WhatsApp Redirect | Email Integration")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
