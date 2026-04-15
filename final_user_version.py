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
    
    users.append({
        "name": name,
        "email": email,
        "phone": phone,
        "time": str(datetime.now())
    })
    
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(users, f, indent=2)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
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
        .chat-box {
            max-width: 900px;
            width: 100%;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 50px rgba(0,0,0,0.3);
            overflow: hidden;
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
            padding: 30px;
            background: #f8f9fa;
        }
        .form-area h3 { color: #1e3c72; margin-bottom: 20px; }
        .form-area input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        .form-area button {
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
        .form-area button:hover { background: #1e3c72; }
        .chat-area {
            display: none;
            flex-direction: column;
            height: 500px;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .msg { margin-bottom: 15px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 70%;
            font-size: 14px;
        }
        .user .bubble { background: #2a5298; color: white; }
        .bot .bubble { background: white; color: black; border: 1px solid #ddd; }
        .input-area {
            padding: 15px;
            background: white;
            display: flex;
            gap: 10px;
            border-top: 1px solid #ddd;
        }
        .input-area input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 14px;
        }
        .input-area button {
            padding: 10px 20px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
        }
        .typing { color: #999; font-style: italic; }
    </style>
</head>
<body>
    <div class="chat-box">
        <div class="header">
            <h1>📦 PAS Freight Services</h1>
            <p>Logistics & Freight Solutions | Bangalore</p>
        </div>
        
        <div id="formSection" class="form-area">
            <h3>Welcome! Please share your details to get started</h3>
            <input type="text" id="userName" placeholder="Full Name *">
            <input type="email" id="userEmail" placeholder="Email Address *">
            <input type="tel" id="userPhone" placeholder="Phone Number (Optional)">
            <button onclick="startChat()">Start Chatting</button>
        </div>
        
        <div id="chatSection" class="chat-area">
            <div class="messages" id="messages">
                <div class="msg bot">
                    <div class="bubble">Hello! How can I help you with your logistics needs today?</div>
                </div>
            </div>
            <div class="input-area">
                <input type="text" id="input" placeholder="Type your message...">
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
            welcome.innerHTML = '<div class="bubble">Thank you ' + name + '! How can I assist you with your logistics needs today?</div>';
            messagesDiv.appendChild(welcome);
        }
        
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('input');
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            div.innerHTML = '<div class="bubble">' + text + '</div>';
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
            typing.innerHTML = '<div class="bubble typing">Typing...</div>';
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
    user_name = data.get('user_name', 'Customer')
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are PAS Freight AI assistant. User name is {user_name}. Answer professionally about logistics services."},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=300
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'Thank you {user_name}. For assistance, call +91 9071660066'})

if __name__ == '__main__':
    print('Server running at http://localhost:5001')
    app.run(host='0.0.0.0', port=5001, debug=False)
