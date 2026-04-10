from flask import Flask, request, jsonify, render_template_string
import subprocess
import re

app = Flask(__name__)

def clean_response(text):
    # Remove terminal escape sequences and special characters
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    text = ansi_escape.sub('', text)
    # Remove other special characters
    text = text.replace('âœ"', '').replace('âœ˜', '').replace('ðŸ¦€', '')
    text = re.sub(r'\[[0-9;]*[mGKH]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Company AI Assistant</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            width: 90%;
            max-width: 1000px;
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
        .chat-header h1 { font-size: 28px; margin-bottom: 5px; }
        .chat-header p { opacity: 0.9; font-size: 14px; }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
        }
        .user-message { justify-content: flex-end; }
        .bot-message { justify-content: flex-start; }
        .message-content {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
            line-height: 1.4;
        }
        .user-message .message-content {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }
        .bot-message .message-content {
            background: white;
            color: #333;
            border: 1px solid #dee2e6;
            border-bottom-left-radius: 4px;
        }
        .chat-input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #dee2e6;
            display: flex;
            gap: 10px;
        }
        .chat-input {
            flex: 1;
            padding: 12px;
            border: 1px solid #dee2e6;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        .chat-input:focus { border-color: #667eea; }
        .send-button {
            padding: 12px 28px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
        }
        .send-button:hover { background: #5a67d8; }
        .typing {
            opacity: 0.7;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🤖 Company AI Assistant</h1>
            <p>Powered by AI | Ask me anything!</p>
        </div>
        <div class="chat-messages" id="messages">
            <div class="message bot-message">
                <div class="message-content">Hello! I'm your AI assistant. How can I help you today?</div>
            </div>
        </div>
        <div class="chat-input-area">
            <input type="text" id="prompt" class="chat-input" placeholder="Type your message here..." autocomplete="off">
            <button onclick="sendMessage()" class="send-button">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const promptInput = document.getElementById('prompt');
        
        function addMessage(text, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = text;
            messageDiv.appendChild(contentDiv);
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        async function sendMessage() {
            const prompt = promptInput.value.trim();
            if (!prompt) return;
            
            promptInput.value = '';
            addMessage(prompt, true);
            
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message';
            typingDiv.innerHTML = '<div class="message-content typing">Thinking...</div>';
            messagesDiv.appendChild(typingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: prompt})
                });
                const data = await response.json();
                typingDiv.remove();
                addMessage(data.response, false);
            } catch (error) {
                typingDiv.remove();
                addMessage('Sorry, an error occurred. Please try again.', false);
            }
        }
        
        promptInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    prompt = data.get('prompt', '')
    
    try:
        result = subprocess.run(
            ['C:\\Users\\prave\\.cargo\\bin\\claw.exe', '--model', 'openai/gpt-4o-mini', 'prompt', prompt],
            capture_output=True,
            text=True,
            timeout=60
        )
        response = result.stdout if result.stdout else result.stderr
        response = clean_response(response)
        
        if not response or len(response.strip()) < 2:
            response = "I processed your request. How can I help further?"
            
    except subprocess.TimeoutExpired:
        response = "Request timed out. Please try again."
    except Exception as e:
        response = f"Error: {str(e)[:100]}"
    
    return jsonify({'response': response[:1000]})

if __name__ == '__main__':
    print("=" * 50)
    print("🌐 Clean AI Assistant Web Server Starting...")
    print("📱 Open in browser: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
