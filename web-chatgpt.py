from flask import Flask, request, jsonify, render_template_string
import subprocess
import json
import re

app = Flask(__name__)

def clean_response(text):
    # Remove markdown math formatting
    text = re.sub(r'\\\(', '', text)
    text = re.sub(r'\\\)', '', text)
    text = re.sub(r'\\\[', '', text)
    text = re.sub(r'\\\]', '', text)
    
    # Remove special characters
    text = text.replace('â€¢', '-')
    text = text.replace('â€"', '-')
    text = text.replace('â€™', "'")
    
    # Clean up extra spaces
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def get_ai_response(prompt):
    try:
        result = subprocess.run(
            ['C:\\Users\\prave\\.cargo\\bin\\claw.exe', 
             '--model', 'openai/gpt-4o-mini',
             'prompt', prompt],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Get the output and clean it
        response = result.stdout if result.stdout else result.stderr
        
        # Find the actual response (after the thinking process)
        lines = response.split('\n')
        clean_response_text = ""
        
        for line in lines:
            # Skip lines with thinking indicators
            if 'Thinking' in line or '✨' in line or '✓' in line or '✗' in line:
                continue
            # Skip empty lines
            if line.strip():
                clean_response_text += line.strip() + ' '
        
        if not clean_response_text:
            clean_response_text = "I received your message. How can I help?"
        
        # Clean the response
        clean_response_text = clean_response(clean_response_text)
        
        return clean_response_text[:800]
        
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
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #343541;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            width: 100%;
            max-width: 1000px;
            height: 100vh;
            background: #343541;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #202123;
            color: white;
            padding: 15px 20px;
            text-align: center;
            border-bottom: 1px solid #4a4b53;
        }
        .header h1 { font-size: 20px; font-weight: 500; }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            margin-bottom: 20px;
            display: flex;
        }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 8px;
            line-height: 1.5;
            font-size: 14px;
        }
        .user .bubble {
            background: #10a37f;
            color: white;
        }
        .bot .bubble {
            background: #444654;
            color: #ececec;
        }
        .input-area {
            padding: 20px;
            background: #40414f;
            border-top: 1px solid #4a4b53;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px;
            background: #40414f;
            border: 1px solid #565869;
            border-radius: 8px;
            color: white;
            font-size: 14px;
            outline: none;
        }
        .input-area input::placeholder { color: #8e8ea0; }
        .input-area input:focus { border-color: #10a37f; }
        .input-area button {
            padding: 12px 24px;
            background: #10a37f;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
        }
        .input-area button:hover { background: #1a7f64; }
        .loading {
            background: #444654;
            color: #8e8ea0;
            padding: 12px 16px;
            border-radius: 8px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <h1>🤖 Company AI Assistant</h1>
        </div>
        <div class="messages" id="messages">
            <div class="message bot">
                <div class="bubble">Hello! How can I help you today?</div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="userInput" placeholder="Send a message..." autocomplete="off">
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
            loadingDiv.innerHTML = '<div class="loading">Typing...</div>';
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
    print("=" * 50)
    print("🚀 ChatGPT-like AI Assistant Ready!")
    print("📱 Open: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
