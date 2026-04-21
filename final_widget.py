import openai
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

WIDGET_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: white;
            width: 380px;
            height: 600px;
            overflow: hidden;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        .chat-widget {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #ffffff;
        }
        
        .widget-header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 14px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }
        
        .header-info {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .avatar {
            width: 32px;
            height: 32px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
        }
        
        .header-text h3 {
            font-size: 13px;
            font-weight: 600;
        }
        
        .header-text p {
            font-size: 9px;
            opacity: 0.8;
        }
        
        .close-btn {
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
        
        .close-btn:hover {
            background: rgba(255,255,255,0.2);
        }
        
        .messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 12px;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 12px;
            display: flex;
        }
        
        .user-message {
            justify-content: flex-end;
        }
        
        .bot-message {
            justify-content: flex-start;
        }
        
        .bubble {
            max-width: 85%;
            padding: 8px 12px;
            border-radius: 16px;
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
        
        .service-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 8px;
        }
        
        .service-btn {
            background: #f0f2f5;
            border: none;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .service-btn:hover {
            background: #2a5298;
            color: white;
        }
        
        .contact-info {
            background: #f0f2f5;
            padding: 10px;
            border-radius: 12px;
            margin-top: 8px;
            font-size: 11px;
        }
        
        .contact-info strong {
            color: #1e3c72;
        }
        
        .input-area {
            padding: 12px;
            background: white;
            border-top: 1px solid #e5e5e5;
            display: flex;
            gap: 8px;
            flex-shrink: 0;
        }
        
        .input-area input {
            flex: 1;
            padding: 12px 14px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        
        .input-area input:focus {
            border-color: #2a5298;
        }
        
        .input-area button {
            background: #2a5298;
            color: white;
            border: none;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .typing {
            display: inline-flex;
            gap: 4px;
            padding: 4px 0;
        }
        
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
        
        .messages-area::-webkit-scrollbar {
            width: 4px;
        }
        
        .sub-buttons {
            display: flex;
            gap: 8px;
            margin-top: 8px;
            flex-wrap: wrap;
        }
        
        .sub-btn {
            background: #e9ecef;
            border: none;
            padding: 6px 12px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 11px;
        }
        
        .sub-btn:hover {
            background: #2a5298;
            color: white;
        }
        
        .main-buttons {
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }
        
        .main-btn {
            flex: 1;
            background: #1e3c72;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 12px;
            font-weight: 500;
        }
        
        .main-btn:hover {
            background: #2a5298;
        }
    </style>
</head>
<body>
<div class="chat-widget">
    <div class="widget-header">
        <div class="header-info">
            <div class="avatar">📦</div>
            <div class="header-text">
                <h3>PAS Freight Services Pvt Ltd</h3>
                <p>Online 24/7 | Logistics Support</p>
            </div>
        </div>
        <button class="close-btn" id="closeWidgetBtn">✕</button>
    </div>
    
    <div class="messages-area" id="messagesArea">
        <div class="message bot-message">
            <div class="bubble">👋 Namaste! Welcome to PAS Freight.<br><br>How can I help you today?</div>
        </div>
        <div class="message bot-message">
            <div class="bubble">
                <div class="main-buttons">
                    <button class="main-btn" onclick="showMainMenuOptions()">📦 Main Menu</button>
                    <button class="main-btn" onclick="showContact()">📞 Contact Us</button>
                    <button class="main-btn" onclick="showAbout()">🏢 About Us</button>
                </div>
            </div>
        </div>
    </div>
    
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Type your message..." autocomplete="off">
        <button id="sendBtn">➤</button>
    </div>
</div>

<script>
    let step = null;
    let currentService = '';
    let userName = '';
    let userEmail = '';
    let userPhone = '';
    
    function addMessage(text, isUser) {
        const div = document.createElement('div');
        div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        div.innerHTML = `<div class="bubble">${text}</div>`;
        document.getElementById('messagesArea').appendChild(div);
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
        step = 'name';
        addMessage("📝 Please share your name for follow-up:", false);
    }
    
    function showMainMenuOptions() {
        addMessage("Main Menu", true);
        const div = document.createElement('div');
        div.className = 'message bot-message';
        div.innerHTML = `<div class="bubble">📦 <strong>Select a service:</strong><br>
            <div class="service-buttons">
                <button class="service-btn" onclick="showImportOptions()">📥 IMPORT</button>
                <button class="service-btn" onclick="showExportOptions()">📤 EXPORT</button>
                <button class="service-btn" onclick="showCustoms()">📋 CUSTOMS</button>
                <button class="service-btn" onclick="showCargo()">🚚 CARGO</button>
            </div>
        </div>`;
        document.getElementById('messagesArea').appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }
    
    function showContact() {
        addMessage("Contact Us", true);
        addContactInfo("PAS FREIGHT CONTACT", 
            ["+91 90361 01201"],
            ["shivu@pasfreight.com", "info@pasfreight.com"]);
    }
    
    function showAbout() {
        addMessage("About Us", true);
        const aboutText = `🏢 <strong>PAS Freight Services Pvt Ltd</strong><br><br>
        📍 Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092<br><br>
        📞 +91 90361 01201<br>
        ✉️ shivu@pasfreight.com<br><br>
        ✅ WCA:115513 | GLA:1166251<br>
        🌟 8+ years experience<br><br>
        🎯 Bangalore's most trusted logistics partner`;
        addMessage(aboutText, false);
    }
    
    function showImportOptions() {
        addMessage("IMPORT", true);
        const div = document.createElement('div');
        div.className = 'message bot-message';
        div.innerHTML = `<div class="bubble">📥 <strong>IMPORT - Select Mode:</strong><br>
            <div class="sub-buttons">
                <button class="sub-btn" onclick="showImportAir()">✈️ AIR</button>
                <button class="sub-btn" onclick="showImportSea()">🚢 SEA</button>
            </div>
        </div>`;
        document.getElementById('messagesArea').appendChild(div);
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
        div.className = 'message bot-message';
        div.innerHTML = `<div class="bubble">📤 <strong>EXPORT - Select Mode:</strong><br>
            <div class="sub-buttons">
                <button class="sub-btn" onclick="showExportAir()">✈️ AIR</button>
                <button class="sub-btn" onclick="showExportSea()">🚢 SEA</button>
            </div>
        </div>`;
        document.getElementById('messagesArea').appendChild(div);
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
        div.className = 'message bot-message';
        div.innerHTML = `<div class="bubble">🚚 <strong>CARGO - Select Type:</strong><br>
            <div class="sub-buttons">
                <button class="sub-btn" onclick="showDomesticCargo()">🇮🇳 DOMESTIC</button>
                <button class="sub-btn" onclick="showInternationalCargo()">🌍 INTERNATIONAL</button>
            </div>
        </div>`;
        document.getElementById('messagesArea').appendChild(div);
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
    
    function showTyping() {
        const div = document.createElement('div');
        div.className = 'message bot-message';
        div.id = 'typing';
        div.innerHTML = '<div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
        document.getElementById('messagesArea').appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }
    
    function hideTyping() {
        const typing = document.getElementById('typing');
        if (typing) typing.remove();
    }
    
    async function sendMessage() {
        const input = document.getElementById('userInput');
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        
        if (step === 'name') {
            userName = text;
            step = 'email';
            addMessage(text, true);
            addMessage("📧 Your email address?", false);
            return;
        }
        
        if (step === 'email') {
            userEmail = text;
            step = 'phone';
            addMessage(text, true);
            addMessage("📞 Your phone number? (type 'skip' to skip)", false);
            return;
        }
        
        if (step === 'phone') {
            if (text !== 'skip') userPhone = text;
            addMessage(text, true);
            
            await fetch('/save_lead', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: userName, email: userEmail, phone: userPhone })
            });
            
            addMessage(`✅ Thank you ${userName}! Our team will contact you within 24 hours.`, false);
            addMessage("📞 For immediate help, call +91 90361 01201", false);
            
            step = null;
            userName = userEmail = userPhone = '';
            return;
        }
        
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
            addMessage('📞 Please call +91 90361 01201 for assistance.', false);
        }
    }
    
    document.getElementById('closeWidgetBtn').addEventListener('click', function() {
        if (window.parent && window.parent.closeWidget) {
            window.parent.closeWidget();
        }
    });
    
    document.getElementById('sendBtn').addEventListener('click', sendMessage);
    document.getElementById('userInput').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
    
    // Make functions global
    window.showMainMenuOptions = showMainMenuOptions;
    window.showContact = showContact;
    window.showAbout = showAbout;
    window.showImportOptions = showImportOptions;
    window.showImportAir = showImportAir;
    window.showImportSea = showImportSea;
    window.showExportOptions = showExportOptions;
    window.showExportAir = showExportAir;
    window.showExportSea = showExportSea;
    window.showCustoms = showCustoms;
    window.showCargo = showCargo;
    window.showDomesticCargo = showDomesticCargo;
    window.showInternationalCargo = showInternationalCargo;
</script>
</body>
</html>
'''

# Embed code with correct BOTTOM-RIGHT positioning
EMBED_CODE = '''
<!-- PAS Freight Chat Widget - Bottom Right Corner -->
<div id="pasfreight-chat-widget" style="position: fixed; bottom: 20px; right: 20px; z-index: 999999;">
    <style>
        #pasfreight-chat-btn {
            width: 55px;
            height: 55px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            border: none;
            position: relative;
        }
        
        #pasfreight-chat-btn:hover {
            transform: scale(1.05);
        }
        
        .chat-icon {
            font-size: 26px;
            color: white;
        }
        
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
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        #pasfreight-chat-frame {
            position: fixed;
            bottom: 85px;
            right: 20px;
            width: 380px;
            height: 600px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: none;
            z-index: 999998;
            border: none;
            overflow: hidden;
        }
        
        @media (max-width: 500px) {
            #pasfreight-chat-frame {
                width: 100%;
                height: 100%;
                bottom: 0;
                right: 0;
                border-radius: 0;
            }
        }
    </style>
    <button id="pasfreight-chat-btn">
        <span class="chat-icon">💬</span>
        <span class="notification-badge" id="notificationBadge" style="display: none;">1</span>
    </button>
    <iframe id="pasfreight-chat-frame" src="CHAT_URL" title="PAS Freight Chat"></iframe>
