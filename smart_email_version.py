import openai
from flask import Flask, request, jsonify, render_template_string
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

# Email configuration - Update with your SMTP settings
EMAIL_CONFIG = {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "sender_email": "your-email@gmail.com",  # Update this
    "sender_password": "your-app-password",   # Update this
    "receiver_email": "priya.c@pasfreight.com"
}

def send_email_notification(user_name, user_email, user_phone, conversation):
    try:
        subject = f"New Lead: {user_name} from PAS Freight AI"
        
        body = f"""
        New User Details from PAS Freight AI Chatbot
        
        Name: {user_name}
        Email: {user_email}
        Phone: {user_phone}
        Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Conversation Summary:
        {conversation}
        
        Please follow up with this lead.
        """
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = EMAIL_CONFIG['receiver_email']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['sender_email'], EMAIL_CONFIG['sender_password'])
        server.send_message(msg)
        server.quit()
        print(f"✓ Email sent to priya.c@pasfreight.com for {user_name}")
        return True
    except Exception as e:
        print(f"✗ Email error: {e}")
        return False

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI - Smart Assistant</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .chat-container {
            max-width: 900px;
            width: 100%;
            height: 90vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
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
        .header h1 { font-size: 22px; }
        .header p { font-size: 12px; opacity: 0.9; margin-top: 5px; }
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
            line-height: 1.4;
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
    <div class="chat-container">
        <div class="header">
            <h1>📦 PAS Freight Services</h1>
            <p>Smart AI Assistant | 24/7 Logistics Support</p>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="bubble">👋 Namaste! Welcome to PAS Freight. Before we begin, could you please share your name?</div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Type your message..." autocomplete="off">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('input');
        let step = 'asking_name';
        let userName = '';
        let userEmail = '';
        let userPhone = '';
        let conversationHistory = [];
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            div.innerHTML = '<div class="bubble">' + text.replace(/\\n/g, '<br>') + '</div>';
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            conversationHistory.push({role: isUser ? 'user' : 'bot', text: text});
        }
        
        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMessage(text, true);
            
            // Handle info collection steps
            if (step === 'asking_name') {
                userName = text;
                step = 'asking_email';
                addMessage('Thanks! Could you please share your email address? We will send you updates.', false);
                return;
            }
            
            if (step === 'asking_email') {
                userEmail = text;
                step = 'asking_phone';
                addMessage('Great! One last thing - your phone number? (Optional, for quick follow-up)', false);
                return;
            }
            
            if (step === 'asking_phone') {
                userPhone = text;
                step = 'ready';
                addMessage('Thank you ' + userName + '! 🎉 Now I can help you with your logistics needs. What would you like to know about?', false);
                
                // Send user details to email
                const res = await fetch('/save_user', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        name: userName,
                        email: userEmail,
                        phone: userPhone,
                        conversation: conversationHistory.map(m => ${m.role}: ).join('\\n')
                    })
                });
                return;
            }
            
            // Normal AI conversation
            const typing = document.createElement('div');
            typing.className = 'msg bot';
            typing.innerHTML = '<div class="bubble typing">...</div>';
            messagesDiv.appendChild(typing);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: text,
                    user_name: userName,
                    user_email: userEmail,
                    step: step
                })
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
    name = data.get('name', '')
    email = data.get('email', '')
    phone = data.get('phone', '')
    conversation = data.get('conversation', '')
    
    # Save to file
    user_data = {"name": name, "email": email, "phone": phone, "time": str(datetime.now())}
    with open('users.json', 'a') as f:
        f.write(json.dumps(user_data) + '\\n')
    
    # Send email to priya.c@pasfreight.com
    try:
        send_email_notification(name, email, phone, conversation)
    except Exception as e:
        print(f"Email error: {e}")
    
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    user_name = data.get('user_name', '')
    step = data.get('step', 'ready')
    
    system_prompt = f"""You are PAS Freight's AI assistant. User name: {user_name}

RULES:
- Give VERY SHORT answers (1-2 sentences max)
- Respond in same language as user
- Be friendly and helpful
- NO bullet points, NO lists
- For rates: Say "Call +91 9071660066 for best rates"
- Understand typos

Company: PAS Freight Services, Bangalore
Contact: +91 9071660066
Services: Air/Sea freight, Customs clearance, Trucking, Warehousing

Be natural and conversational."""
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=100,
            temperature=0.8
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'Hey {user_name}! Call +91 9071660066 and we will help you right away!'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 PAS Freight AI - Smart Assistant")
    print("📱 Open: http://localhost:5001")
    print("📧 Emails will be sent to: priya.c@pasfreight.com")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)
