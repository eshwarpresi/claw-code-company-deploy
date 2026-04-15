import openai
from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .chat-container {
            max-width: 450px;
            width: 100%;
            height: 90vh;
            background: white;
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        .header {
            background: #1e3c72;
            color: white;
            padding: 15px;
            text-align: center;
        }
        .header h1 { font-size: 18px; }
        .header p { font-size: 11px; opacity: 0.8; margin-top: 3px; }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #f0f2f5;
        }
        .msg {
            margin-bottom: 12px;
            display: flex;
        }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            max-width: 75%;
            padding: 10px 14px;
            border-radius: 18px;
            font-size: 13px;
            line-height: 1.4;
        }
        .user .bubble { background: #2a5298; color: white; }
        .bot .bubble { background: white; color: #333; border: 1px solid #ddd; }
        .buttons {
            padding: 12px;
            background: white;
            border-top: 1px solid #ddd;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .btn {
            flex: 1;
            min-width: 80px;
            padding: 10px;
            background: #1e3c72;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
        }
        .btn:active { transform: scale(0.97); }
        .input-area {
            padding: 12px;
            background: white;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 8px;
        }
        .input-area input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 13px;
            outline: none;
        }
        .input-area button {
            padding: 10px 18px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
        }
        .sub-btns {
            display: flex;
            gap: 8px;
            margin-top: 8px;
            flex-wrap: wrap;
        }
        .sub-btn {
            padding: 6px 12px;
            background: #4a6a8a;
            color: white;
            border: none;
            border-radius: 15px;
            cursor: pointer;
            font-size: 11px;
        }
        .typing {
            background: white;
            padding: 10px 14px;
            border-radius: 18px;
            display: inline-flex;
            gap: 4px;
        }
        .typing span {
            width: 6px;
            height: 6px;
            background: #999;
            border-radius: 50%;
            animation: blink 1.4s infinite;
        }
        @keyframes blink {
            0%, 60%, 100% { opacity: 0.3; }
            30% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <h1>📦 PAS Freight Services</h1>
            <p>Online 24/7 | Logistics Support</p>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="bubble">Welcome! Click a service below or type your question.</div>
            </div>
        </div>
        <div class="buttons" id="buttons">
            <button class="btn" onclick="selectService('import')">📦 Import</button>
            <button class="btn" onclick="selectService('export')">🚢 Export</button>
            <button class="btn" onclick="selectService('customs')">📋 Customs</button>
            <button class="btn" onclick="selectService('domestic')">🚚 Domestic</button>
            <button class="btn" onclick="selectService('courier')">📮 Courier</button>
            <button class="btn" onclick="showAbout()">🏢 About</button>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type your question...">
            <button onclick="sendChat()">Send</button>
        </div>
    </div>

    <script>
        let step = null;
        let service = '';
        let userName = '';
        let userEmail = '';
        let userPhone = '';
        
        const messagesDiv = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            div.innerHTML = '<div class="bubble">' + text + '</div>';
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function showTyping() {
            const div = document.createElement('div');
            div.className = 'msg bot';
            div.id = 'typing';
            div.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function hideTyping() {
            const t = document.getElementById('typing');
            if (t) t.remove();
        }
        
        function selectService(s) {
            service = s;
            const names = { import:'IMPORT', export:'EXPORT', customs:'CUSTOMS', domestic:'DOMESTICS', courier:'COURIERS' };
            addMessage(I need  service, true);
            
            let options = '';
            if (s === 'import' || s === 'export') {
                options = '<div class="sub-btns"><button class="sub-btn" onclick="selectMode(\\'air\\')">✈️ Air</button><button class="sub-btn" onclick="selectMode(\\'sea\\')">🚢 Sea</button></div>';
            } else if (s === 'domestic') {
                options = '<div class="sub-btns"><button class="sub-btn" onclick="selectMode(\\'full\\')">Full Truck</button><button class="sub-btn" onclick="selectMode(\\'less\\')">Less Truck</button></div>';
            } else if (s === 'courier') {
                options = '<div class="sub-btns"><button class="sub-btn" onclick="selectMode(\\'domestic\\')">Domestic</button><button class="sub-btn" onclick="selectMode(\\'international\\')">International</button></div>';
            } else if (s === 'customs') {
                options = '<div class="sub-btns"><button class="sub-btn" onclick="selectMode(\\'import\\')">Import Customs</button><button class="sub-btn" onclick="selectMode(\\'export\\')">Export Customs</button></div>';
            }
            
            const div = document.createElement('div');
            div.className = 'msg bot';
            div.innerHTML = '<div class="bubble">Select type:' + options + '</div>';
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function selectMode(mode) {
            addMessage(mode.toUpperCase(), true);
            step = 'name';
            addMessage('Please share your full name:', false);
        }
        
        async function showAbout() {
            addMessage('Tell me about company', true);
            const res = await fetch('/about');
            const data = await res.json();
            addMessage(data.info, false);
        }
        
        async function sendChat() {
            const text = userInput.value.trim();
            if (!text) return;
            userInput.value = '';
            addMessage(text, true);
            
            if (step === 'name') {
                userName = text;
                step = 'email';
                addMessage('What is your email address?', false);
                return;
            }
            
            if (step === 'email') {
                userEmail = text;
                step = 'phone';
                addMessage('Your phone number? (type "skip" if not needed)', false);
                return;
            }
            
            if (step === 'phone') {
                if (text.toLowerCase() !== 'skip') userPhone = text;
                
                await fetch('/save_lead', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ service, name: userName, email: userEmail, phone: userPhone, time: new Date().toISOString() })
                });
                
                addMessage(Thank you ! Our team will contact you within 24 hours about  service., false);
                addMessage(For immediate help, call +91 9071660066, false);
                
                step = null;
                service = '';
                userName = userEmail = userPhone = '';
                return;
            }
            
            showTyping();
            const res = await fetch('/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message: text}) });
            const data = await res.json();
            hideTyping();
            addMessage(data.reply, false);
        }
        
        userInput.addEventListener('keypress', (e) => { if (e.key === 'Enter') sendChat(); });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/about')
def about():
    return jsonify({'info': '📍 Jakkur-BDA, Bangalore\n📞 +91 9071660066\n📧 shivu@pasfreight.com\n✅ WCA & GLA Certified\n🎯 8+ years experience'})

@app.route('/save_lead', methods=['POST'])
def save_lead():
    data = request.get_json()
    with open('leads.json', 'a') as f:
        f.write(json.dumps(data) + '\\n')
    print(f"LEAD: {data.get('name')} - {data.get('service')}")
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "system", "content": "You are PAS Freight assistant. Give short answers. Call +91 9071660066 for rates."},
                      {"role": "user", "content": user_msg}],
            max_tokens=100
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except:
        return jsonify({'reply': 'Call +91 9071660066 for assistance'})

if __name__ == '__main__':
    print("=" * 40)
    print("🚀 PAS Freight AI - WORKING")
    print("📱 http://localhost:5001")
    print("=" * 40)
    app.run(host='0.0.0.0', port=5001, debug=False)
