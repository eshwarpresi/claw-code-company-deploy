import openai
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

user_sessions = {}

def calculate_price(weight_kg, mode, cargo_type=""):
    if mode == "air":
        rate_per_kg = 300
        days = "3-7 days"
    else:
        rate_per_kg = 80
        days = "20-35 days"
    total = weight_kg * rate_per_kg
    return total, rate_per_kg, days

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Aisea - PAS Freight AI</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; }
        #chat-btn {
            position: fixed; bottom: 20px; right: 20px; width: 55px; height: 55px;
            background: #1e3c72; border-radius: 50%; cursor: pointer;
            display: flex; align-items: center; justify-content: center;
            border: none; z-index: 999999; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        #chat-btn:hover { transform: scale(1.05); }
        .chat-icon { font-size: 28px; color: white; }
        #chat-window {
            position: fixed; bottom: 85px; right: 20px; width: 380px; height: 550px;
            background: white; border-radius: 16px; box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            display: none; z-index: 999998; overflow: hidden; flex-direction: column;
        }
        .chat-header {
            background: #1e3c72; color: white; padding: 15px;
            display: flex; align-items: center; justify-content: space-between;
        }
        .avatar { width: 35px; height: 35px; background: rgba(255,255,255,0.2); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; }
        .header-text h3 { font-size: 14px; }
        .header-text p { font-size: 10px; opacity: 0.8; }
        .close-btn { background: none; border: none; color: white; font-size: 18px; cursor: pointer; }
        .messages-area { flex: 1; overflow-y: auto; padding: 15px; background: #f5f7fb; }
        .message { margin-bottom: 12px; display: flex; }
        .user-msg { justify-content: flex-end; }
        .bot-msg { justify-content: flex-start; }
        .bubble { max-width: 80%; padding: 8px 12px; border-radius: 18px; font-size: 12px; }
        .user-msg .bubble { background: #1e3c72; color: white; }
        .bot-msg .bubble { background: white; color: #333; border: 1px solid #ddd; }
        .main-buttons { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
        .main-btn { background: #e9ecef; border: none; padding: 6px 10px; border-radius: 15px; cursor: pointer; font-size: 10px; }
        .main-btn:hover { background: #1e3c72; color: white; }
        .sub-buttons { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 8px; }
        .sub-btn { background: #e9ecef; border: none; padding: 5px 10px; border-radius: 12px; cursor: pointer; font-size: 10px; }
        .sub-btn:hover { background: #1e3c72; color: white; }
        .input-area { padding: 12px; background: white; border-top: 1px solid #ddd; display: flex; gap: 8px; }
        .input-area input { flex: 1; padding: 8px 12px; border: 1px solid #ddd; border-radius: 20px; font-size: 12px; outline: none; }
        .input-area button { background: #1e3c72; color: white; border: none; width: 35px; height: 35px; border-radius: 50%; cursor: pointer; }
        .typing { display: inline-flex; gap: 4px; padding: 4px 0; }
        .typing span { width: 5px; height: 5px; background: #999; border-radius: 50%; animation: bounce 1.4s infinite; }
        @keyframes bounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-5px); } }
    </style>
</head>
<body>
    <button id="chat-btn"><span class="chat-icon">??</span></button>
    <div id="chat-window">
        <div class="chat-header">
            <div class="avatar">??</div>
            <div class="header-text"><h3>Aisea</h3><p>PAS Freight AI</p></div>
            <button class="close-btn" id="closeBtn">X</button>
        </div>
        <div class="messages-area" id="messagesArea">
            <div class="message bot-msg">
                <div class="bubble">Hi, I'm Aisea. Need a shipping quote? Share weight, destination.</div>
            </div>
            <div class="message bot-msg">
                <div class="bubble">
                    <div class="main-buttons">
                        <button class="main-btn" onclick="showImport()">IMPORT</button>
                        <button class="main-btn" onclick="showExport()">EXPORT</button>
                        <button class="main-btn" onclick="showCustoms()">CUSTOMS</button>
                        <button class="main-btn" onclick="showCargo()">CARGO</button>
                        <button class="main-btn" onclick="showContact()">CONTACT</button>
                        <button class="main-btn" onclick="showAbout()">ABOUT</button>
                    </div>
                </div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Ask me...">
            <button id="sendBtn">Send</button>
        </div>
    </div>
    <script>
        var chatBtn = document.getElementById('chat-btn');
        var chatWindow = document.getElementById('chat-window');
        var closeBtn = document.getElementById('closeBtn');
        var messagesArea = document.getElementById('messagesArea');
        var userInput = document.getElementById('userInput');
        var sendBtn = document.getElementById('sendBtn');
        var sessionId = 'session_' + Date.now();
        var isOpen = false;
        
        chatBtn.onclick = function() {
            if (isOpen) {
                chatWindow.style.display = 'none';
                isOpen = false;
            } else {
                chatWindow.style.display = 'flex';
                isOpen = true;
            }
        };
        
        closeBtn.onclick = function() {
            chatWindow.style.display = 'none';
            isOpen = false;
        };
        
        function addMessage(text, isUser) {
            var div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user-msg' : 'bot-msg');
            div.innerHTML = '<div class="bubble">' + text + '</div>';
            messagesArea.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        }
        
        function addContactInfo(title, numbers, emails) {
            var html = '<div style="background:#f0f2f5;padding:8px;border-radius:8px;margin-top:5px;"><strong>' + title + '</strong><br>';
            if (numbers) {
                for (var i = 0; i < numbers.length; i++) {
                    html += 'Phone: ' + numbers[i] + '<br>';
                }
            }
            if (emails) {
                for (var i = 0; i < emails.length; i++) {
                    html += 'Email: ' + emails[i] + '<br>';
                }
            }
            html += '</div>';
            addMessage(html, false);
        }
        
        function showTyping() {
            var div = document.createElement('div');
            div.className = 'message bot-msg';
            div.id = 'typing';
            div.innerHTML = '<div class="bubble">Typing...</div>';
            messagesArea.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        }
        
        function hideTyping() {
            var typing = document.getElementById('typing');
            if (typing) typing.remove();
        }
        
        window.showImport = function() {
            addMessage("IMPORT", true);
            var div = document.createElement('div');
            div.className = 'message bot-msg';
            div.innerHTML = '<div class="bubble">Select Mode:<br><button class="sub-btn" onclick="showImportAir()">AIR</button> <button class="sub-btn" onclick="showImportSea()">SEA</button></div>';
            messagesArea.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        };
        
        window.showImportAir = function() {
            addMessage("IMPORT - AIR", true);
            addContactInfo("IMPORT AIR FREIGHT", ["+91 99869 42772", "+91 63615 21413"], ["gj@pasfreight.com", "rachana@pasfreight.com"]);
        };
        
        window.showImportSea = function() {
            addMessage("IMPORT - SEA", true);
            addContactInfo("IMPORT SEA FREIGHT", ["+91 93648 81371", "+91 63615 21413"], ["vinodh@pasfreight.com", "gj@pasfreight.com"]);
        };
        
        window.showExport = function() {
            addMessage("EXPORT", true);
            var div = document.createElement('div');
            div.className = 'message bot-msg';
            div.innerHTML = '<div class="bubble">Select Mode:<br><button class="sub-btn" onclick="showExportAir()">AIR</button> <button class="sub-btn" onclick="showExportSea()">SEA</button></div>';
            messagesArea.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        };
        
        window.showExportAir = function() {
            addMessage("EXPORT - AIR", true);
            addContactInfo("EXPORT AIR FREIGHT", ["+91 93648 81371", "+91 63615 26659"], ["vinodh@pasfreight.com", "kavan@pasfreight.com"]);
        };
        
        window.showExportSea = function() {
            addMessage("EXPORT - SEA", true);
            addContactInfo("EXPORT SEA FREIGHT", ["+91 93648 81371", "+91 63615 26659"], ["vinodh@pasfreight.com", "kavan@pasfreight.com"]);
        };
        
        window.showCustoms = function() {
            addMessage("CUSTOMS", true);
            addContactInfo("CUSTOMS CLEARANCE", ["+91 63615 26664"], ["ajith@pasfreight.com", "edi.blr@pasfreight.com"]);
        };
        
        window.showCargo = function() {
            addMessage("CARGO", true);
            var div = document.createElement('div');
            div.className = 'message bot-msg';
            div.innerHTML = '<div class="bubble">Select Type:<br><button class="sub-btn" onclick="showDomesticCargo()">DOMESTIC</button> <button class="sub-btn" onclick="showInternationalCargo()">INTERNATIONAL</button></div>';
            messagesArea.appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
        };
        
        window.showDomesticCargo = function() {
            addMessage("DOMESTIC CARGO", true);
            addContactInfo("DOMESTIC CARGO", ["+91 63615 26659"], ["kavan@pasfreight.com", "info@pasfreight.com"]);
        };
        
        window.showInternationalCargo = function() {
            addMessage("INTERNATIONAL CARGO", true);
            addContactInfo("INTERNATIONAL CARGO", ["+91 63615 26659"], ["kavan@pasfreight.com", "info@pasfreight.com"]);
        };
        
        window.showContact = function() {
            addMessage("CONTACT", true);
            addContactInfo("PAS FREIGHT", ["+91 90361 01201"], ["shivu@pasfreight.com", "info@pasfreight.com"]);
        };
        
        window.showAbout = function() {
            addMessage("ABOUT", true);
            addMessage("PAS Freight Services Pvt Ltd - Bangalore. 8+ years experience. WCA & GLA Certified.", false);
        };
        
        async function sendMessage() {
            var text = userInput.value.trim();
            if (!text) return;
            userInput.value = '';
            addMessage(text, true);
            showTyping();
            try {
                var response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text, session_id: sessionId })
                });
                var data = await response.json();
                hideTyping();
                addMessage(data.reply, false);
            } catch(error) {
                hideTyping();
                addMessage('Call +91 90361 01201 for assistance.', false);
            }
        }
        
        sendBtn.onclick = sendMessage;
        userInput.onkeypress = function(e) {
            if (e.key === 'Enter') sendMessage();
        };
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
    user_msg = data.get('message', '').lower()
    session_id = data.get('session_id', 'default')
    
    if session_id not in user_sessions:
        user_sessions[session_id] = {'weight': None, 'destination': None, 'phone': None}
    
    session_data = user_sessions[session_id]
    
    weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilogram)', user_msg)
    if weight_match:
        session_data['weight'] = float(weight_match.group(1))
    
    destinations = ['germany', 'usa', 'uk', 'dubai', 'singapore', 'china']
    for dest in destinations:
        if dest in user_msg:
            session_data['destination'] = dest
            break
    
    phone_match = re.search(r'\d{10}', user_msg)
    if phone_match:
        session_data['phone'] = phone_match.group(0)
    
    if 'get exact quote' in user_msg or 'give me quote' in user_msg:
        if session_data['weight'] and session_data['destination']:
            weight = session_data['weight']
            dest = session_data['destination'].title()
            air_total, air_rate, air_days = calculate_price(weight, "air")
            sea_total, sea_rate, sea_days = calculate_price(weight, "sea")
            reply = f"Got it - {int(weight)} kg to {dest}.\n\nAir: Rs.{air_rate}/kg -> Rs.{int(air_total):,} ({air_days})\nSea: Rs.{sea_rate}/kg -> Rs.{int(sea_total):,} ({sea_days})\n\nShare your number - team will call you within 10 minutes."
            return jsonify({'reply': reply})
        else:
            return jsonify({'reply': 'Please share weight and destination first.'})
    
    if 'compare air vs sea' in user_msg:
        if session_data['weight'] and session_data['destination']:
            weight = session_data['weight']
            dest = session_data['destination'].title()
            air_total, air_rate, air_days = calculate_price(weight, "air")
            sea_total, sea_rate, sea_days = calculate_price(weight, "sea")
            reply = f"For {int(weight)} kg to {dest}:\n\nAir: Rs.{int(air_total):,} | {air_days}\nSea: Rs.{int(sea_total):,} | {sea_days}\n\nAir is faster, Sea is cheaper."
            return jsonify({'reply': reply})
        else:
            return jsonify({'reply': 'Share weight and destination first.'})
    
    if 'talk to expert' in user_msg:
        if session_data.get('phone'):
            reply = f"Great! Team will call you at {session_data['phone']} within 10 minutes."
        else:
            reply = "Share your number - team will call you within 10 minutes with best rates."
        return jsonify({'reply': reply})
    
    system_prompt = """You are Aisea, PAS Freight AI. Be short and professional. Ask for weight and destination. Contact: +91 90361 01201"""
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}],
            max_tokens=100,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except:
        return jsonify({'reply': 'Call +91 90361 01201 for assistance.'})

if __name__ == '__main__':
    print("=" * 50)
    print("Aisea Assistant Running")
    print("Open: http://localhost:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)