from flask import Flask, request, jsonify, render_template_string
import subprocess
import json
import re

app = Flask(__name__)

def get_ai_response(prompt):
    try:
        # Call claw with JSON output to avoid terminal codes
        result = subprocess.run(
            ['C:\\Users\\prave\\.cargo\\bin\\claw.exe', 
             '--model', 'openai/gpt-4o-mini',
             '--output-format', 'json',
             'prompt', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Try to parse JSON response
        if result.stdout:
            try:
                data = json.loads(result.stdout)
                if 'response' in data:
                    return data['response']
                elif 'content' in data:
                    return data['content']
            except:
                pass
        
        # If not JSON, clean the text
        text = result.stdout if result.stdout else result.stderr
        # Remove ANSI escape sequences
        ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
        text = ansi_escape.sub('', text)
        # Remove common symbols
        text = text.replace('✓', '').replace('✗', '').replace('✨', '')
        text = text.replace('🦀', '').replace('Thinking...', '')
        text = re.sub(r'\[[0-9;]*[mGKH]', '', text)
        text = text.strip()
        
        if text and len(text) > 5:
            return text[:500]
        
        return "I received your message. How can I help you?"
        
    except subprocess.TimeoutExpired:
        return "Request timed out. Please try again."
    except Exception as e:
        return f"Error: {str(e)[:100]}"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Company AI Assistant</title>
    <meta charset="UTF-8">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            margin: 0;
            padding: 20px;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-box {
            width: 100%;
            max-width: 900px;
            height: 85vh;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            background: #2c3e50;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { margin: 0; font-size: 24px; }
        .header p { margin: 5px 0 0; opacity: 0.9; font-size: 14px; }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
        }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            max-width: 70%;
            padding: 10px 15px;
            border-radius: 15px;
            word-wrap: break-word;
        }
        .user .bubble {
            background: #007bff;
            color: white;
        }
        .bot .bubble {
            background: white;
            color: #333;
            border: 1px solid #ddd;
        }
        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        .input-area button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .input-area button:hover { background: #0056b3; }
        .loading { opacity: 0.6; font-style: italic; }
    </style>
</head>
<body>
    <div class="chat-box">
        <div class="header">
            <h1>🤖 Company AI Assistant</h1>
            <p>Ask me anything - Powered by AI</p>
        </div>
        <div class="messages" id="messages">
            <div class="message bot">
                <div class="bubble">Hello! How can I help you today?</div>
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
            bubble.textContent = text;
            messageDiv.appendChild(bubble);
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;
            
            userInput.value = '';
            addMessage(text, true);
            
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message bot';
            loadingDiv.innerHTML = '<div class="bubble loading">Thinking...</div>';
            messagesDiv.appendChild(loadingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            try {
                const response = await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({prompt: text})
                });
                const data = await response.json();
                loadingDiv.remove();
                addMessage(data.response, false);
            } catch (error) {
                loadingDiv.remove();
                addMessage('Sorry, an error occurred. Please try again.', false);
            }
        }
        
        userInput.addEventListener('keypress', function(e) {
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
    response = get_ai_response(prompt)
    return jsonify({'response': response})

if __name__ == '__main__':
    print("🚀 AI Assistant Server Started!")
    print("📱 Open http://localhost:5000 in your browser")
    print("Press Ctrl+C to stop")
    app.run(host='0.0.0.0', port=5000, debug=False)
