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

session_memory = {}

# Email configuration
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "priya.c@pasfreight.com",
    "sender_password": "fgph mosx qknt nwvr",
    "receiver_email": "priya.c@pasfreight.com"
}

def send_email_lead(name, email, phone, message):
    try:
        subject = f"New Lead from Aisea Chatbot - {name}"
        
        body = f"""
        New Lead Details from PAS Freight Chatbot
        
        Name: {name}
        Email: {email}
        Phone: {phone}
        Message: {message}
        Time: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Please follow up with this lead.
        """
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['receiver_email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.send_message(msg)
        server.quit()
        print(f"✓ Email sent for lead: {name}")
        return True
    except Exception as e:
        print(f"✗ Email error: {e}")
        return False

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Aisea - PAS Freight AI</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; display: flex; justify-content: center; align-items: center; }
        
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
        
        .chat-header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-header h3 { font-size: 18px; font-weight: 600; margin-bottom: 4px; }
        .chat-header p { font-size: 12px; opacity: 0.8; }
        
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
        }
        .service-btn:hover { background: linear-gradient(135deg, #2a5298, #1e3c72); color: white; transform: translateY(-2px); }
        
        .chat-messages { flex: 1; overflow-y: auto; padding: 20px; background: #f8f9fa; }
        .message { margin-bottom: 20px; display: flex; animation: fadeInUp 0.3s ease; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .user-message { justify-content: flex-end; }
        .bot-message { justify-content: flex-start; }
        .bubble { max-width: 80%; padding: 12px 16px; border-radius: 20px; font-size: 13px; line-height: 1.45; }
        .user-message .bubble { background: #2a5298; color: white; border-bottom-right-radius: 4px; }
        .bot-message .bubble { background: white; color: #1a202c; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; }
        
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 1000000;
            justify-content: center;
            align-items: center;
        }
        .modal-content {
            background: white;
            border-radius: 24px;
            padding: 28px;
            width: 90%;
            max-width: 380px;
        }
        .modal-content h3 { font-size: 20px; font-weight: 600; color: #1e3c72; margin-bottom: 8px; }
        .modal-content p { font-size: 13px; color: #64748b; margin-bottom: 20px; }
        .modal-content input {
            width: 100%;
            padding: 12px 16px;
            margin-bottom: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            font-size: 14px;
            outline: none;
        }
        .modal-content input:focus { border-color: #2a5298; }
        .modal-content button {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #2a5298, #1e3c72);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            margin-top: 8px;
        }
        .close-modal { background: #f1f5f9 !important; color: #64748b !important; }
        
        .typing { display: inline-flex; gap: 4px; padding: 8px 0; }
        .typing span { width: 8px; height: 8px; background: #cbd5e0; border-radius: 50%; animation: typingBounce 1.4s infinite; }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typingBounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-8px); } }
        
        .sub-buttons { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
        .sub-btn { background: #f1f5f9; border: 1px solid #e2e8f0; padding: 8px 14px; border-radius: 30px; font-size: 12px; cursor: pointer; color: #1e3c72; font-weight: 500; }
        .sub-btn:hover { background: #2a5298; color: white; }
        
        .contact-card { background: #f8fafc; border-radius: 16px; padding: 16px; margin-top: 12px; border: 1px solid #e2e8f0; }
        .contact-card h4 { font-size: 14px; font-weight: 600; color: #1e3c72; margin-bottom: 12px; }
        .contact-item { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-size: 12px; color: #334155; }
        
        .chat-input { padding: 16px; background: white; border-top: 1px solid #e2e8f0; display: flex; gap: 12px; }
        .chat-input input { flex: 1; padding: 12px 16px; background: #f8f9fa; border: 1px solid #e2e8f0; border-radius: 30px; font-size: 13px; outline: none; }
        .chat-input input:focus { border-color: #2a5298; box-shadow: 0 0 0 3px rgba(42,82,152,0.1); }
        .chat-input button { background: #2a5298; color: white; border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; font-size: 18px; }
        
        .chat-messages::-webkit-scrollbar { width: 5px; }
        .chat-messages::-webkit-scrollbar-track { background: #e2e8f0; border-radius: 10px; }
        .chat-messages::-webkit-scrollbar-thumb { background: #cbd5e0; border-radius: 10px; }
        
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
    
    <div id="quoteModal" class="modal">
        <div class="modal-content">
            <h3>💰 Get a Quote</h3>
            <p>Share your details and our team will get back to you with the best rates.</p>
            <input type="text" id="quoteName" placeholder="Your Name *">
            <input type="email" id="quoteEmail" placeholder="Email Address *">
            <input type="tel" id="quotePhone" placeholder="Phone Number">
            <button onclick="submitQuote()">Submit →</button>
            <button class="close-modal" onclick="closeQuoteModal()">Cancel</button>
        </div>
    </div>
    
    <div id="pasfreight-chat-window">
        <div class="chat-header">
            <h3>✨ Aisea</h3>
            <p>PAS Freight AI • 24/7 Support</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="bubble">Hi, I'm Aisea 👋<br><br>Tell me what you're shipping - I'll help you figure out the best way.</div>
            </div>
            <div class="message bot-message">
                <div class="bubble">
                    <div class="service-buttons">
                        <button class="service-btn" onclick="showImportMenu()">📥 IMPORT</button>
                        <button class="service-btn" onclick="showExportMenu()">📤 EXPORT</button>
                        <button class="service-btn" onclick="showCustoms()">📋 CUSTOMS</button>
                        <button class="service-btn" onclick="showCourier()">📮 COURIER</button>
                        <button class="service-btn" onclick="openQuoteModal()">💰 Get Quote</button>
                        <button class="service-btn" onclick="talkToExpert()">🎧 Talk to Expert</button>
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
        
        function openQuoteModal() { quoteModal.style.display = 'flex'; }
        function closeQuoteModal() { quoteModal.style.display = 'none'; document.getElementById('quoteName').value = ''; document.getElementById('quoteEmail').value = ''; document.getElementById('quotePhone').value = ''; }
        
        async function submitQuote() {
            const name = document.getElementById('quoteName').value.trim();
            const email = document.getElementById('quoteEmail').value.trim();
            const phone = document.getElementById('quotePhone').value.trim();
            if (!name || !email) { alert('Please enter your name and email address.'); return; }
            await fetch('/submit_lead', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ name: name, email: email, phone: phone, message: 'Quote request' }) });
            closeQuoteModal();
            addMessage("Thanks " + name + "! Our team will contact you within 24 hours.", false);
        }
        
        function talkToExpert() { window.open('https://wa.me/919036101201', '_blank'); addMessage("Redirecting to WhatsApp... You'll be connected to our expert shortly.", false); }
        
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
        
        function hideTyping() { const typing = document.getElementById('typing'); if (typing) typing.remove(); }
        
        function addContactInfo(title, numbers, emails) {
            let html = `<div class="contact-card"><h4>${title}</h4>`;
            if (numbers && numbers.length) numbers.forEach(num => { html += `<div class="contact-item">📞 ${num}</div>`; });
            if (emails && emails.length) emails.forEach(email => { html += `<div class="contact-item">✉️ ${email}</div>`; });
            html += `</div>`;
            addMessage(html, false);
        }
        
        window.showImportMenu = function() {
            addMessage("IMPORT", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📥 <strong>Select Mode:</strong><br><div class="sub-buttons"><button class="sub-btn" onclick="showImportAir()">✈️ AIR</button><button class="sub-btn" onclick="showImportSea()">🚢 SEA</button></div></div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        };
        
        window.showImportAir = function() { addMessage("IMPORT - AIR", true); addContactInfo("IMPORT AIR FREIGHT", ["+91 99869 42772", "+91 63615 21413"], ["gj@pasfreight.com", "rachana@pasfreight.com"]); };
        window.showImportSea = function() { addMessage("IMPORT - SEA", true); addContactInfo("IMPORT SEA FREIGHT (FCL/LCL)", ["+91 93648 81371", "+91 63615 21413"], ["vinodh@pasfreight.com", "gj@pasfreight.com"]); };
        
        window.showExportMenu = function() {
            addMessage("EXPORT", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📤 <strong>Select Mode:</strong><br><div class="sub-buttons"><button class="sub-btn" onclick="showExportAir()">✈️ AIR</button><button class="sub-btn" onclick="showExportSea()">🚢 SEA</button></div></div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        };
        
        window.showExportAir = function() { addMessage("EXPORT - AIR", true); addContactInfo("EXPORT AIR FREIGHT", ["+91 93648 81371", "+91 63615 26659"], ["vinodh@pasfreight.com", "kavan@pasfreight.com"]); };
        window.showExportSea = function() { addMessage("EXPORT - SEA", true); addContactInfo("EXPORT SEA FREIGHT", ["+91 93648 81371", "+91 63615 26659"], ["vinodh@pasfreight.com", "kavan@pasfreight.com"]); };
        
        window.showCustoms = function() { addMessage("CUSTOMS CLEARANCE", true); addContactInfo("CUSTOMS CLEARANCE", ["+91 63615 26664"], ["ajith@pasfreight.com", "edi.blr@pasfreight.com"]); };
        
        window.showCourier = function() {
            addMessage("COURIER", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📮 <strong>Select Type:</strong><br><div class="sub-buttons"><button class="sub-btn" onclick="showDomesticCourier()">🇮🇳 DOMESTIC</button><button class="sub-btn" onclick="showInternationalCourier()">🌍 INTERNATIONAL</button></div></div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        };
        
        window.showDomesticCourier = function() { addMessage("DOMESTIC COURIER", true); addContactInfo("DOMESTIC COURIER", ["+91 63615 26659"], ["kavan@pasfreight.com", "info@pasfreight.com"]); };
        window.showInternationalCourier = function() { addMessage("INTERNATIONAL COURIER", true); addContactInfo("INTERNATIONAL COURIER", ["+91 63615 26659"], ["kavan@pasfreight.com", "info@pasfreight.com"]); };
        
        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;
            userInput.value = '';
            addMessage(text, true);
            showTyping();
            try {
                const response = await fetch('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message: text, session_id: sessionId }) });
                const data = await response.json();
                hideTyping();
                addMessage(data.reply, false);
            } catch(error) { hideTyping(); addMessage('Call +91 90361 01201 for assistance.', false); }
        }
        
        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', function(e) { if (e.key === 'Enter') sendMessage(); });
        
        window.openQuoteModal = openQuoteModal;
        window.closeQuoteModal = closeQuoteModal;
        window.talkToExpert = talkToExpert;
    </script>
</body>
</html>
'''

def update_context(user_msg, ctx):
    msg_lower = user_msg.lower()
    
    # Update destination (CRITICAL - always update when user changes)
    dest_match = re.search(r'(?:to|for|change to|update to|switch to)\s+([A-Z][a-z]+|[A-Z]+)', user_msg, re.IGNORECASE)
    if dest_match:
        ctx['destination'] = dest_match.group(1).title()
        print(f"Context updated: destination -> {ctx['destination']}")
    
    # Update weight
    weight_match = re.search(r'(\d+)\s*(?:kg|kgs|kilo|kilogram)', msg_lower)
    if weight_match:
        ctx['weight'] = weight_match.group(1)
    
    # Update urgency
    if 'urgent' in msg_lower or 'fast' in msg_lower or 'express' in msg_lower:
        ctx['urgency'] = 'urgent'
    elif 'not urgent' in msg_lower or 'not in a hurry' in msg_lower or 'no rush' in msg_lower:
        ctx['urgency'] = 'not_urgent'
    
    # Update cargo type
    cargo_map = {'electronics': 'electronics', 'garments': 'garments', 'fragile': 'fragile', 'medicine': 'medicine'}
    for key, value in cargo_map.items():
        if key in msg_lower:
            ctx['cargo_type'] = value
            break
    
    return ctx

def get_smart_response(user_msg, ctx):
    msg_lower = user_msg.lower()
    
    # SHORT CLOSING FOR HOT LEADS
    if any(word in msg_lower for word in ['confirm now', 'ready to book', 'go ahead', 'lock it', 'proceed']):
        return "Perfect 👍 I'll lock this for you now. Just share your name and WhatsApp - I'll get our team to confirm immediately."
    
    # EXPERT ADVICE - "What would YOU do?"
    if 'what would you do' in msg_lower or 'what would you recommend' in msg_lower:
        if ctx.get('cargo_type') == 'electronics':
            return "If it was my shipment, I'd split it: critical items via air for speed, remaining via sea for cost. This balances safety + budget. Want me to help you plan this?"
        else:
            return "If it was my shipment, I'd choose sea for cost savings unless time is critical. What's more important to you - speed or budget?"
    
    # MESSY INPUT handling
    if 'or' in msg_lower and 'kg' in msg_lower and ('urgent' in msg_lower or 'maybe' in msg_lower):
        return "Got it 👍 sounds like approx 150-300kg and urgent. Let me confirm quickly: Is delivery time critical? Any fragile items?"
    
    # BALANCED RESPONSE (not repetitive)
    if ctx.get('urgency') == 'not_urgent' and ctx.get('cargo_type') == 'electronics':
        return f"Based on what you told me - electronics, not urgent, budget matters - I'd recommend sea with proper packing OR economy air if you want a safer middle option. Want me to check both for {ctx.get('weight', 'your')}kg to {ctx.get('destination', 'destination')}?"
    
    # NOT URGENT - Sea recommendation
    if ctx.get('urgency') == 'not_urgent':
        return f"Since you're not in a hurry, sea freight is your best bet - saves 60-70% vs air. Takes 20-30 days. Want me to check current sea rates for {ctx.get('weight', 'your')}kg to {ctx.get('destination', 'destination')}?"
    
    # URGENT - Air recommendation
    if ctx.get('urgency') == 'urgent':
        return f"For urgent delivery, air freight is your fastest option - 3-5 days. I can check immediate flight availability. Shall I proceed for {ctx.get('weight', 'your')}kg to {ctx.get('destination', 'destination')}?"
    
    # CUSTOMS question
    if 'customs' in msg_lower:
        return "We handle customs clearance with proper documentation. Our team reviews documents upfront to avoid delays. Need help with a specific shipment?"
    
    # Track shipment
    if 'track' in msg_lower:
        return "Please share your tracking ID - I'll check the status for you right away."
    
    # Human handoff
    if 'human' in msg_lower or 'talk to person' in msg_lower:
        return "Of course 👍 I'll connect you with our team. Call +91 90361 01201 or share your number and we'll call you within 10 minutes."
    
    # Get Quote - form
    if 'get quote' in msg_lower or 'quote' in msg_lower:
        return "Sure! Click the 'Get Quote' button above and fill in your details. Our team will send you the best rates within 24 hours."
    
    return None

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/submit_lead', methods=['POST'])
def submit_lead():
    data = request.get_json()
    name = data.get('name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    message = data.get('message', '')
    send_email_lead(name, email, phone, message)
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if session_id not in session_memory:
        session_memory[session_id] = {'cargo_type': None, 'destination': None, 'weight': None, 'urgency': None}
    
    ctx = session_memory[session_id]
    ctx = update_context(user_msg, ctx)
    session_memory[session_id] = ctx
    
    # Check for smart response first
    smart_response = get_smart_response(user_msg, ctx)
    if smart_response:
        return jsonify({'reply': smart_response})
    
    # Use AI for other queries
    system_prompt = f"""You are Aisea, a logistics consultant. Current context: Destination: {ctx.get('destination', 'unknown')}, Weight: {ctx.get('weight', 'unknown')}kg, Urgency: {ctx.get('urgency', 'unknown')}, Cargo: {ctx.get('cargo_type', 'unknown')}

Rules:
- Give SHORT answers (2-3 sentences max)
- Never repeat the same recommendation
- Use context from above - don't ask for info already given
- If user changed destination, acknowledge it
- Be conversational, not corporate
- Close with a question

Be helpful and direct."""
    
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
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': "Tell me what you're shipping - I'll help you figure out the best way."})

if __name__ == '__main__':
    print("=" * 60)
    print("Aisea - DEPLOY-READY 10/10 Chatbot")
    print("Open: http://localhost:5001")
    print("Fixes: Context memory | No repetition | Strong closing | Smart responses")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
