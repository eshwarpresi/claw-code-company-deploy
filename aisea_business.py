import openai
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Aisea - PAS Freight AI</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
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
        
        #pasfreight-chat-btn:hover {
            transform: scale(1.08);
            box-shadow: 0 12px 32px rgba(0,0,0,0.25);
        }
        
        .chat-icon {
            font-size: 28px;
            color: white;
        }
        
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
        
        @keyframes blink {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.7; transform: scale(1.1); }
        }
        
        #pasfreight-chat-window {
            position: fixed;
            bottom: 90px;
            right: 24px;
            width: 400px;
            height: 600px;
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
        
        .header-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .avatar {
            width: 40px;
            height: 40px;
            background: rgba(255,255,255,0.15);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        
        .header-text h3 {
            font-size: 16px;
            font-weight: 600;
            letter-spacing: -0.3px;
        }
        
        .header-text p {
            font-size: 10px;
            opacity: 0.8;
            margin-top: 2px;
        }
        
        .close-chat {
            background: rgba(255,255,255,0.1);
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s;
        }
        
        .close-chat:hover {
            background: rgba(255,255,255,0.2);
            transform: scale(1.05);
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f7f9fc;
        }
        
        .message {
            margin-bottom: 16px;
            display: flex;
            animation: slideIn 0.3s ease;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .user-message {
            justify-content: flex-end;
        }
        
        .bot-message {
            justify-content: flex-start;
        }
        
        .bubble {
            max-width: 85%;
            padding: 10px 14px;
            border-radius: 20px;
            font-size: 13px;
            line-height: 1.45;
            font-weight: 400;
        }
        
        .user-message .bubble {
            background: #2a5298;
            color: white;
            border-bottom-right-radius: 5px;
        }
        
        .bot-message .bubble {
            background: white;
            color: #1a202c;
            border: 1px solid #e2e8f0;
            border-bottom-left-radius: 5px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        }
        
        .suggestion-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 12px;
        }
        
        .suggestion-btn {
            background: #f1f5f9;
            border: 1px solid #e2e8f0;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            cursor: pointer;
            color: #1e3c72;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .suggestion-btn:hover {
            background: #2a5298;
            color: white;
            border-color: #2a5298;
        }
        
        .main-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 8px;
        }
        
        .main-btn {
            background: #f1f5f9;
            color: #1e293b;
            border: none;
            padding: 8px 14px;
            border-radius: 24px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .main-btn:hover {
            background: #2a5298;
            color: white;
            transform: translateY(-1px);
        }
        
        .sub-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 8px;
        }
        
        .sub-btn {
            background: #e9ecef;
            color: #495057;
            border: none;
            padding: 6px 12px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 500;
            transition: all 0.2s;
        }
        
        .sub-btn:hover {
            background: #2a5298;
            color: white;
        }
        
        .contact-info {
            background: #f8fafc;
            padding: 10px;
            border-radius: 12px;
            margin-top: 6px;
            font-size: 11px;
            border: 1px solid #e2e8f0;
        }
        
        .chat-input {
            padding: 12px 16px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 10px 16px;
            border: 1px solid #e2e8f0;
            border-radius: 28px;
            font-size: 13px;
            outline: none;
            font-family: 'Inter', sans-serif;
            transition: all 0.2s;
        }
        
        .chat-input input:focus {
            border-color: #2a5298;
            box-shadow: 0 0 0 3px rgba(42,82,152,0.1);
        }
        
        .chat-input button {
            background: #2a5298;
            color: white;
            border: none;
            width: 40px;
            height: 40px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-input button:hover {
            background: #1e3c72;
            transform: scale(1.02);
        }
        
        .typing {
            display: inline-flex;
            gap: 5px;
            padding: 6px 0;
        }
        
        .typing span {
            width: 7px;
            height: 7px;
            background: #94a3b8;
            border-radius: 50%;
            animation: typingBounce 1.4s infinite;
        }
        
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        
        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-8px); }
        }
        
        .chat-messages::-webkit-scrollbar {
            width: 5px;
        }
        
        .chat-messages::-webkit-scrollbar-track {
            background: #e2e8f0;
            border-radius: 10px;
        }
        
        .chat-messages::-webkit-scrollbar-thumb {
            background: #94a3b8;
            border-radius: 10px;
        }
        
        @media (max-width: 500px) {
            #pasfreight-chat-window {
                width: 100%;
                height: 100%;
                bottom: 0;
                right: 0;
                border-radius: 0;
            }
            
            #pasfreight-chat-btn {
                bottom: 16px;
                right: 16px;
            }
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
                <div class="bubble">Hi, I'm Aisea. Need a shipping quote or logistics advice? Let me know your shipment details.</div>
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
            <input type="text" id="userInput" placeholder="Ask Aisea about shipping..." autocomplete="off">
            <button id="sendBtn">➤</button>
        </div>
    </div>

    <script>
        const chatBtn = document.getElementById('pasfreight-chat-btn');
        const chatWindow = document.getElementById('pasfreight-chat-window');
        const closeChatBtn = document.getElementById('closeChatBtn');
        const notificationBadge = document.getElementById('notificationBadge');
        const messagesDiv = document.getElementById('chatMessages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        
        let isOpen = false;
        let notified = false;
        let lastBotResponse = '';
        
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
        
        function addMessage(text, isUser, showSuggestions = false) {
            const div = document.createElement('div');
            div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
            div.innerHTML = `<div class="bubble">${text}</div>`;
            messagesDiv.appendChild(div);
            
            if (showSuggestions && !isUser) {
                addSuggestionButtons();
            }
            
            div.scrollIntoView({ behavior: 'smooth' });
        }
        
        function addSuggestionButtons() {
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">
                <div class="suggestion-buttons">
                    <button class="suggestion-btn" onclick="sendQuick('Get exact quote')">💰 Get Exact Quote</button>
                    <button class="suggestion-btn" onclick="sendQuick('Compare air vs sea')">📊 Compare Air vs Sea</button>
                    <button class="suggestion-btn" onclick="sendQuick('Talk to expert')">🎧 Talk to Expert</button>
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
        
        window.showImportAir = function() {
            addMessage("IMPORT - AIR", true);
            addContactInfo("IMPORT AIR FREIGHT", 
                ["+91 99869 42772", "+91 63615 21413"],
                ["gj@pasfreight.com", "rachana@pasfreight.com"]);
        };
        
        window.showImportSea = function() {
            addMessage("IMPORT - SEA", true);
            addContactInfo("IMPORT SEA FREIGHT", 
                ["+91 93648 81371", "+91 63615 21413"],
                ["vinodh@pasfreight.com", "gj@pasfreight.com"]);
        };
        
        window.showExportOptions = function() {
            addMessage("EXPORT", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📤 <strong>EXPORT - Select Mode:</strong><br>
                <div class="sub-buttons">
                    <button class="sub-btn" onclick="showExportAir()">✈️ AIR (3-7 days)</button>
                    <button class="sub-btn" onclick="showExportSea()">🚢 SEA (20-35 days)</button>
                </div>
            </div>`;
            messagesDiv.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        };
        
        window.showExportAir = function() {
            addMessage("EXPORT - AIR", true);
            addContactInfo("EXPORT AIR FREIGHT", 
                ["+91 93648 81371", "+91 63615 26659"],
                ["vinodh@pasfreight.com", "kavan@pasfreight.com"]);
        };
        
        window.showExportSea = function() {
            addMessage("EXPORT - SEA", true);
            addContactInfo("EXPORT SEA FREIGHT", 
                ["+91 93648 81371", "+91 63615 26659"],
                ["vinodh@pasfreight.com", "kavan@pasfreight.com"]);
        };
        
        window.showCustoms = function() {
            addMessage("CUSTOMS CLEARANCE", true);
            addContactInfo("CUSTOMS CLEARANCE", 
                ["+91 63615 26664"],
                ["ajith@pasfreight.com", "edi.blr@pasfreight.com"]);
        };
        
        window.showCargo = function() {
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
        };
        
        window.showDomesticCargo = function() {
            addMessage("DOMESTIC CARGO", true);
            addContactInfo("DOMESTIC CARGO", 
                ["+91 63615 26659"],
                ["kavan@pasfreight.com", "info@pasfreight.com"]);
        };
        
        window.showInternationalCargo = function() {
            addMessage("INTERNATIONAL CARGO", true);
            addContactInfo("INTERNATIONAL CARGO", 
                ["+91 63615 26659"],
                ["kavan@pasfreight.com", "info@pasfreight.com"]);
        };
        
        window.showContact = function() {
            addMessage("CONTACT", true);
            addContactInfo("PAS FREIGHT CONTACT", 
                ["+91 90361 01201"],
                ["shivu@pasfreight.com", "info@pasfreight.com"]);
        };
        
        window.showAbout = function() {
            addMessage("ABOUT", true);
            addMessage("🏢 <strong>PAS Freight Services Pvt Ltd</strong><br><br>📍 Jakkur-BDA, Bangalore<br>📞 +91 90361 01201<br>✅ WCA & GLA Certified<br>🌟 8+ years experience", false);
        };
        
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
                    body: JSON.stringify({ message: text })
                });
                const data = await response.json();
                hideTyping();
                const isSalesIntent = text.toLowerCase().includes('quote') || text.toLowerCase().includes('price') || text.toLowerCase().includes('shipping');
                addMessage(data.reply, false, isSalesIntent);
            } catch(error) {
                hideTyping();
                addMessage('Call +91 90361 01201 for immediate assistance.', false);
            }
        }
        
        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
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
    user_msg = data.get('message', '')
    
    system_prompt = """You are Aisea, a logistics expert and sales assistant for PAS Freight.

You are NOT a chatbot. You are:
- A logistics consultant
- A sales closer

GOALS:
1. Help users with shipping decisions
2. Give estimated pricing + transit time
3. Ask for missing shipment details
4. Guide conversation step-by-step
5. Capture leads (name + phone)
6. Push towards booking

STYLE:
- Short, sharp, professional
- No long paragraphs
- No "I'm glad you asked"
- No robotic tone

RULES:
- Always ask next logical question
- Always suggest best shipping method
- Use memory from previous messages
- Add urgency where possible
- Push for lead capture after giving value

EXAMPLES:

Bad: "I'm glad you asked! We provide..."
Good: "We handle air (3-7 days), sea (20-35 days), customs, trucking. What do you need—quote or info?"

Bad: "Please share your number"
Good: "I can lock the best rate for you. Share your number—our team will call you within 10 minutes."

Bad: "100kg Singapore" then stops
Good: "Got it - 100kg to Singapore. Air freight (~$5-7/kg, 3-5 days) or sea (~$2-3/kg, 25-30 days)? Want me to get a firm quote?"

END GOAL: Convert every conversation into a lead or booking.

Company: PAS Freight Services Pvt Ltd, Bangalore. Contact: +91 90361 01201, Email: shivu@pasfreight.com"""

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
        return jsonify({'reply': 'Call +91 90361 01201 for best rates. Our team will lock the best price for you.'})

if __name__ == '__main__':
    print("=" * 60)
    print("✨ Aisea - Business/Sales Assistant")
    print("📱 Open: http://localhost:5001")
    print("🎯 Features: Lead capture | Urgency | Smart follow-ups")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
