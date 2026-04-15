from flask import Flask, request, jsonify, render_template_string
import openai
import json

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .chat-container {
            max-width: 450px;
            width: 100%;
            background: white;
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        .header {
            background: #1e3c72;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 18px; }
        .messages {
            height: 500px;
            overflow-y: auto;
            padding: 20px;
            background: #f0f2f5;
        }
        .msg { margin-bottom: 15px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            padding: 10px 15px;
            border-radius: 18px;
            max-width: 75%;
            font-size: 14px;
        }
        .user .bubble { background: #2a5298; color: white; }
        .bot .bubble { background: white; color: #333; border: 1px solid #ddd; }
        .buttons {
            padding: 15px;
            background: white;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            border-top: 1px solid #ddd;
        }
        .btn {
            flex: 1;
            min-width: 80px;
            padding: 10px;
            background: #1e3c72;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
        }
        .input-area {
            padding: 15px;
            background: white;
            display: flex;
            gap: 10px;
            border-top: 1px solid #ddd;
        }
        .input-area input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 14px;
            outline: none;
        }
        .input-area button {
            padding: 10px 20px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
        }
    </style>
</head>
<body>
<div class="chat-container">
    <div class="header">
        <h1>📦 PAS Freight Services Pvt Ltd</h1>
    </div>
    <div class="messages" id="messages">
        <div class="msg bot"><div class="bubble">Welcome! Click a service below.</div></div>
    </div>
    <div class="buttons">
        <button class="btn" onclick="testClick('import')">📦 Import</button>
        <button class="btn" onclick="testClick('export')">🚢 Export</button>
        <button class="btn" onclick="testClick('customs')">📋 Customs</button>
        <button class="btn" onclick="testClick('domestic')">🚚 Domestic</button>
        <button class="btn" onclick="testClick('courier')">📮 Courier</button>
        <button class="btn" onclick="testClick('about')">🏢 About</button>
    </div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Type your question...">
        <button onclick="sendMessage()">Send</button>
    </div>
</div>

<script>
function addMessage(text, isUser) {
    const messages = document.getElementById('messages');
    const div = document.createElement('div');
    div.className = 'msg ' + (isUser ? 'user' : 'bot');
    div.innerHTML = '<div class="bubble">' + text + '</div>';
    messages.appendChild(div);
    messages.scrollTop = messages.scrollHeight;
}

function testClick(service) {
    addMessage('I clicked ' + service, true);
    
    if (service === 'import') {
        addMessage('📞 For Import/Export services, please call: 90716 60066', false);
    } else if (service === 'export') {
        addMessage('📞 For Import/Export services, please call: 90716 60066', false);
    } else if (service === 'customs') {
        addMessage('📞 For Customs Clearance, please call: 63615 26664', false);
    } else if (service === 'domestic') {
        addMessage('📞 For Domestic/Courier services, please call: 96116 60204', false);
    } else if (service === 'courier') {
        addMessage('📞 For Domestic/Courier services, please call: 96116 60204', false);
    } else if (service === 'about') {
        addMessage('📍 Jakkur-BDA, Bangalore\n📞 +91 9071660066\n📧 shivu@pasfreight.com', false);
    }
}

async function sendMessage() {
    const input = document.getElementById('userInput');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    addMessage(text, true);
    
    const res = await fetch('/chat', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({message: text})
    });
    const data = await res.json();
    addMessage(data.reply, false);
}
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
            max_tokens=100
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': 'Call +91 9071660066 for assistance'})

if __name__ == '__main__':
    print("🚀 Server running at http://localhost:5001")
    app.run(host='0.0.0.0', port=5001, debug=False)
