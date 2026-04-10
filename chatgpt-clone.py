import openai
from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

# Set your OpenRouter API key
openai.api_key = "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"
openai.base_url = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Company AI Chat</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            background: #343541;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat {
            width: 100%;
            max-width: 900px;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: #343541;
        }
        .header {
            padding: 15px 20px;
            background: #202123;
            color: white;
            text-align: center;
            border-bottom: 1px solid #4a4b53;
        }
        .header h1 { font-size: 20px; font-weight: 500; }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .msg {
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
            display: flex;
            gap: 10px;
            border-top: 1px solid #4a4b53;
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
        .input-area button {
            padding: 12px 24px;
            background: #10a37f;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
        }
        .input-area button:hover { background: #1a7f64; }
        .typing { color: #8e8ea0; font-style: italic; }
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <h1>🤖 Company AI Chat</h1>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="bubble">Hello! How can I help you today?</div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Type your message..." autocomplete="off">
            <button onclick="send()">Send</button>
        </div>
    </div>

    <script>
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
            typing.innerHTML = '<div class="bubble typing">Typing...</div>';
            messagesDiv.appendChild(typing);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                typing.remove();
                addMessage(data.reply, false);
            } catch(err) {
                typing.remove();
                addMessage('Error. Please try again.', false);
            }
        }
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') send();
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
            messages=[{"role": "user", "content": user_msg}],
            max_tokens=500
        )
        reply = response.choices[0].message.content
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'Error: {str(e)}'})

if __name__ == '__main__':
    print('=' * 50)
    print('🚀 ChatGPT Clone Running!')
    print('📱 Open http://localhost:5000')
    print('=' * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