</div>

<script>
    (function() {
        var btn = document.getElementById('pasfreight-chat-btn');
        var frame = document.getElementById('pasfreight-chat-frame');
        var badge = document.getElementById('notificationBadge');
        var isOpen = false;
        var notified = false;
        
        window.closeWidget = function() {
            frame.style.display = 'none';
            isOpen = false;
        };
        
        btn.addEventListener('click', function() {
            if (isOpen) {
                frame.style.display = 'none';
                isOpen = false;
            } else {
                frame.style.display = 'block';
                isOpen = true;
                badge.style.display = 'none';
                notified = true;
            }
        });
        
        setTimeout(function() {
            if (!isOpen && !notified) {
                badge.style.display = 'flex';
            }
        }, 30000);
    })();
</script>
'''

@app.route('/')
def index():
    return render_template_string(WIDGET_HTML)

@app.route('/widget.js')
def widget_js():
    import socket
    host = request.host
    scheme = request.scheme
    chat_url = f'{scheme}://{host}'
    embed = EMBED_CODE.replace('CHAT_URL', chat_url)
    return embed, 200, {'Content-Type': 'application/javascript'}

@app.route('/save_lead', methods=['POST'])
def save_lead():
    data = request.get_json()
    with open('leads.txt', 'a') as f:
        import json
        f.write(json.dumps(data) + '\n')
    print(f"Lead: {data.get('name')} - {data.get('email')}")
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    
    system_prompt = """You are PAS Freight AI Assistant. Give short, helpful answers.

Company: PAS Freight Services Pvt Ltd, Bangalore
Services: Import/Export (Air/Sea), Customs Clearance, Domestics, Courier
Contact: +91 90361 01201
Email: shivu@pasfreight.com

Keep answers to 1-2 sentences. Be helpful and professional."""

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
    except:
        return jsonify({'reply': '📞 For assistance, call +91 90361 01201 or email shivu@pasfreight.com'})

if __name__ == '__main__':
    import socket
    hostname = socket.gethostbyname(socket.gethostname())
    print("=" * 60)
    print("🚀 PAS Freight Chat Widget - BOTTOM RIGHT CORNER")
    print(f"📱 Widget URL: http://localhost:5001")
    print(f"📱 Network URL: http://{hostname}:5001")
    print("\n📋 ADD THIS CODE TO YOUR WEBSITE (before closing </body> tag):")
    print(f'<script src="http://{hostname}:5001/widget.js"></script>')
    print("=" * 60)
    print("\n💡 The widget will appear as a floating button at BOTTOM-RIGHT corner of your website!")
    app.run(host='0.0.0.0', port=5001, debug=False)
