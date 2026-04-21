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
    <title>PAS Freight AI - Advanced</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        #pasfreight-chat-btn {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 52px;
            height: 52px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            border: none;
            z-index: 999999;
        }
        
        #pasfreight-chat-btn:hover { transform: scale(1.05); }
        .chat-icon { font-size: 26px; color: white; }
        
        .notification-badge {
            position: absolute;
            top: -3px;
            right: -3px;
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
            bottom: 82px;
            right: 20px;
            width: 360px;
            height: 520px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: none;
            z-index: 999998;
            border: none;
            overflow: hidden;
            flex-direction: column;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 12px 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .header-info { display: flex; align-items: center; gap: 8px; }
        .avatar {
            width: 32px;
            height: 32px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }
        .header-text h3 { font-size: 13px; font-weight: 600; }
        .header-text p { font-size: 9px; opacity: 0.8; }
        
        .close-chat {
            background: none;
            border: none;
            color: white;
            font-size: 18px;
            cursor: pointer;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            background: #f8f9fa;
        }
        
        .message { margin-bottom: 12px; display: flex; }
        .user-message { justify-content: flex-end; }
        .bot-message { justify-content: flex-start; }
        
        .bubble {
            max-width: 85%;
            padding: 8px 12px;
            border-radius: 18px;
            font-size: 12px;
            line-height: 1.4;
        }
        
        .user-message .bubble {
            background: #2a5298;
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .bot-message .bubble {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        
        .main-buttons { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
        .main-btn {
            background: #1e3c72;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 500;
        }
        .main-btn:hover { background: #2a5298; }
        
        .sub-buttons { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
        .sub-btn {
            background: #e9ecef;
            color: #333;
            border: none;
            padding: 5px 10px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 10px;
        }
        .sub-btn:hover { background: #2a5298; color: white; }
        
        .contact-info {
            background: #f0f2f5;
            padding: 8px;
            border-radius: 10px;
            margin-top: 6px;
            font-size: 10px;
        }
        
        .chat-input {
            padding: 10px;
            background: white;
            border-top: 1px solid #e5e5e5;
            display: flex;
            gap: 8px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 10px 14px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 12px;
            outline: none;
        }
        
        .chat-input input:focus { border-color: #2a5298; }
        
        .chat-input button {
            background: #2a5298;
            color: white;
            border: none;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 16px;
        }
        
        .typing { display: inline-flex; gap: 4px; padding: 4px 0; }
        .typing span {
            width: 6px;
            height: 6px;
            background: #999;
            border-radius: 50%;
            animation: typingBounce 1.4s infinite;
        }
        
        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }
        
        @media (max-width: 500px) {
            #pasfreight-chat-window {
                width: 100%;
                height: 100%;
                bottom: 0;
                right: 0;
                border-radius: 0;
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
                    <h3>PAS Freight AI</h3>
                    <p>Logistics Assistant | 24/7</p>
                </div>
            </div>
            <button class="close-chat" id="closeChatBtn">✕</button>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="bubble">Hi, I'm PAS Freight AI Assistant. I can help with import/export, customs clearance, and cargo services. Ask me anything about logistics!</div>
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
            <input type="text" id="userInput" placeholder="Ask me anything..." autocomplete="off">
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
        
        // IMPORT Options
        window.showImportOptions = function() {
            addMessage("IMPORT", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📥 <strong>IMPORT - Select Mode:</strong><br>
                <div class="sub-buttons">
                    <button class="sub-btn" onclick="showImportAir()">✈️ AIR</button>
                    <button class="sub-btn" onclick="showImportSea()">🚢 SEA</button>
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
        
        // EXPORT Options
        window.showExportOptions = function() {
            addMessage("EXPORT", true);
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.innerHTML = `<div class="bubble">📤 <strong>EXPORT - Select Mode:</strong><br>
                <div class="sub-buttons">
                    <button class="sub-btn" onclick="showExportAir()">✈️ AIR</button>
                    <button class="sub-btn" onclick="showExportSea()">🚢 SEA</button>
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
        
        // CUSTOMS
        window.showCustoms = function() {
            addMessage("CUSTOMS CLEARANCE", true);
            addContactInfo("CUSTOMS CLEARANCE", 
                ["+91 63615 26664"],
                ["ajith@pasfreight.com", "edi.blr@pasfreight.com"]);
        };
        
        // CARGO
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
        
        // CONTACT
        window.showContact = function() {
            addMessage("CONTACT", true);
            addContactInfo("PAS FREIGHT CONTACT", 
                ["+91 90361 01201"],
                ["shivu@pasfreight.com", "info@pasfreight.com"]);
        };
        
        // ABOUT
        window.showAbout = function() {
            addMessage("ABOUT", true);
            addMessage("🏢 <strong>PAS Freight Services Pvt Ltd</strong><br><br>📍 Jakkur-BDA, Bangalore - 560092<br>📞 +91 90361 01201<br>✉️ shivu@pasfreight.com<br>✅ WCA:115513 | GLA:1166251<br>🌟 8+ years experience<br>🎯 Bangalore's most trusted logistics partner", false);
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
                addMessage(data.reply, false);
            } catch(error) {
                hideTyping();
                addMessage('For assistance with PAS Freight services, call +91 90361 01201 or email shivu@pasfreight.com', false);
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
    
    system_prompt = """You are PAS Freight AI Assistant - a professional, helpful logistics assistant.

COMPANY INFO:
- Name: PAS Freight Services Pvt Ltd
- Location: Bangalore, India
- Services: Air Freight, Sea Freight, Customs Clearance, Domestic Trucking, Courier, Warehousing
- Contact: +91 90361 01201
- Email: shivu@pasfreight.com
- Certifications: WCA (115513), GLA (1166251)

RESPONSE STYLE (Professional, crisp, helpful like Agentforce):
- Greetings: "Hi there! How can I assist you with your logistics needs today?"
- Services: "We offer Import/Export (Air/Sea), Customs Clearance, Domestic Trucking, and Courier services."
- Name: "I'm PAS Freight AI Assistant. How can I help with your logistics needs?"
- Rates: "For exact rates, please call +91 90361 01201. Our team will provide you the best quote."
- Off-topic: "I'm here to assist with logistics. Let me know if you need help with import/export or cargo services."
- Negative: "Sorry, I can't assist with that. Let me know if you have any logistics-related questions."

Be professional, direct, and helpful. Keep responses to 1-2 sentences."""

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=100,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': 'For assistance with PAS Freight services, call +91 90361 01201 or email shivu@pasfreight.com'})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PAS Freight Advanced AI Assistant")
    print("📱 Open: http://localhost:5001")
    print("📋 Features: IMPORT | EXPORT | CUSTOMS | CARGO | CONTACT | ABOUT")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
