import openai
from flask import Flask, request, jsonify, render_template_string
import json
import os
from datetime import datetime

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

USER_DATA_FILE = "users.json"

def save_user(name, email, phone):
    users = []
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            try:
                users = json.load(f)
            except:
                users = []
    users.append({"name": name, "email": email, "phone": phone, "time": str(datetime.now())})
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI - Advanced Assistant</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .chat-box {
            max-width: 1000px;
            width: 100%;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            overflow: hidden;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 24px; }
        .header p { font-size: 12px; opacity: 0.9; margin-top: 5px; }
        .form-area {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            background: #f8f9fa;
        }
        .form-card {
            background: white;
            padding: 40px;
            border-radius: 15px;
            width: 90%;
            max-width: 400px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }
        .form-card h3 { color: #1e3c72; margin-bottom: 20px; text-align: center; }
        .form-card input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        .form-card button {
            width: 100%;
            padding: 12px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 10px;
        }
        .chat-area {
            flex: 1;
            display: none;
            flex-direction: column;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .msg { margin-bottom: 16px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            padding: 10px 16px;
            border-radius: 20px;
            max-width: 75%;
            font-size: 14px;
            line-height: 1.5;
            word-wrap: break-word;
        }
        .user .bubble { background: #2a5298; color: white; border-bottom-right-radius: 4px; }
        .bot .bubble { background: white; color: #333; border: 1px solid #e0e0e0; border-bottom-left-radius: 4px; }
        .input-area {
            padding: 20px;
            background: white;
            display: flex;
            gap: 12px;
            border-top: 1px solid #e5e5e5;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        .input-area input:focus { border-color: #2a5298; }
        .input-area button {
            padding: 12px 24px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 500;
        }
        .typing { color: #999; font-style: italic; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .msg { animation: fadeIn 0.3s ease; }
    </style>
</head>
<body>
    <div class="chat-box">
        <div class="header">
            <h1>📦 PAS Freight Services</h1>
            <p>Advanced AI Assistant | 24/7 Support</p>
        </div>
        
        <div id="formSection" class="form-area">
            <div class="form-card">
                <h3>✨ Welcome to PAS Freight AI</h3>
                <input type="text" id="userName" placeholder="Your Name *">
                <input type="email" id="userEmail" placeholder="Email Address *">
                <input type="tel" id="userPhone" placeholder="Phone Number">
                <button onclick="startChat()">Start Conversation →</button>
            </div>
        </div>
        
        <div id="chatSection" class="chat-area">
            <div class="messages" id="messages">
                <div class="msg bot">
                    <div class="bubble">👋 Hey! I'm your PAS Freight AI. Ask me anything about shipping, freight, or logistics. I speak English, Hindi, and Kannada!</div>
                </div>
            </div>
            <div class="input-area">
                <input type="text" id="input" placeholder="Type in English, Hindi, or Kannada..." autocomplete="off">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        let userName = '';
        
        async function startChat() {
            const name = document.getElementById('userName').value.trim();
            const email = document.getElementById('userEmail').value.trim();
            const phone = document.getElementById('userPhone').value.trim();
            
            if (!name || !email) {
                alert('Please enter your name and email');
                return;
            }
            
            userName = name;
            
            await fetch('/save_user', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: name, email: email, phone: phone})
            });
            
            document.getElementById('formSection').style.display = 'none';
            document.getElementById('chatSection').style.display = 'flex';
            
            const messagesDiv = document.getElementById('messages');
            const welcome = document.createElement('div');
            welcome.className = 'msg bot';
            welcome.innerHTML = '<div class="bubble">Namaste ' + name + '! 👋 How can I help you today?</div>';
            messagesDiv.appendChild(welcome);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('input');
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            div.innerHTML = '<div class="bubble">' + text.replace(/\\n/g, '<br>') + '</div>';
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMessage(text, true);
            
            const typing = document.createElement('div');
            typing.className = 'msg bot';
            typing.innerHTML = '<div class="bubble typing">...</div>';
            messagesDiv.appendChild(typing);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text, user_name: userName})
            });
            const data = await res.json();
            typing.remove();
            addMessage(data.reply, false);
        }
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/save_user', methods=['POST'])
def save_user():
    data = request.get_json()
    save_user(data.get('name', ''), data.get('email', ''), data.get('phone', ''))
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    user_name = data.get('user_name', '')
    
    system_prompt = """You are PAS Freight's advanced AI assistant. 

IMPORTANT RULES:
1. Give SHORT, CONVERSATIONAL answers (1-2 sentences max)
2. Respond in the SAME LANGUAGE as the user (Kannada, Hindi, English, or mix)
3. Be friendly, warm, and human-like
4. Understand typos and incorrect spelling
5. For rates: Say "Call +91 9071660066 for best rates"
6. Remember user's name and use it naturally
7. NO bullet points, NO numbered lists
8. Just chat like a helpful friend

Company: PAS Freight Services, Bangalore
Contact: +91 9071660066
Services: Air/Sea freight, Customs clearance, Trucking, Warehousing

Examples:
User: "nimma kannada chenagi ill astondhu" 
You: "Naanu try madthini! Hege help madbeku?"

User: "i need rates for shipping"
You: "Call +91 9071660066 - our team will give you the best rates!"

User: "what services"
You: "Air/sea freight, customs clearance, and trucking. Need anything specific?"

Be natural, be helpful, be conversational."""
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=120,
            temperature=0.8
        )
        reply = response['choices'][0]['message']['content']
        print(f"✓ {user_name}: {user_msg[:50]}")
        return jsonify({'reply': reply})
    except Exception as e:
        print(f"✗ Error: {e}")
        return jsonify({'reply': f'Hey {user_name}! Call +91 9071660066 and we will help you right away!'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 PAS Freight ADVANCED AI Assistant")
    print("📱 Open: http://localhost:5001")
    print("💬 Supports: English, Hindi, Kannada")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)
