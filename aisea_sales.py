import openai
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import re

app = Flask(__name__)
CORS(app)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

session_memory = {}

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Aisea - PAS Freight AI</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #343541; height: 100vh; display: flex; justify-content: center; align-items: center; }
        
        #pasfreight-chat-btn {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 56px;
            height: 56px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 8px 24px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            border: none;
            z-index: 999999;
        }
        #pasfreight-chat-btn:hover { transform: scale(1.08); box-shadow: 0 12px 32px rgba(0,0,0,0.25); }
        .chat-icon { font-size: 28px; color: white; }
        
        .notification-badge {
            position: absolute;
            top: -4px;
            right: -4px;
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
            bottom: 90px;
            right: 24px;
            width: 420px;
            height: 620px;
            background: #343541;
            border-radius: 24px;
            box-shadow: 0 24px 48px rgba(0,0,0,0.3);
            display: none;
            z-index: 999998;
            border: none;
            overflow: hidden;
            flex-direction: column;
        }
        
        .chat-header {
            background: #202123;
            padding: 16px 18px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid #4a4b53;
        }
        .header-info { display: flex; align-items: center; gap: 10px; }
        .avatar { width: 36px; height: 36px; background: #2a5298; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; }
        .header-text h3 { font-size: 16px; font-weight: 600; color: #ececec; }
        .header-text p { font-size: 10px; color: #8e8ea0; margin-top: 2px; }
        .close-chat { background: none; border: none; color: #8e8ea0; font-size: 18px; cursor: pointer; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
        .close-chat:hover { background: #40414f; color: white; }
        
        .chat-messages { flex: 1; overflow-y: auto; padding: 20px; background: #343541; }
        .message { margin-bottom: 20px; display: flex; }
        .user-message { justify-content: flex-end; }
        .bot-message { justify-content: flex-start; }
        .bubble { max-width: 80%; padding: 10px 14px; border-radius: 20px; font-size: 13px; line-height: 1.45; }
        .user-message .bubble { background: #2a5298; color: white; border-bottom-right-radius: 4px; }
        .bot-message .bubble { background: #444654; color: #ececec; border-bottom-left-radius: 4px; }
        
        .chat-input { padding: 16px; background: #40414f; border-top: 1px solid #4a4b53; display: flex; gap: 10px; }
        .chat-input input { flex: 1; padding: 12px 16px; background: #40414f; border: 1px solid #565869; border-radius: 28px; font-size: 13px; color: white; outline: none; font-family: 'Inter', sans-serif; }
        .chat-input input::placeholder { color: #8e8ea0; }
        .chat-input input:focus { border-color: #10a37f; }
        .chat-input button { background: #10a37f; color: white; border: none; width: 42px; height: 42px; border-radius: 50%; cursor: pointer; font-size: 18px; transition: all 0.2s; }
        .chat-input button:hover { background: #1a7f64; transform: scale(1.02); }
        
        .typing { display: inline-flex; gap: 5px; padding: 6px 0; }
        .typing span { width: 7px; height: 7px; background: #8e8ea0; border-radius: 50%; animation: typingBounce 1.4s infinite; }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typingBounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-8px); } }
        
        .chat-messages::-webkit-scrollbar { width: 5px; }
        .chat-messages::-webkit-scrollbar-track { background: #40414f; }
        .chat-messages::-webkit-scrollbar-thumb { background: #565869; border-radius: 5px; }
        
        @media (max-width: 500px) {
            #pasfreight-chat-window { width: 100%; height: 100%; bottom: 0; right: 0; border-radius: 0; }
            #pasfreight-chat-btn { bottom: 16px; right: 16px; }
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
                    <h3>Aisea</h3>
                    <p>PAS Freight AI • 24/7</p>
                </div>
            </div>
            <button class="close-chat" id="closeChatBtn">✕</button>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="message bot-message">
                <div class="bubble">Hi, I'm Aisea. Need rates? Share weight + destination.</div>
            </div>
        </div>
        
        <div class="chat-input">
            <input type="text" id="userInput" placeholder="Ask me anything..." autocomplete="off">
            <button id="sendBtn">➤</button>
        </div>
    </div>

    <script>
        let sessionId = 'session_' + Date.now();
        let isOpen = false;
        let notified = false;
        
        const chatBtn = document.getElementById('pasfreight-chat-btn');
        const chatWindow = document.getElementById('pasfreight-chat-window');
        const closeChatBtn = document.getElementById('closeChatBtn');
        const notificationBadge = document.getElementById('notificationBadge');
        const messagesDiv = document.getElementById('chatMessages');
        const userInput = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        
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
                    body: JSON.stringify({ message: text, session_id: sessionId })
                });
                const data = await response.json();
                hideTyping();
                addMessage(data.reply, false);
            } catch(error) {
                hideTyping();
                addMessage('Call +91 90361 01201.', false);
            }
        }
        
        sendBtn.addEventListener('click', sendMessage);
        userInput.addEventListener('keypress', function(e) { if (e.key === 'Enter') sendMessage(); });
    </script>
</body>
</html>
'''

def update_context(user_msg, ctx):
    new_ctx = ctx.copy()
    
    weight_match = re.search(r'(\d+)\s*(?:kg|kgs|kilogram|kilo|ton)', user_msg, re.IGNORECASE)
    if weight_match:
        new_ctx['weight'] = weight_match.group(1)
    
    dest_match = re.search(r'(?:to|for|from|change to)\s+([A-Z][a-z]+|[A-Z]{2})', user_msg, re.IGNORECASE)
    if dest_match:
        new_ctx['destination'] = dest_match.group(1)
    
    return new_ctx

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    session_id = data.get('session_id', 'default')
    
    if session_id not in session_memory:
        session_memory[session_id] = {'weight': None, 'destination': None}
    
    session_memory[session_id] = update_context(user_msg, session_memory[session_id])
    ctx = session_memory[session_id]
    
    context_str = ""
    if ctx.get('weight'):
        context_str += f" {ctx['weight']}kg"
    if ctx.get('destination'):
        context_str += f" to {ctx['destination']}"
    
    system_prompt = f"""You are Aisea, a sales-driven logistics assistant for PAS Freight.

RULES:
- Keep responses SHORT (2-3 lines max)
- ALWAYS end with a question or CTA
- Use urgency when possible
- Be direct, not polite

FORMAT EXAMPLES:
User: "100kg to Dubai"
You: "✈️ Air: ₹320-400/kg (3-5 days)\n🚢 Sea: ₹80-120/kg (20-30 days)\n\nWhat matters more - speed or cost?"

User: "rates"
You: "For {context_str}:\n✈️ Air: ₹320-400/kg\n🚢 Sea: ₹80-120/kg\n\nShare your number - I'll lock today's best rate."

User: "hi"
You: "Hi! Need rates? Share weight + destination."

Company: PAS Freight, Contact: +91 90361 01201

Be short, sharp, and sales-focused. Always close with a question or action."""

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
        return jsonify({'reply': 'Share weight + destination for best rates. Call +91 90361 01201.'})

if __name__ == '__main__':
    print("=" * 60)
    print("Aisea - Sales-Optimized AI (9.5/10)")
    print("Open: http://localhost:5001")
    print("Features: Short replies | CTAs | Urgency | Lead capture")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
