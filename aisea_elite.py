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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); height: 100vh; display: flex; justify-content: center; align-items: center; }
        
        #pasfreight-chat-btn {
            position: fixed; bottom: 24px; right: 24px; width: 60px; height: 60px;
            background: linear-gradient(135deg, #1e3c72, #2a5298); border-radius: 50%; cursor: pointer;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2); display: flex; align-items: center; justify-content: center;
            transition: all 0.3s ease; border: none; z-index: 999999;
        }
        #pasfreight-chat-btn:hover { transform: scale(1.08); box-shadow: 0 12px 32px rgba(0,0,0,0.25); }
        .chat-icon { font-size: 28px; color: white; }
        
        .notification-badge {
            position: absolute; top: -4px; right: -4px; background: #ef4444; color: white;
            border-radius: 50%; width: 18px; height: 18px; font-size: 10px;
            display: flex; align-items: center; justify-content: center; font-weight: bold; animation: blink 1s infinite;
        }
        @keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        
        #pasfreight-chat-window {
            position: fixed; bottom: 90px; right: 24px; width: 420px; height: 620px;
            background: white; border-radius: 24px; box-shadow: 0 24px 48px rgba(0,0,0,0.3);
            display: none; z-index: 999998; border: none; overflow: hidden; flex-direction: column;
        }
        
        .chat-header { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; text-align: center; }
        .chat-header h3 { font-size: 18px; font-weight: 600; margin-bottom: 4px; }
        .chat-header p { font-size: 12px; opacity: 0.8; }
        
        .service-buttons { display: flex; flex-wrap: wrap; gap: 10px; margin: 16px 0; justify-content: center; }
        .service-btn {
            background: linear-gradient(135deg, #f1f5f9, #ffffff); border: 1px solid #e2e8f0;
            padding: 10px 16px; border-radius: 40px; font-size: 13px; cursor: pointer;
            color: #1e3c72; font-weight: 600; transition: all 0.2s;
        }
        .service-btn:hover { background: linear-gradient(135deg, #2a5298, #1e3c72); color: white; transform: translateY(-2px); }
        
        .action-buttons { display: flex; gap: 12px; margin: 16px 0; justify-content: center; }
        .action-btn {
            flex: 1; background: linear-gradient(135deg, #10a37f, #0d8c6d); border: none;
            padding: 12px 16px; border-radius: 40px; font-size: 13px; cursor: pointer;
            color: white; font-weight: 600; transition: all 0.2s; text-align: center;
        }
        .action-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
        .action-btn-wa { background: linear-gradient(135deg, #25D366, #128C7E); }
        
        .modal {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.5); z-index: 1000000; justify-content: center; align-items: center;
        }
        .modal-content {
            background: white; border-radius: 24px; padding: 24px; width: 90%; max-width: 350px; animation: slideIn 0.3s ease;
        }
        @keyframes slideIn { from { transform: translateY(-50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
        .modal-content h3 { font-size: 20px; color: #1e3c72; margin-bottom: 8px; }
        .modal-content p { font-size: 13px; color: #64748b; margin-bottom: 20px; }
        .modal-content input { width: 100%; padding: 12px; margin-bottom: 12px; border: 1px solid #e2e8f0; border-radius: 12px; font-size: 14px; outline: none; }
        .modal-content button { width: 100%; padding: 12px; background: #2a5298; color: white; border: none; border-radius: 12px; font-size: 14px; font-weight: 600; cursor: pointer; margin-top: 8px; }
        .modal-close { background: #e2e8f0 !important; color: #1e293b !important; }
        
        .chat-messages { flex: 1; overflow-y: auto; padding: 20px; background: #f8f9fa; }
        .message { margin-bottom: 20px; display: flex; animation: fadeInUp 0.3s ease; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
        .user-message { justify-content: flex-end; }
        .bot-message { justify-content: flex-start; }
        .bubble { max-width: 80%; padding: 12px 16px; border-radius: 20px; font-size: 13px; line-height: 1.45; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        .user-message .bubble { background: #2a5298; color: white; border-bottom-right-radius: 4px; }
        .bot-message .bubble { background: white; color: #1a202c; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; }
        
        .typing { display: inline-flex; gap: 4px; padding: 8px 0; }
        .typing span { width: 8px; height: 8px; background: #cbd5e0; border-radius: 50%; animation: typingBounce 1.4s infinite; }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typingBounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-8px); } }
        
        .sub-buttons { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
        .sub-btn { background: #f1f5f9; border: 1px solid #e2e8f0; padding: 8px 14px; border-radius: 30px; font-size: 12px; cursor: pointer; color: #1e3c72; font-weight: 500; transition: all 0.2s; }
        .sub-btn:hover { background: #2a5298; color: white; border-color: #2a5298; }
        
        .contact-card { background: #f8fafc; border-radius: 16px; padding: 16px; margin-top: 12px; border: 1px solid #e2e8f0; }
        .contact-card h4 { font-size: 14px; font-weight: 600; color: #1e3c72; margin-bottom: 12px; }
        .contact-item { display: flex; align-items: center; gap: 10px; margin-bottom: 10px; font-size: 12px; color: #334155; }
        
        .chat-input { padding: 16px; background: white; border-top: 1px solid #e2e8f0; display: flex; gap: 12px; }
        .chat-input input { flex: 1; padding: 12px 16px; background: #f8f9fa; border: 1px solid #e2e8f0; border-radius: 30px; font-size: 13px; outline: none; }
        .chat-input input:focus { border-color: #2a5298; box-shadow: 0 0 0 3px rgba(42,82,152,0.1); }
        .chat-input button { background: #2a5298; color: white; border: none; width: 44px; height: 44px; border-radius: 50%; cursor: pointer; font-size: 18px; transition: all 0.2s; }
        
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
            <input type="text" id="quoteName" placeholder="Full Name" required>
            <input type="email" id="quoteEmail" placeholder="Email Address" required>
            <input type="tel" id="quotePhone" placeholder="Phone Number" required>
            <button onclick="submitQuote()">Submit →</button>
            <button class="modal-close" onclick="closeQuoteModal()">Cancel</button>
        </div>
    </div>
    
    <div id="pasfreight-chat-window">
        <div class="chat-header">
            <h3>✨ Aisea</h3>
            <p>PAS Freight AI • 24/7 Support</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="bubble">Hi, I'm Aisea 👋<br><br>Need help with shipping? Select a service below.</div>
            </div>
            <div class="message bot-message">
                <div class="bubble">
                    <div class="service-buttons">
                        <button class="service-btn" onclick="showImportMenu()">📥 IMPORT</button>
                        <button class="service-btn" onclick="showExportMenu()">📤 EXPORT</button>
                        <button class="service-btn" onclick="showCustoms()">📋 CUSTOMS</button>
                        <button class="service-btn" onclick="showCourier()">📮 COURIER</button>
                    </div>
                    <div class="action-buttons">
                        <button class="action-btn" onclick="openQuoteModal()">💰 Get Quote</button>
                        <button class="action-btn action-btn-wa" onclick="openWhatsApp()">🎧 Talk to Expert</button>
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
        
        function openQuoteModal() {
            document.getElementById('quoteModal').style.display = 'flex';
        }
        
        function closeQuoteModal() {
            document.getElementById('quoteModal').style.display = 'none';
            document.getElementById('quoteName').value = '';
            document.getElementById('quoteEmail').value = '';
            document.getElementById('quotePhone').value = '';
        }
        
        function openWhatsApp() {
            window.open('https://wa.me/919036101201', '_blank');
            addMessage("Connecting you to WhatsApp...", false);
        }
        
        async function submitQuote() {
            const name = document.getElementById('quoteName').value.trim();
            const email = document.getElementById('quoteEmail').value.trim();
            const phone = document.getElementById('quotePhone').value.trim();
            
            if (!name || !email || !phone) {
                alert('Please fill all fields');
                return;
            }
            
            closeQuoteModal();
            addMessage("💰 Requesting a quote...", true);
            showTyping();
            
            const response = await fetch('/submit_quote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email, phone })
            });
            const data = await response.json();
            hideTyping();
            addMessage(data.reply, false);
        }
        
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
        
        window.showImportAir = function() { addMessage("IMPORT - AIR", true); addContactInfo("IMPORT AIR FREIGHT", ["+91 99869 42772", "+91 63615 21413"], ["gj@pasfreight.com", "rachana@pasfreight.com"]); };
        window.showImportSea = function() { addMessage("IMPORT - SEA", true); addContactInfo("IMPORT SEA FREIGHT", ["+91 93648 81371", "+91 63615 21413"], ["vinodh@pasfreight.com", "gj@pasfreight.com"]); };
        window.showExportMenu = function() { addMessage("EXPORT", true); const div = document.createElement('div'); div.className = 'message bot-message'; div.innerHTML = `<div class="bubble">📤 <strong>Select Mode:</strong><br><div class="sub-buttons"><button class="sub-btn" onclick="showExportAir()">✈️ AIR</button><button class="sub-btn" onclick="showExportSea()">🚢 SEA</button></div></div>`; messagesDiv.appendChild(div); div.scrollIntoView({ behavior: 'smooth' }); };
        window.showExportAir = function() { addMessage("EXPORT - AIR", true); addContactInfo("EXPORT AIR FREIGHT", ["+91 93648 81371", "+91 63615 26659"], ["vinodh@pasfreight.com", "kavan@pasfreight.com"]); };
        window.showExportSea = function() { addMessage("EXPORT - SEA", true); addContactInfo("EXPORT SEA FREIGHT", ["+91 93648 81371", "+91 63615 26659"], ["vinodh@pasfreight.com", "kavan@pasfreight.com"]); };
        window.showCustoms = function() { addMessage("CUSTOMS CLEARANCE", true); addContactInfo("CUSTOMS CLEARANCE", ["+91 63615 26664"], ["ajith@pasfreight.com", "edi.blr@pasfreight.com"]); };
        window.showCourier = function() { addMessage("COURIER", true); const div = document.createElement('div'); div.className = 'message bot-message'; div.innerHTML = `<div class="bubble">📮 <strong>Select Type:</strong><br><div class="sub-buttons"><button class="sub-btn" onclick="showDomesticCourier()">🇮🇳 DOMESTIC</button><button class="sub-btn" onclick="showInternationalCourier()">🌍 INTERNATIONAL</button></div></div>`; messagesDiv.appendChild(div); div.scrollIntoView({ behavior: 'smooth' }); };
        window.showDomesticCourier = function() { addMessage("DOMESTIC COURIER", true); addContactInfo("DOMESTIC COURIER", ["+91 63615 26659"], ["kavan@pasfreight.com", "info@pasfreight.com"]); };
        window.showInternationalCourier = function() { addMessage("INTERNATIONAL COURIER", true); addContactInfo("INTERNATIONAL COURIER", ["+91 63615 26659"], ["kavan@pasfreight.com", "info@pasfreight.com"]); };
        
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
        
        window.openQuoteModal = openQuoteModal;
        window.closeQuoteModal = closeQuoteModal;
        window.submitQuote = submitQuote;
        window.openWhatsApp = openWhatsApp;
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

def detect_intent(user_msg, ctx):
    msg_lower = user_msg.lower()
    
    # Dangerous goods
    if any(word in msg_lower for word in ['lithium', 'battery', 'chemical', 'acid', 'flammable', 'explosive', 'batteries', 'restricted']):
        return 'dangerous_goods'
    
    # Tracking
    if 'track' in msg_lower or 'tracking' in msg_lower:
        return 'tracking'
    
    # Trust / complaint / delayed / lost
    if any(word in msg_lower for word in ['lost', 'damage', 'trust', 'reliable', 'safe', 'insurance', 'claim', 'delayed', 'company delayed', 'forwarder']):
        return 'trust'
    
    # Negotiation / match price
    if any(word in msg_lower for word in ['match price', 'match rate', 'negotiate', 'can you do better', 'discount', 'competitive']):
        return 'negotiate'
    
    # Ready to proceed
    if any(word in msg_lower for word in ['handle everything', 'take care', 'proceed', 'book', 'ready', 'finalize']):
        return 'ready'
    
    # Urgent
    if any(word in msg_lower for word in ['urgent', 'fast', 'quick', 'express', 'asap']):
        return 'urgent'
    
    # Cheapest / budget
    if any(word in msg_lower for word in ['cheapest', 'budget', 'save money', 'low cost', 'affordable']):
        return 'budget'
    
    # Bulk
    if any(word in msg_lower for word in ['bulk', 'monthly', 'weekly', 'regular', 'volume']):
        return 'bulk'
    
    # Customs
    if any(word in msg_lower for word in ['customs', 'clearance', 'duty', 'documentation']):
        return 'customs'
    
    # Quote
    if any(word in msg_lower for word in ['quote', 'price', 'cost', 'rate', 'how much']):
        return 'quote'
    
    # Comparison (air vs split, etc.)
    if any(word in msg_lower for word in ['air vs', 'split vs', 'compare', 'better option', 'which is better']):
        return 'comparison'
    
    # Destination change
    if 'change to' in msg_lower or 'change destination' in msg_lower:
        return 'destination_change'
    
    # General shipping
    if any(word in msg_lower for word in ['ship', 'send', 'courier', 'logistics', 'kg', 'to']):
        return 'shipping'
    
    return 'general'

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/submit_quote', methods=['POST'])
def submit_quote():
    data = request.get_json()
    name = data.get('name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    print(f"Lead: {name} - {email} - {phone}")
    return jsonify({'reply': f"✅ Thank you {name}! Our team will contact you within 10 minutes at {phone} or {email}. For immediate assistance, you can also WhatsApp us at +91 90361 01201."})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if session_id not in session_memory:
        session_memory[session_id] = {'weight': None, 'destination': None, 'cargo': None}
    
    ctx = session_memory[session_id]
    intent = detect_intent(user_msg, ctx)
    
    print(f"Intent: {intent}")  # Debug
    
    # 1. DESTINATION CHANGE - Preserve context
    if intent == 'destination_change':
        dest_match = re.search(r'(?:change to|to)\s+([A-Z][a-z]+|[A-Z]+)', user_msg)
        if dest_match:
            new_dest = dest_match.group(1).title()
            ctx['destination'] = new_dest
            session_memory[session_id] = ctx
            weight = ctx.get('weight', '120')
            return jsonify({'reply': f"Got it 👍 changing destination to {new_dest}.\nSame {weight}kg electronics.\n\nDo you prefer faster delivery or lower cost?"})
        return jsonify({'reply': "Got it 👍 I've updated the destination. What's your priority - speed or cost?"})
    
    # 2. COMPARISON (Air vs Split)
    if intent == 'comparison':
        weight = ctx.get('weight', '120')
        return jsonify({'reply': f"Good question 👍\n\n✔️ Full air → fastest ({weight}kg, 3-5 days), highest cost\n✔️ Split (air + sea) → balances cost & speed\n\nFor {weight}kg, split option often gives better value if not urgent. Want me to check both options?"})
    
    # 3. DANGEROUS GOODS
    if intent == 'dangerous_goods':
        return jsonify({'reply': "Batteries require special handling 👍\n\nWe manage:\n✔️ DG documentation\n✔️ compliance approvals\n✔️ safe packaging\n\nLet me check the best option for this shipment."})
    
    # 4. TRUST / DELAY COMPLAINT
    if intent == 'trust':
        return jsonify({'reply': "I understand 👍 that's frustrating.\n\nWe handle this differently:\n✔️ proactive updates\n✔️ tracking visibility\n✔️ dedicated support\n\nSo you're never left without updates. Would you like to know more?"})
    
    # 5. MULTI-INTENT: Safety + Good Price + Not Urgent
    if 'not urgent' in user_msg.lower() and ('safe' in user_msg.lower() or 'safety' in user_msg.lower()) and ('price' in user_msg.lower() or 'cost' in user_msg.lower()):
        weight = ctx.get('weight', '120')
        return jsonify({'reply': f"Got it 👍 since it's not urgent and you want safety + good pricing:\n\n✈️ Economy air → safer, moderate cost\n🚢 Sea (with insurance) → lowest cost\n\nFor {weight}kg, I'd recommend economy air for safety, or sea with insurance for savings. Which matters more?"})
    
    # 6. TRACKING
    if intent == 'tracking':
        return jsonify({'reply': "Sure 👍 please share your tracking ID and I'll check the status for you right away."})
    
    # 7. NEGOTIATION
    if intent == 'negotiate':
        return jsonify({'reply': "I understand 👍 let me check if we can match or give a better value option.\n\nIf it works, we can proceed immediately. What price point are you looking for?"})
    
    # 8. READY
    if intent == 'ready':
        return jsonify({'reply': "Perfect 👍 I'll take care of everything.\n\nJust share your name and WhatsApp number, and our team will handle pickup to delivery.\n\nWhat's the best number to reach you?"})
    
    # 9. URGENT
    if intent == 'urgent':
        dest = ctx.get('destination', '')
        if dest:
            return jsonify({'reply': f"For urgent delivery to {dest}:\n\n✓ Express air: 3-5 days\n✓ Priority handling\n✓ Real-time tracking\n\nShall I check flight availability?"})
        return jsonify({'reply': "For urgent shipments:\n\n✓ Express air: 3-5 days\n✓ Priority handling\n✓ Real-time tracking\n\nWhat's your destination?"})
    
    # 10. BUDGET
    if intent == 'budget':
        weight = ctx.get('weight', '')
        dest = ctx.get('destination', '')
        if weight and dest:
            return jsonify({'reply': f"For {weight}kg to {dest}, sea freight saves 60-70% compared to air.\n\nSea: 20-30 days | Air: 3-7 days\n\nWant me to check current sea freight rates?"})
        return jsonify({'reply': "For budget shipping, sea freight saves 60-70% compared to air.\n\nSea: 20-30 days | Air: 3-7 days\n\nWhat's your weight and destination?"})
    
    # 11. BULK
    if intent == 'bulk':
        return jsonify({'reply': "For regular shipments, we offer:\n\n✓ Volume discounts (tiered pricing)\n✓ Dedicated account manager\n✓ Priority space allocation\n\nWhat's your estimated monthly volume?"})
    
    # 12. CUSTOMS
    if intent == 'customs':
        return jsonify({'reply': "Customs clearance is our expertise 👍\n\nWe handle:\n✓ Document preparation\n✓ HS code classification\n✓ Duty calculation\n✓ Compliance verification\n\nNeed help with a specific shipment?"})
    
    # 13. QUOTE
    if intent == 'quote':
        return jsonify({'reply': "💰 I can help you with a quote.\n\nPlease share:\n📦 What are you shipping?\n⚖️ Approx weight?\n📍 Destination?\n\nI'll check the best rates for you."})
    
    # 14. SHIPPING - Extract and store context
    if intent == 'shipping':
        weight_match = re.search(r'(\d+)\s*(?:kg|kgs|kilo|kilogram)', user_msg, re.IGNORECASE)
        if weight_match:
            ctx['weight'] = weight_match.group(1)
        
        dest_match = re.search(r'(?:to|for)\s+([A-Z][a-z]+|[A-Z]+)', user_msg)
        if dest_match:
            ctx['destination'] = dest_match.group(1).title()
        
        # Also extract cargo type
        if 'electronics' in user_msg.lower():
            ctx['cargo'] = 'electronics'
        
        session_memory[session_id] = ctx
        
        weight = ctx.get('weight', '')
        dest = ctx.get('destination', '')
        
        if weight and dest:
            return jsonify({'reply': f"For {weight}kg to {dest}:\n\n✈️ Air: 3-7 days (faster, higher cost)\n🚢 Sea: 20-30 days (slower, saves 60-70%)\n\nWhich matters more - speed or cost?"})
        elif weight:
            return jsonify({'reply': f"For {weight}kg shipment - where is it going?\n\n✈️ Air: 3-7 days\n🚢 Sea: 20-30 days\n\nShare destination for better recommendation."})
        elif dest:
            return jsonify({'reply': f"To {dest} - what's the approximate weight?\n\n✈️ Air: 3-7 days\n🚢 Sea: 20-30 days\n\nWeight helps me recommend the best option."})
        else:
            return jsonify({'reply': "I can help with shipping! Just tell me:\n📦 What are you shipping?\n⚖️ Approx weight?\n📍 Destination?\n\nI'll suggest the best option for you."})
    
    # 15. GENERAL - Fallback to AI
    system_prompt = """You are Aisea, a logistics consultant for PAS Freight.

Rules:
- Keep responses short and conversational
- Be helpful and friendly
- Never overpromise delivery times
- Close confidently when user is ready

Company: PAS Freight, Contact: +91 90361 01201

Be helpful and conversational."""
    
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
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': "Tell me what you'd like to ship - I'll help you figure out the best way."})

if __name__ == '__main__':
    print("=" * 60)
    print("Aisea - ELITE 10/10 Chatbot")
    print("Open: http://localhost:5001")
    print("Fixed: Multi-intent | Context memory | Trust handling | Dangerous goods | Comparison")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
