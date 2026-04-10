from flask import Flask, request, jsonify, render_template_string
import subprocess
import json
import os

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Company AI Assistant</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            width: 90%;
            max-width: 1200px;
            height: 85vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .chat-header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .chat-header h1 { font-size: 24px; }
        .chat-header p { opacity: 0.9; margin-top: 5px; }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        .user-message {
            justify-content: flex-end;
        }
        .bot-message {
            justify-content: flex-start;
        }
        .message-content {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .user-message .message-content {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .bot-message .message-content {
            background: white;
            color: #333;
            border: 1px solid #ddd;
            border-bottom-left-radius: 4px;
        }
        .chat-input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }
        .chat-input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        .send-button {
            padding: 12px 24px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
        }
        .send-button:hover { background: #5a67d8; }
        .typing { opacity: 0.7; font-style: italic; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 Company AI Assistant</h1>
            <p>Powered by Claw-Code | Ask me anything!</p>
        </div>
        <div class="chat-messages" id="messages">
            <div class="message bot-message">
                <div class="message-content">Hello! I'm your AI assistant. How can I help you today?</div>
            </div>
        </div>
        <div class="chat-input-area">
            <input type="text" class="chat-input" id="prompt" placeholder="Type your message here..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button class="send-button" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        async function sendMessage() {
            const input = document.getElementById('prompt');
            const message = input.value.trim();
            if (!message) return;
            
            input.value = '';
            addMessage(message, 'user');
            
            const responseDiv = addMessage('', 'bot');
            responseDiv.querySelector('.message-content').innerHTML = '<span class="typing">Typing...</span>';
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: message})
                });
                const data = await response.json();
                responseDiv.querySelector('.message-content').innerHTML = data.response.replace(/\\n/g, '<br>');
            } catch(error) {
                responseDiv.querySelector('.message-content').innerHTML = 'Sorry, an error occurred. Please try again.';
            }
            
            const messagesDiv = document.getElementById('messages');
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function addMessage(text, sender) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = message -message;
            messageDiv.innerHTML = <div class="message-content"></div>;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            return messageDiv;
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    prompt = request.json.get('prompt', '')
    
    result = subprocess.run(
        ['C:\\Users\\prave\\.cargo\\bin\\claw.exe', 
         '--model', 'openai/gpt-4o-mini', 
         'prompt', prompt],
        capture_output=True,
        text=True,
        shell=True,
        timeout=60
    )
    
    response_text = result.stdout if result.stdout else result.stderr
    if not response_text or response_text.strip() == '':
        response_text = "I couldn't process that request. Please try again."
    
    return jsonify({'response': response_text[:2000]})

if __name__ == '__main__':
    print("=" * 50)
    print("🌐 Company AI Assistant Web Server Starting...")
    print("📱 Open in your browser: http://localhost:5000")
    print("🔒 Press Ctrl+C to stop the server")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
