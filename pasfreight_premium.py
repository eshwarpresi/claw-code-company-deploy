import openai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <title>PAS Freight AI | Smart Logistics Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica Neue', sans-serif;
            background: linear-gradient(145deg, #0f0f13 0%, #1a1a2e 100%);
            height: 100vh;
            overflow: hidden;
        }

        /* Main Container */
        .app {
            display: flex;
            height: 100vh;
            background: #0f0f13;
        }

        /* Sidebar */
        .sidebar {
            width: 280px;
            background: #1e1e2a;
            border-right: 1px solid #2a2a35;
            display: flex;
            flex-direction: column;
            transition: all 0.3s ease;
        }

        .sidebar-header {
            padding: 24px 20px;
            border-bottom: 1px solid #2a2a35;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-icon {
            width: 40px;
            height: 40px;
            background: linear-gradient(135deg, #10a37f, #1a7f64);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 22px;
        }

        .logo-text h2 {
            font-size: 18px;
            font-weight: 600;
            color: #ececec;
        }

        .logo-text p {
            font-size: 11px;
            color: #8e8ea0;
            margin-top: 2px;
        }

        .new-chat-btn {
            margin: 20px;
            padding: 12px 16px;
            background: #2a2a35;
            border: 1px solid #3a3a45;
            border-radius: 12px;
            color: #ececec;
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 10px;
            transition: all 0.2s;
        }

        .new-chat-btn:hover {
            background: #3a3a45;
            border-color: #10a37f;
        }

        .sidebar-menu {
            flex: 1;
            padding: 0 12px;
        }

        .menu-item {
            padding: 12px 16px;
            border-radius: 10px;
            color: #8e8ea0;
            font-size: 14px;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 12px;
            transition: all 0.2s;
            margin-bottom: 4px;
        }

        .menu-item:hover {
            background: #2a2a35;
            color: #ececec;
        }

        .sidebar-footer {
            padding: 20px;
            border-top: 1px solid #2a2a35;
        }

        .user-info {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .user-avatar {
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #10a37f, #1a7f64);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
        }

        .user-details p {
            font-size: 13px;
            color: #ececec;
            font-weight: 500;
        }

        .user-details span {
            font-size: 10px;
            color: #8e8ea0;
        }

        /* Main Chat Area */
        .chat-main {
            flex: 1;
            display: flex;
            flex-direction: column;
            background: #0f0f13;
        }

        .chat-header {
            padding: 16px 24px;
            background: #0f0f13;
            border-bottom: 1px solid #2a2a35;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .chat-header h3 {
            font-size: 16px;
            font-weight: 500;
            color: #ececec;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: #10a37f;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #10a37f;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* Messages Container */
        .messages-container {
            flex: 1;
            overflow-y: auto;
            padding: 24px;
        }

        .messages-container::-webkit-scrollbar {
            width: 5px;
        }
        .messages-container::-webkit-scrollbar-track {
            background: #2a2a35;
        }
        .messages-container::-webkit-scrollbar-thumb {
            background: #10a37f;
            border-radius: 5px;
        }

        .message {
            display: flex;
            margin-bottom: 24px;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            justify-content: flex-end;
        }

        .message.bot {
            justify-content: flex-start;
        }

        .message-avatar {
            width: 36px;
            height: 36px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
        }

        .message.user .message-avatar {
            background: linear-gradient(135deg, #10a37f, #1a7f64);
            margin-left: 12px;
            order: 2;
        }

        .message.bot .message-avatar {
            background: #2a2a35;
            margin-right: 12px;
        }

        .message-content {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 20px;
            font-size: 14px;
            line-height: 1.5;
        }

        .message.user .message-content {
            background: linear-gradient(135deg, #10a37f, #1a7f64);
            color: white;
            border-bottom-right-radius: 4px;
        }

        .message.bot .message-content {
            background: #2a2a35;
            color: #ececec;
            border-bottom-left-radius: 4px;
        }

        /* Typing Indicator */
        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 4px 0;
        }
        .typing-indicator span {
            width: 6px;
            height: 6px;
            background: #8e8ea0;
            border-radius: 50%;
            animation: typingBounce 1.4s infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }

        /* Input Area */
        .input-area {
            padding: 20px 24px;
            background: #0f0f13;
            border-top: 1px solid #2a2a35;
        }

        .input-wrapper {
            display: flex;
            gap: 12px;
            align-items: center;
            background: #2a2a35;
            border-radius: 28px;
            padding: 8px 8px 8px 20px;
            border: 1px solid #3a3a45;
            transition: all 0.2s;
        }

        .input-wrapper:focus-within {
            border-color: #10a37f;
        }

        .input-wrapper input {
            flex: 1;
            background: none;
            border: none;
            color: #ececec;
            font-size: 14px;
            outline: none;
            font-family: inherit;
        }

        .input-wrapper input::placeholder {
            color: #6e6e80;
        }

        .input-actions {
            display: flex;
            gap: 6px;
        }

        .input-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 20px;
            padding: 8px;
            border-radius: 50%;
            color: #8e8ea0;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .input-btn:hover {
            background: #3a3a45;
            color: #ececec;
        }

        .send-btn {
            background: #10a37f;
            color: white;
            border-radius: 50%;
            width: 40px;
            height: 40px;
        }

        .send-btn:hover {
            background: #1a7f64;
        }

        .voice-active {
            background: #ef4444 !important;
            color: white !important;
            animation: voicePulse 1s infinite;
        }

        @keyframes voicePulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        /* Service Buttons */
        .service-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 10px;
        }

        .service-btn {
            background: #2a2a35;
            border: 1px solid #3a3a45;
            padding: 8px 16px;
            border-radius: 25px;
            font-size: 12px;
            cursor: pointer;
            color: #ececec;
            transition: all 0.2s;
        }

        .service-btn:hover {
            background: #3a3a45;
            border-color: #10a37f;
        }

        .contact-info {
            background: #2a2a35;
            padding: 12px;
            border-radius: 12px;
            margin-top: 10px;
            font-size: 12px;
            border: 1px solid #3a3a45;
        }

        .image-preview {
            max-width: 150px;
            max-height: 120px;
            border-radius: 12px;
            margin-top: 8px;
            cursor: pointer;
        }

        /* Mobile Responsive */
        @media (max-width: 768px) {
            .sidebar {
                position: fixed;
                left: -280px;
                z-index: 1000;
                height: 100vh;
            }
            .sidebar.open {
                left: 0;
            }
            .message-content {
                max-width: 85%;
            }
        }
    </style>
</head>
<body>
<div class="app">
    <!-- Sidebar -->
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <div class="logo">
                <div class="logo-icon">📦</div>
                <div class="logo-text">
                    <h2>PAS Freight AI</h2>
                    <p>Smart Logistics Assistant</p>
                </div>
            </div>
        </div>
        <div class="new-chat-btn" onclick="resetChat()">
            <span>+</span> New Chat
        </div>
        <div class="sidebar-menu">
            <div class="menu-item" onclick="showMainMenu()">
                <span>📦</span> Main Menu
            </div>
            <div class="menu-item" onclick="showContact()">
                <span>📞</span> Contact Us
            </div>
            <div class="menu-item" onclick="showAbout()">
                <span>🏢</span> About Us
            </div>
        </div>
        <div class="sidebar-footer">
            <div class="user-info">
                <div class="user-avatar">👤</div>
                <div class="user-details">
                    <p>Guest User</p>
                    <span>Online</span>
                </div>
            </div>
        </div>
    </div>

    <!-- Main Chat Area -->
    <div class="chat-main">
        <div class="chat-header">
            <h3>PAS Freight Assistant</h3>
            <div class="status">
                <span class="status-dot"></span>
                <span>24/7 Support</span>
            </div>
        </div>

        <div class="messages-container" id="messagesContainer">
            <div class="message bot">
                <div class="message-avatar">🤖</div>
                <div class="message-content">Hi, I'm PAS Freight AI Assistant. I can help with import/export, customs clearance, and cargo services. Ask me anything about logistics!</div>
            </div>
        </div>

        <div class="input-area">
            <div class="input-wrapper">
                <input type="text" id="userInput" placeholder="Ask me anything about logistics...">
                <div class="input-actions">
                    <button class="input-btn" id="voiceBtn" title="Voice Input">🎤</button>
                    <button class="input-btn" id="cameraBtn" title="Upload Screenshot">📷</button>
                    <button class="input-btn send-btn" id="sendBtn">➤</button>
                </div>
                <input type="file" id="cameraInput" style="display:none" accept="image/*">
            </div>
        </div>
    </div>
</div>

<script>
    let recognition = null;
    let isListening = false;
    let isVoiceMode = false;

    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-IN';
        
        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            document.getElementById('userInput').value = text;
            document.getElementById('voiceBtn').classList.remove('voice-active');
            isListening = false;
            isVoiceMode = true;
            sendMessage();
        };
        
        recognition.onerror = function() {
            document.getElementById('voiceBtn').classList.remove('voice-active');
            isListening = false;
        };
        
        recognition.onend = function() {
            document.getElementById('voiceBtn').classList.remove('voice-active');
            isListening = false;
        };
    }
    
    document.getElementById('voiceBtn').onclick = function() {
        if (!recognition) {
            addMessage("Voice support requires Chrome browser.", false);
            return;
        }
        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
            this.classList.add('voice-active');
            isListening = true;
        }
    };
    
    document.getElementById('cameraBtn').onclick = () => document.getElementById('cameraInput').click();
    document.getElementById('cameraInput').onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const div = document.createElement('div');
                div.className = 'message user';
                div.innerHTML = `<div class="message-avatar">👤</div>
                                <div class="message-content">📷 Screenshot uploaded</div>`;
                document.getElementById('messagesContainer').appendChild(div);
                div.scrollIntoView({ behavior: 'smooth' });
                
                setTimeout(() => {
                    addMessage("Thanks for sharing! Our team will review it. Call +91 90361 01201 for immediate help.", false);
                }, 500);
            };
            reader.readAsDataURL(file);
        }
        this.value = '';
    };

    function addMessage(text, isUser) {
        const container = document.getElementById('messagesContainer');
        const div = document.createElement('div');
        div.className = `message ${isUser ? 'user' : 'bot'}`;
        div.innerHTML = `<div class="message-avatar">${isUser ? '👤' : '🤖'}</div>
                        <div class="message-content">${text}</div>`;
        container.appendChild(div);
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
        
        const container = document.getElementById('messagesContainer');
        const div = document.createElement('div');
        div.className = 'message bot';
        div.innerHTML = `<div class="message-avatar">🤖</div><div class="message-content">${html}</div>`;
        container.appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }

    function addServiceButtons(title, buttonsHtml) {
        const container = document.getElementById('messagesContainer');
        const div = document.createElement('div');
        div.className = 'message bot';
        div.innerHTML = `<div class="message-avatar">🤖</div><div class="message-content">${title}<div class="service-buttons">${buttonsHtml}</div></div>`;
        container.appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }

    function showMainMenu() {
        addMessage("Main Menu", true);
        const container = document.getElementById('messagesContainer');
        const div = document.createElement('div');
        div.className = 'message bot';
        div.innerHTML = `<div class="message-avatar">🤖</div>
                        <div class="message-content">📦 Select a service:<br>
                        <div class="service-buttons">
                            <button class="service-btn" onclick="showImportOptions()">📥 IMPORT</button>
                            <button class="service-btn" onclick="showExportOptions()">📤 EXPORT</button>
                            <button class="service-btn" onclick="showCustoms()">📋 CUSTOMS</button>
                            <button class="service-btn" onclick="showCargo()">🚚 CARGO</button>
                        </div></div>`;
        container.appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }

    function showImportOptions() {
        addMessage("IMPORT", true);
        const container = document.getElementById('messagesContainer');
        const div = document.createElement('div');
        div.className = 'message bot';
        div.innerHTML = `<div class="message-avatar">🤖</div>
                        <div class="message-content">📥 IMPORT - Select Mode:<br>
                        <div class="service-buttons">
                            <button class="service-btn" onclick="showImportAir()">✈️ AIR</button>
                            <button class="service-btn" onclick="showImportSea()">🚢 SEA</button>
                        </div></div>`;
        container.appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }

    function showImportAir() {
        addMessage("IMPORT - AIR", true);
        addContactInfo("IMPORT AIR FREIGHT", 
            ["+91 99869 42772", "+91 63615 21413"],
            ["gj@pasfreight.com", "rachana@pasfreight.com"]);
    }

    function showImportSea() {
        addMessage("IMPORT - SEA", true);
        addContactInfo("IMPORT SEA FREIGHT (FCL/LCL)", 
            ["+91 93648 81371", "+91 63615 21413"],
            ["vinodh@pasfreight.com", "gj@pasfreight.com"]);
    }

    function showExportOptions() {
        addMessage("EXPORT", true);
        const container = document.getElementById('messagesContainer');
        const div = document.createElement('div');
        div.className = 'message bot';
        div.innerHTML = `<div class="message-avatar">🤖</div>
                        <div class="message-content">📤 EXPORT - Select Mode:<br>
                        <div class="service-buttons">
                            <button class="service-btn" onclick="showExportAir()">✈️ AIR</button>
                            <button class="service-btn" onclick="showExportSea()">🚢 SEA</button>
                        </div></div>`;
        container.appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }

    function showExportAir() {
        addMessage("EXPORT - AIR", true);
        addContactInfo("EXPORT AIR FREIGHT", 
            ["+91 93648 81371", "+91 63615 26659"],
            ["vinodh@pasfreight.com", "kavan@pasfreight.com"]);
    }

    function showExportSea() {
        addMessage("EXPORT - SEA", true);
        addContactInfo("EXPORT SEA FREIGHT", 
            ["+91 93648 81371", "+91 63615 26659"],
            ["vinodh@pasfreight.com", "kavan@pasfreight.com"]);
    }

    function showCustoms() {
        addMessage("CUSTOMS CLEARANCE", true);
        addContactInfo("CUSTOMS CLEARANCE", 
            ["+91 63615 26664"],
            ["ajith@pasfreight.com", "edi.blr@pasfreight.com"]);
    }

    function showCargo() {
        addMessage("CARGO", true);
        const container = document.getElementById('messagesContainer');
        const div = document.createElement('div');
        div.className = 'message bot';
        div.innerHTML = `<div class="message-avatar">🤖</div>
                        <div class="message-content">🚚 CARGO - Select Type:<br>
                        <div class="service-buttons">
                            <button class="service-btn" onclick="showDomesticCargo()">🇮🇳 DOMESTIC</button>
                            <button class="service-btn" onclick="showInternationalCargo()">🌍 INTERNATIONAL</button>
                        </div></div>`;
        container.appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }

    function showDomesticCargo() {
        addMessage("DOMESTIC CARGO", true);
        addContactInfo("DOMESTIC CARGO", 
            ["+91 63615 26659"],
            ["kavan@pasfreight.com", "info@pasfreight.com"]);
    }

    function showInternationalCargo() {
        addMessage("INTERNATIONAL CARGO", true);
        addContactInfo("INTERNATIONAL CARGO", 
            ["+91 63615 26659"],
            ["kavan@pasfreight.com", "info@pasfreight.com"]);
    }

    function showContact() {
        addMessage("Contact Us", true);
        addContactInfo("PAS FREIGHT CONTACT", 
            ["+91 90361 01201"],
            ["shivu@pasfreight.com", "info@pasfreight.com"]);
    }

    function showAbout() {
        addMessage("About Us", true);
        const container = document.getElementById('messagesContainer');
        const div = document.createElement('div');
        div.className = 'message bot';
        div.innerHTML = `<div class="message-avatar">🤖</div>
                        <div class="message-content">🏢 <strong>PAS Freight Services Pvt Ltd</strong><br><br>
                        📍 Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092<br><br>
                        📞 +91 90361 01201<br>
                        ✉️ shivu@pasfreight.com<br><br>
                        ✅ WCA:115513 | GLA:1166251<br>
                        🌟 8+ years experience<br><br>
                        🎯 Bangalore's most trusted logistics partner</div>`;
        container.appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }

    function resetChat() {
        const container = document.getElementById('messagesContainer');
        container.innerHTML = '';
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'message bot';
        welcomeDiv.innerHTML = `<div class="message-avatar">🤖</div>
                                <div class="message-content">Hi, I'm PAS Freight AI Assistant. I can help with import/export, customs clearance, and cargo services. Ask me anything about logistics!</div>`;
        container.appendChild(welcomeDiv);
    }

    async function sendMessage() {
        const input = document.getElementById('userInput');
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        addMessage(text, true);
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot';
        typingDiv.id = 'typing';
        typingDiv.innerHTML = `<div class="message-avatar">🤖</div><div class="message-content"><div class="typing-indicator"><span></span><span></span><span></span></div></div>`;
        document.getElementById('messagesContainer').appendChild(typingDiv);
        typingDiv.scrollIntoView({ behavior: 'smooth' });
        
        const res = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: text})
        });
        const data = await res.json();
        
        const typing = document.getElementById('typing');
        if (typing) typing.remove();
        
        addMessage(data.reply, false);
        
        if (isVoiceMode && 'speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(data.reply);
            utterance.lang = 'en-IN';
            utterance.rate = 0.9;
            window.speechSynthesis.speak(utterance);
            isVoiceMode = false;
        }
    }

    document.getElementById('sendBtn').onclick = () => { isVoiceMode = false; sendMessage(); };
    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            isVoiceMode = false;
            sendMessage();
        }
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
    
    system_prompt = """You are PAS Freight AI Assistant. Be professional, crisp, and helpful.

RESPONSE RULES:
- Keep responses short and professional (1-2 sentences)
- Don't use excessive emojis
- Redirect off-topic questions to logistics services
- Always provide helpful, actionable information

Company Info:
PAS Freight Services - Logistics provider in Bangalore
Services: Import/Export (Air/Sea), Customs Clearance, Cargo
Contact: +91 90361 01201
Email: shivu@pasfreight.com

Be professional, direct, and helpful."""

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
        return jsonify({'reply': "For assistance with PAS Freight services, call +91 90361 01201 or email shivu@pasfreight.com"})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PAS Freight AI - Premium UI")
    print("📱 Open: http://localhost:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
