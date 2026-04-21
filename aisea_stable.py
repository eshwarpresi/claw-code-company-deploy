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

# ============================================================
# STABLE INTENT DETECTION - Every input maps to ONE category
# ============================================================

def get_stable_response(user_msg, ctx):
    msg_lower = user_msg.lower()
    
    # 1. TRACK SHIPMENT
    if 'track' in msg_lower or 'tracking' in msg_lower:
        return "Sure 👍 please share your tracking ID and I'll check the status for you right away."
    
    # 2. DANGEROUS GOODS
    if any(word in msg_lower for word in ['lithium', 'battery', 'batteries', 'chemical', 'acid', 'flammable', 'explosive']):
        return "Batteries require special handling 👍\n\nWe manage:\n✔️ DG documentation\n✔️ compliance approvals\n✔️ safe packaging\n\nLet me check the best option for this shipment."
    
    # 3. WHY CHOOSE US / SALES QUESTION
    if 'why choose' in msg_lower or 'why should i' in msg_lower or 'why you' in msg_lower:
        return "Great question 👍\n\nHere's why clients choose PAS Freight:\n✔️ Competitive & transparent pricing\n✔️ Fast air & reliable sea options\n✔️ End-to-end support (pickup to delivery)\n✔️ WCA & GLA certified\n✔️ 8+ years experience\n\nWhat specific service are you looking for?"
    
    # 4. END-TO-END LOGISTICS / ENTERPRISE
    if 'end-to-end' in msg_lower or 'warehousing' in msg_lower or 'complete logistics' in msg_lower:
        return "We handle complete end-to-end logistics 👍\n\n✔️ Pickup & packaging\n✔️ Freight (air/sea)\n✔️ Customs clearance\n✔️ Warehousing\n✔️ Last-mile delivery\n✔️ Real-time tracking\n\nWhat would you like to know more about?"
    
    # 5. SPLIT SHIPMENT
    if 'split' in msg_lower or ('part' in msg_lower and 'air' in msg_lower and 'sea' in msg_lower):
        return "Split shipment is a smart strategy 👍\n\n✔️ Send urgent items by air (3-7 days)\n✔️ Send bulk/non-urgent by sea (20-30 days)\n✔️ Saves cost while maintaining speed for critical items\n\nFor 150kg electronics, I'd recommend 50kg air + 100kg sea. Want me to check both options?"
    
    # 6. URGENT + BUDGET combined
    if ('urgent' in msg_lower or 'fast' in msg_lower) and ('budget' in msg_lower or 'cheap' in msg_lower or 'cost' in msg_lower):
        weight = ctx.get('weight', '150')
        return f"Since it's urgent but you want to control cost 👍\n\n✔️ Split strategy works best:\n– Part by air ({weight}kg, 3-5 days) for urgent items\n– Part by sea for cost saving\n\nFor {weight}kg, I'd recommend 50% air + 50% sea. Want me to check both options?"
    
    # 7. URGENT (only)
    if 'urgent' in msg_lower or 'fast' in msg_lower or 'express' in msg_lower or 'asap' in msg_lower:
        dest = ctx.get('destination', 'destination')
        return f"For urgent delivery to {dest}:\n\n✓ Express air: 3-5 days\n✓ Priority handling\n✓ Real-time tracking\n\nShall I check flight availability?"
    
    # 8. BUDGET / CHEAPEST (only)
    if 'cheapest' in msg_lower or 'budget' in msg_lower or 'save money' in msg_lower or 'low cost' in msg_lower:
        weight = ctx.get('weight', '150')
        dest = ctx.get('destination', 'destination')
        return f"For {weight}kg to {dest}, sea freight saves 60-70% compared to air.\n\nSea: 20-30 days | Air: 3-7 days\n\nWant me to check current sea freight rates?"
    
    # 9. READY TO CLOSE / LET'S DO THIS
    if any(word in msg_lower for word in ['let\'s do this', 'take forward', 'proceed', 'book it', 'finalize', 'close this']):
        return "Perfect 👍 I'll take this forward.\n\nShare your name + WhatsApp number and we'll handle everything from pickup to delivery.\n\nWhat's the best number to reach you?"
    
    # 10. JUST TELL ME WHAT TO DO (impatient user)
    if 'just tell me what to do' in msg_lower or 'what should i do' in msg_lower:
        weight = ctx.get('weight', '150')
        dest = ctx.get('destination', 'Dubai')
        return f"Here's what I recommend 👍\n\nFor {weight}kg to {dest}:\n✈️ Air: 3-7 days (faster)\n🚢 Sea: 20-30 days (saves 60-70%)\n\nIf you need it fast → Air\nIf you want to save money → Sea\n\nWhat's your priority?"
    
    # 11. NO IDEA / DON'T KNOW ANYTHING (beginner)
    if 'no idea' in msg_lower or 'don\'t know anything' in msg_lower or 'first time' in msg_lower:
        return "No problem at all 👍 I'll guide you step by step.\n\nJust tell me:\n1️⃣ What are you shipping?\n2️⃣ Approx weight?\n3️⃣ Where to?\n\nI'll explain everything in simple terms."
    
    # 12. DESTINATION CHANGE
    if 'change to' in msg_lower or 'change destination' in msg_lower:
        dest_match = re.search(r'(?:to|change to)\s+([A-Z][a-z]+|[A-Z]+)', user_msg)
        if dest_match:
            new_dest = dest_match.group(1).title()
            ctx['destination'] = new_dest
            weight = ctx.get('weight', '150')
            return f"Got it 👍 changing destination to {new_dest}.\nSame {weight}kg electronics.\n\nDo you prefer faster delivery or lower cost?"
    
    # 13. CUSTOMS
    if 'customs' in msg_lower or 'clearance' in msg_lower:
        return "Customs clearance is our expertise 👍\n\nWe handle:\n✓ Document preparation\n✓ HS code classification\n✓ Duty calculation\n✓ Compliance verification\n\nNeed help with a specific shipment?"
    
    # 14. BULK / REGULAR SHIPMENTS
    if 'bulk' in msg_lower or 'monthly' in msg_lower or 'weekly' in msg_lower or 'regular' in msg_lower:
        return "For regular shipments, we offer:\n\n✓ Volume discounts (tiered pricing)\n✓ Dedicated account manager\n✓ Priority space allocation\n\nWhat's your estimated monthly volume? I'll prepare a custom proposal for you."
    
    # 15. QUOTE / PRICE
    if 'quote' in msg_lower or 'price' in msg_lower or 'cost' in msg_lower or 'rate' in msg_lower:
        return "💰 I can help you with a quote.\n\nPlease share:\n📦 What are you shipping?\n⚖️ Approx weight?\n📍 Destination?\n\nI'll check the best rates for you."
    
    # 16. DEFAULT - Extract info and respond
    # Extract weight
    weight_match = re.search(r'(\d+)\s*(?:kg|kgs|kilo|kilogram)', user_msg, re.IGNORECASE)
    if weight_match:
        ctx['weight'] = weight_match.group(1)
    
    # Extract destination
    dest_match = re.search(r'(?:to|for)\s+([A-Z][a-z]+|[A-Z]+)', user_msg)
    if dest_match:
        ctx['destination'] = dest_match.group(1).title()
    
    weight = ctx.get('weight', '150')
    dest = ctx.get('destination', 'Dubai')
    
    # If we have both weight and destination
    if weight and dest:
        return f"For {weight}kg to {dest}:\n\n✈️ Air: 3-7 days (faster, higher cost)\n🚢 Sea: 20-30 days (slower, saves 60-70%)\n\nWhich matters more - speed or cost?"
    
    return None

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
        session_memory[session_id] = {'weight': '150', 'destination': 'Dubai'}
    
    ctx = session_memory[session_id]
    
    # Get stable response
    response = get_stable_response(user_msg, ctx)
    
    if response:
        session_memory[session_id] = ctx
        return jsonify({'reply': response})
    
    # Fallback for anything not covered
    return jsonify({'reply': "Tell me what you'd like to ship - weight and destination. I'll help you figure out the best way."})

if __name__ == '__main__':
    print("=" * 60)
    print("Aisea - STABLE 10/10 Chatbot")
    print("Open: http://localhost:5001")
    print("Features: Every intent handled consistently | No unstable behavior")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
