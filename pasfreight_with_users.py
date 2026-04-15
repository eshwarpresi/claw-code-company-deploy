import openai
from flask import Flask, request, jsonify, render_template_string
import json
import os

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

# File to store user information
USER_DATA_FILE = "user_data.json"

def save_user_info(name, email, phone):
    data = []
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as f:
            try:
                data = json.load(f)
            except:
                data = []
    
    data.append({
        "name": name,
        "email": email,
        "phone": phone,
        "timestamp": str(__import__('datetime').datetime.now())
    })
    
    with open(USER_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI Assistant</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        /* Modal for user info collection */
        .modal {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-content {
            background: white;
            border-radius: 15px;
            padding: 40px;
            max-width: 450px;
            width: 90%;
            text-align: center;
            animation: slideIn 0.5s ease;
        }
        @keyframes slideIn {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .modal-content h2 {
            color: #1e3c72;
            margin-bottom: 10px;
        }
        .modal-content p {
            color: #666;
            margin-bottom: 25px;
        }
        .modal-content input {
            width: 100%;
            padding: 12px;
            margin: 10px 0;
            border: 1px solid #ddd;
            border-radius: 8px;
            font-size: 14px;
        }
        .modal-content button {
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
        .modal-content button:hover { background: #1e3c72; }
        
        /* Main Chat */
        .chat-container {
            max-width: 900px;
            width: 100%;
            height: 85vh;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 24px; margin-bottom: 5px; }
        .header p { font-size: 12px; opacity: 0.9; }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .msg { margin-bottom: 20px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 20px;
            line-height: 1.4;
            font-size: 14px;
        }
        .user .bubble { background: #2a5298; color: white; border-bottom-right-radius: 4px; }
        .bot .bubble { background: white; color: #333; border: 1px solid #ddd; border-bottom-left-radius: 4px; }
        .input-area {
            padding: 20px;
            background: white;
            display: flex;
            gap: 10px;
            border-top: 1px solid #ddd;
        }
        .input-area input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        .input-area input:focus { border-color: #2a5298; }
        .input-area button {
            padding: 12px 25px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
        }
        .typing { color: #999; font-style: italic; }
        .user-info {
            background: #e8f4f8;
            padding: 10px;
            text-align: center;
            font-size: 12px;
            color: #1e3c72;
        }
    </style>
</head>
<body>
    <div id="userModal" class="modal">
        <div class="modal-content">
            <div style="font-size: 50px;">📦</div>
            <h2>Welcome to PAS Freight</h2>
            <p>Please share your details so we can assist you better and follow up if needed.</p>
            <input type="text" id="userName" placeholder="Your Full Name" required>
            <input type="email" id="userEmail" placeholder="Email Address" required>
            <input type="tel" id="userPhone" placeholder="Phone Number (Optional)">
            <button onclick="startChat()">Start Chatting →</button>
        </div>
    </div>

    <div class="chat-container" id="chatContainer" style="display: none;">
        <div class="header">
            <h1>📦 PAS Freight Services Pvt Ltd</h1>
            <p>Logistics & Freight Solutions | Bangalore | WCA & GLA Certified</p>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="bubble">Namaste! 👋 I'm PAS Freight's AI Assistant. How can I help you with your logistics needs today?</div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Ask about freight, customs, shipping..." autocomplete="off">
            <button onclick="send()">Send</button>
        </div>
    </div>

    <script>
        let userName = '';
        let userEmail = '';
        let userPhone = '';
        
        async function startChat() {
            userName = document.getElementById('userName').value.trim();
            userEmail = document.getElementById('userEmail').value.trim();
            userPhone = document.getElementById('userPhone').value.trim();
            
            if (!userName || !userEmail) {
                alert('Please enter your name and email address to continue.');
                return;
            }
            
            // Save user info
            const response = await fetch('/save_user', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    name: userName,
                    email: userEmail,
                    phone: userPhone
                })
            });
            
            document.getElementById('userModal').style.display = 'none';
            document.getElementById('chatContainer').style.display = 'flex';
            
            // Add welcome message with user's name
            const messagesDiv = document.getElementById('messages');
            const welcomeMsg = document.createElement('div');
            welcomeMsg.className = 'msg bot';
            welcomeMsg.innerHTML = <div class="bubble">Thank you ! I'll make sure to assist you personally. How can I help with your logistics needs today?</div>;
            messagesDiv.appendChild(welcomeMsg);
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
        
        async function send() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMessage(text, true);
            
            const typing = document.createElement('div');
            typing.className = 'msg bot';
            typing.innerHTML = '<div class="bubble typing">Thinking...</div>';
            messagesDiv.appendChild(typing);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: text,
                    user_name: userName,
                    user_email: userEmail
                })
            });
            const data = await res.json();
            typing.remove();
            addMessage(data.reply, false);
        }
        
        input.addEventListener('keypress', (e) => { if (e.key === 'Enter') send(); });
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
    save_user_info(
        data.get('name', ''),
        data.get('email', ''),
        data.get('phone', '')
    )
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    user_name = data.get('user_name', 'Customer')
    user_email = data.get('user_email', '')
    
    system_prompt = f"""You are the official AI assistant for PAS Freight Services Pvt Ltd. The user's name is {user_name} and their email is {user_email}.

COMPANY INFORMATION:
- Services: Air freight, Sea freight, Customs clearance, Trucking, Warehousing, International shipping, Supply chain management
- Contact: +91 9071660066, +91 9164466664
- Email: shivu@pasfreight.com
- Address: Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092
- Certifications: WCA Member ID 115513, GLA Member ID 1166251

When answering:
- Use the user's name ({user_name}) to personalize responses
- Be helpful, professional, and friendly
- For rates: explain they vary by weight, dimensions, and destination
- Always offer to connect with the team via phone or email
- If the user asks complex questions, offer to have a team member call them back
- Answer naturally like a helpful customer service representative

Answer the user's question professionally and helpfully."""

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=500,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        print(f"✓ {user_name}: {user_msg[:50]}")
        return jsonify({'reply': reply})
    except Exception as e:
        print(f"✗ Error: {e}")
        return jsonify({'reply': f'Thank you {user_name} for your inquiry. For immediate assistance, please call +91 9071660066 or email shivu@pasfreight.com'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 PAS Freight AI Assistant with User Info Collection")
    print("📱 Open: http://localhost:5001")
    print("📊 User data saved to: user_data.json")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)
