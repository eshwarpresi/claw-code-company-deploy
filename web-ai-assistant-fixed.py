from flask import Flask, request, jsonify, render_template_string
import subprocess
import json

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Company AI Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background: #f0f2f5;
        }
        .chat-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            height: 80vh;
            display: flex;
            flex-direction: column;
        }
        .chat-header {
            background: #2c3e50;
            color: white;
            padding: 15px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
        }
        .user-message {
            justify-content: flex-end;
        }
        .bot-message {
            justify-content: flex-start;
        }
        .message-content {
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 15px;
            word-wrap: break-word;
        }
        .user-message .message-content {
            background: #007bff;
            color: white;
        }
        .bot-message .message-content {
            background: #e9ecef;
            color: black;
        }
        .chat-input-area {
            padding: 20px;
            border-top: 1px solid #dee2e6;
            display: flex;
            gap: 10px;
        }
        .chat-input {
            flex: 1;
            padding: 10px;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            font-size: 14px;
        }
        .send-button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .send-button:hover {
            background: #0056b3;
        }
        .loading {
            text-align: center;
            color: #666;
            padding: 10px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>🤖 Company AI Assistant</h2>
            <p>Ask me anything!</p>
        </div>
        <div class="chat-messages" id="messages">
            <div class="message bot-message">
                <div class="message-content">Hello! How can I help you today?</div>
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
            contentDiv.innerText = text;
            messageDiv.appendChild(contentDiv);
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function showLoading() {
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'loading';
            loadingDiv.id = 'loading';
            loadingDiv.innerText = 'Thinking...';
            messagesDiv.appendChild(loadingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function hideLoading() {
            const loading = document.getElementById('loading');
            if (loading) loading.remove();
        }
        
        async function sendMessage() {
            const prompt = promptInput.value.trim();
            if (!prompt) return;
            
            promptInput.value = '';
            addMessage(prompt, true);
            showLoading();
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({prompt: prompt})
                });
                const data = await response.json();
                hideLoading();
                addMessage(data.response, false);
            } catch (error) {
                hideLoading();
                addMessage('Sorry, an error occurred. Please try again.', false);
            }
        }
        
        promptInput.addEventListener('keypress', function(e) {
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
            timeout=30
        )
        response = result.stdout if result.stdout else result.stderr
        if not response:
            response = "I processed your request but no output was generated."
    except subprocess.TimeoutExpired:
        response = "Request timed out. Please try again."
    except Exception as e:
        response = f"Error: {str(e)}"
    
    return jsonify({'response': response[:500]})

if __name__ == '__main__':
    print("=" * 50)
    print("🌐 AI Assistant Web Server Starting...")
    print("📱 Open in browser: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
