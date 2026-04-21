import openai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #343541;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            width: 100%;
            max-width: 800px;
            height: 100vh;
            background: #343541;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #202123;
            color: #ececec;
            padding: 12px 20px;
            text-align: center;
            border-bottom: 1px solid #4a4b53;
        }
        .header h1 { font-size: 16px; font-weight: 500; }
        .header p { font-size: 11px; opacity: 0.7; margin-top: 3px; }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .msg {
            margin-bottom: 20px;
            display: flex;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            flex-shrink: 0;
        }
        .bot-avatar { background: #10a37f; color: white; margin-right: 12px; }
        .user-avatar { background: #5436da; color: white; margin-left: 12px; order: 2; }
        .bubble {
            max-width: 80%;
            padding: 10px 16px;
            border-radius: 20px;
            font-size: 14px;
            line-height: 1.5;
        }
        .user .bubble { background: #5436da; color: white; border-bottom-right-radius: 4px; }
        .bot .bubble { background: #444654; color: #ececec; border-bottom-left-radius: 4px; }
        .service-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-top: 10px;
        }
        .service-btn {
            background: #40414f;
            border: 1px solid #565869;
            padding: 10px 16px;
            border-radius: 25px;
            font-size: 13px;
            cursor: pointer;
            color: #ececec;
            transition: all 0.2s;
        }
        .service-btn:hover { background: #565869; transform: scale(0.98); }
        .contact-info {
            background: #2a2a2a;
            padding: 12px;
            border-radius: 12px;
            margin-top: 10px;
            font-size: 12px;
        }
        .contact-info p { margin: 5px 0; }
        .input-container {
            padding: 16px 20px;
            background: #40414f;
            border-top: 1px solid #4a4b53;
        }
        .input-wrapper {
            display: flex;
            gap: 10px;
            align-items: center;
            background: #40414f;
            border: 1px solid #565869;
            border-radius: 28px;
            padding: 6px 8px 6px 18px;
        }
        .input-wrapper input {
            flex: 1;
            background: none;
            border: none;
            color: white;
            font-size: 14px;
            outline: none;
        }
        .input-wrapper input::placeholder { color: #8e8ea0; }
        .tool-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 20px;
            padding: 6px;
            border-radius: 50%;
            color: #8e8ea0;
            width: 36px;
            height: 36px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .tool-btn:hover { background: #565869; color: white; }
        .voice-active { background: #ef4444 !important; color: white !important; animation: pulse 1s infinite; }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
        .send-btn {
            background: #10a37f;
            color: white;
            border: none;
            border-radius: 50%;
            width: 36px;
            height: 36px;
            cursor: pointer;
            font-size: 18px;
        }
        .send-btn:hover { background: #1a7f64; }
        .quick-buttons {
            padding: 12px 20px;
            background: #343541;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            border-bottom: 1px solid #4a4b53;
        }
        .quick-btn {
            background: #40414f;
            border: 1px solid #565869;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            cursor: pointer;
            color: #ececec;
        }
        .quick-btn:hover { background: #565869; }
        .footer {
            text-align: center;
            padding: 8px;
            font-size: 10px;
            color: #565869;
            background: #343541;
        }
        .image-preview {
            max-width: 150px;
            max-height: 120px;
            border-radius: 12px;
            margin-top: 8px;
            cursor: pointer;
        }
        .typing {
            display: inline-flex;
            gap: 4px;
            padding: 4px 0;
        }
        .typing span {
            width: 6px;
            height: 6px;
            background: #8e8ea0;
            border-radius: 50%;
            animation: bounce 1.4s infinite;
        }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }
        .messages::-webkit-scrollbar { width: 6px; }
        .messages::-webkit-scrollbar-track { background: #40414f; }
        .messages::-webkit-scrollbar-thumb { background: #565869; border-radius: 3px; }
    </style>
</head>
<body>
<div class="chat-container">
    <div class="header">
        <h1>📦 PAS Freight Services Pvt Ltd</h1>
        <p>WCA & GLA Certified | 24/7 Support</p>
    </div>

    <div class="messages" id="messages">
        <div class="msg bot">
            <div class="avatar bot-avatar">🤖</div>
            <div class="bubble">✨ Namaste! I'm PAS Freight's AI assistant. I can help with import/export, customs clearance, and cargo services. How can I help you today?</div>
        </div>
    </div>

    <div class="quick-buttons">
        <button class="quick-btn" onclick="showMainMenu()">📦 Main Menu</button>
        <button class="quick-btn" onclick="showContact()">📞 Contact Us</button>
        <button class="quick-btn" onclick="showAbout()">🏢 About Us</button>
    </div>

    <div class="input-container">
        <div class="input-wrapper">
            <input type="text" id="userInput" placeholder="Ask me anything about logistics...">
            <button class="tool-btn" id="voiceBtn" title="Voice Input">🎤</button>
            <button class="tool-btn" id="cameraBtn" title="Upload Screenshot">📷</button>
            <button class="send-btn" id="sendBtn">➤</button>
            <input type="file" id="cameraInput" style="display:none" accept="image/*">
        </div>
    </div>
    <div class="footer">PAS Freight | 24/7 Support | +91 90361 01201</div>
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
            addMessage("🎤 Sorry, couldn't hear you. Please type your question.", false);
        };
        
        recognition.onend = function() {
            document.getElementById('voiceBtn').classList.remove('voice-active');
            isListening = false;
        };
    }
    
    document.getElementById('voiceBtn').onclick = function() {
        if (!recognition) {
            addMessage("🎤 Voice support requires Chrome browser.", false);
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
                div.className = 'msg user';
                div.innerHTML = `<div class="avatar user-avatar">👤</div>
                                <div class="bubble">📷 <strong>Screenshot uploaded</strong><br><img src="${event.target.result}" class="image-preview" onclick="window.open(this.src)"></div>`;
                document.getElementById('messages').appendChild(div);
                div.scrollIntoView({ behavior: 'smooth' });
                
                setTimeout(() => {
                    addMessage("✅ Thanks for sharing! Our team will review it. For immediate help, call +91 90361 01201", false);
                }, 500);
            };
            reader.readAsDataURL(file);
        }
        this.value = '';
    };

    function addMessage(text, isUser) {
        const div = document.createElement('div');
        div.className = 'msg ' + (isUser ? 'user' : 'bot');
        div.innerHTML = `<div class="avatar ${isUser ? 'user-avatar' : 'bot-avatar'}">${isUser ? '👤' : '🤖'}</div>
                        <div class="bubble">${text}</div>`;
        document.getElementById('messages').appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }

    function addContactInfo(title, numbers, emails) {
        let html = `<div class="contact-info"><strong>${title}</strong><br>`;
        if (numbers && numbers.length) {
            html += `📞 <strong>Phone:</strong><br>`;
            numbers.forEach(num => { html += `   ${num}<br>`; });
        }
        if (emails && emails.length) {
            html += `✉️ <strong>Email:</strong><br>`;
            emails.forEach(email => { html += `   ${email}<br>`; });
        }
        html += `</div>`;
        
        const div = document.createElement('div');
        div.className = 'msg bot';
        div.innerHTML = `<div class="avatar bot-avatar">🤖</div><div class="bubble">${html}</div>`;
        document.getElementById('messages').appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }

    function showMainMenu() {
        addMessage("Main Menu", true);
        const div = document.createElement('div');
        div.className = 'msg bot';
        div.innerHTML = `<div class="avatar bot-avatar">🤖</div>
                        <div class="bubble">📦 <strong>Select a service:</strong><br>
                        <div class="service-buttons">
                            <button class="service-btn" onclick="showImportOptions()">📥 IMPORT</button>
                            <button class="service-btn" onclick="showExportOptions()">📤 EXPORT</button>
                            <button class="service-btn" onclick="showCustoms()">📋 CUSTOMS CLEARANCE</button>
                            <button class="service-btn" onclick="showCargo()">🚚 CARGO</button>
                        </div></div>`;
        document.getElementById('messages').appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }

    function showImportOptions() {
        addMessage("IMPORT", true);
        const div = document.createElement('div');
        div.className = 'msg bot';
        div.innerHTML = `<div class="avatar bot-avatar">🤖</div>
                        <div class="bubble">📥 <strong>IMPORT - Select Mode:</strong><br>
                        <div class="service-buttons">
                            <button class="service-btn" onclick="showImportAir()">✈️ AIR</button>
                            <button class="service-btn" onclick="showImportSea()">🚢 SEA</button>
                        </div></div>`;
        document.getElementById('messages').appendChild(div);
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
        const div = document.createElement('div');
        div.className = 'msg bot';
        div.innerHTML = `<div class="avatar bot-avatar">🤖</div>
                        <div class="bubble">📤 <strong>EXPORT - Select Mode:</strong><br>
                        <div class="service-buttons">
                            <button class="service-btn" onclick="showExportAir()">✈️ AIR</button>
                            <button class="service-btn" onclick="showExportSea()">🚢 SEA</button>
                        </div></div>`;
        document.getElementById('messages').appendChild(div);
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
        const div = document.createElement('div');
        div.className = 'msg bot';
        div.innerHTML = `<div class="avatar bot-avatar">🤖</div>
                        <div class="bubble">🚚 <strong>CARGO - Select Type:</strong><br>
                        <div class="service-buttons">
                            <button class="service-btn" onclick="showDomesticCargo()">🇮🇳 DOMESTIC</button>
                            <button class="service-btn" onclick="showInternationalCargo()">🌍 INTERNATIONAL</button>
                        </div></div>`;
        document.getElementById('messages').appendChild(div);
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
        const div = document.createElement('div');
        div.className = 'msg bot';
        div.innerHTML = `<div class="avatar bot-avatar">🤖</div>
                        <div class="bubble">🏢 <strong>PAS Freight Services Pvt Ltd</strong><br><br>
                        📍 <strong>Address:</strong> Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092<br><br>
                        📞 <strong>Contact:</strong> +91 90361 01201<br><br>
                        ✉️ <strong>Email:</strong> shivu@pasfreight.com<br><br>
                        ✅ <strong>Certifications:</strong> WCA (115513), GLA (1166251)<br><br>
                        🌟 <strong>Experience:</strong> Over 8 years in logistics<br><br>
                        💼 <strong>Services:</strong> Import, Export, Customs, Cargo, Air & Sea Freight<br><br>
                        🎯 <strong>Vision:</strong> To be Bangalore's most trusted logistics partner</div>`;
        document.getElementById('messages').appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }

    async function sendMessage() {
        const input = document.getElementById('userInput');
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        addMessage(text, true);
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'msg bot';
        typingDiv.id = 'typing';
        typingDiv.innerHTML = `<div class="avatar bot-avatar">🤖</div><div class="typing"><span></span><span></span><span></span></div>`;
        document.getElementById('messages').appendChild(typingDiv);
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
    
    system_prompt = """You are PAS Freight's friendly AI assistant. Be conversational, warm, and helpful.

IMPORTANT RULES:
1. For greetings like "hi", "hello", "hey" -> Respond warmly and offer help
2. For logistics questions -> Give specific PAS Freight information
3. For non-logistics questions -> Politely redirect to PAS Freight services
4. Keep responses conversational and use emojis occasionally
5. Always be helpful and solution-oriented

Company Info:
PAS Freight Services Pvt Ltd - Bangalore's leading logistics provider
Services: Import/Export (Air/Sea), Customs Clearance, Domestic/International Cargo
Contact: +91 90361 01201
Email: shivu@pasfreight.com, info@pasfreight.com
Certifications: WCA (115513), GLA (1166251)

Examples:
User: "hi" -> "Hey there! Welcome to PAS Freight. How can I help you with your logistics needs today?"
User: "What services?" -> "We offer comprehensive logistics services! Import/Export by Air & Sea, Customs Clearance, and Domestic & International Cargo."
User: "rates" -> "For exact rates, please call us at +91 90361 01201. Our team will provide you the best quote!"

Be conversational, helpful, and friendly!"""

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=200,
            temperature=0.8
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': "Hey there! Thanks for reaching out to PAS Freight. For immediate assistance, please call us at +91 90361 01201 or email shivu@pasfreight.com. Our team is available 24/7!"})

if __name__ == '__main__':
    print("=" * 60)
    print("PAS Freight FINAL AI Assistant")
    print("Open: http://localhost:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
