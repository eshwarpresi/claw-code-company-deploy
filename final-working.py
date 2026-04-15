import openai
from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

# Your API key
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
    <style>
        body { font-family: Arial; background: #f0f2f5; margin: 0; padding: 20px; }
        .chat-container { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { background: #1e3c72; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }
        .messages { height: 500px; overflow-y: auto; padding: 20px; }
        .message { margin-bottom: 15px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble { padding: 10px 15px; border-radius: 18px; max-width: 70%; word-wrap: break-word; }
        .user .bubble { background: #1e3c72; color: white; }
        .bot .bubble { background: #e9ecef; color: black; }
        .input-area { padding: 20px; border-top: 1px solid #dee2e6; display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 10px; border: 1px solid #dee2e6; border-radius: 5px; }
        .input-area button { padding: 10px 20px; background: #1e3c72; color: white; border: none; border-radius: 5px; cursor: pointer; }
        .typing { color: #6c757d; font-style: italic; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <h2>📦 PAS Freight AI Assistant</h2>
            <p>Logistics & Freight Solutions | Bangalore</p>
        </div>
        <div class="messages" id="messages">
            <div class="message bot">
                <div class="bubble">Namaste! Welcome to PAS Freight Services. How can I help you with your logistics needs today?</div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type your message..." autocomplete="off">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        
        function addMessage(text, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (isUser ? 'user' : 'bot');
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.innerText = text;
            messageDiv.appendChild(bubble);
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;
            
            userInput.value = '';
            addMessage(text, true);
            
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot';
            typingDiv.innerHTML = '<div class="bubble typing">Thinking...</div>';
            messagesDiv.appendChild(typingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await response.json();
                typingDiv.remove();
                addMessage(data.reply, false);
            } catch (error) {
                typingDiv.remove();
                addMessage('Sorry, an error occurred. Please try again.', false);
            }
        }
        
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
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
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are PAS Freight customer service. Answer professionally about freight forwarding, customs clearance, trucking, warehousing, and international shipping. Company contact: +91 9071660066, Email: shivu@pasfreight.com, Address: Bangalore. Be helpful and concise."},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=300
        )
        reply = response['choices'][0]['message']['content']
        print(f"Success: {reply[:50]}")
        return jsonify({'reply': reply})
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR: {error_msg}")
        return jsonify({'reply': f'Thank you for your inquiry. For immediate assistance, please call +91 9071660066 or email shivu@pasfreight.com.'})

if __name__ == '__main__':
    print('=' * 50)
    print('PAS Freight AI Assistant Starting...')
    print('Open http://localhost:5000 in your browser')
    print('=' * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
