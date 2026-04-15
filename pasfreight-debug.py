import openai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

COMPANY_NAME = "PAS Freight Services Pvt Ltd"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
    <style>
        body { font-family: Arial; background: #1e3c72; margin: 0; padding: 20px; }
        .chat { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; height: 90vh; display: flex; flex-direction: column; }
        .header { background: #1e3c72; color: white; padding: 15px; text-align: center; }
        .messages { flex: 1; overflow-y: auto; padding: 20px; }
        .msg { margin-bottom: 15px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble { padding: 10px 15px; border-radius: 15px; max-width: 70%; }
        .user .bubble { background: #2a5298; color: white; }
        .bot .bubble { background: #e9ecef; color: black; }
        .input-area { padding: 15px; display: flex; gap: 10px; border-top: 1px solid #ddd; }
        .input-area input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        .input-area button { padding: 10px 20px; background: #2a5298; color: white; border: none; border-radius: 5px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <h2>📦 PAS Freight AI Assistant</h2>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot"><div class="bubble">Hello! How can I help with your logistics needs?</div></div>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Type your question...">
            <button onclick="send()">Send</button>
        </div>
    </div>
    <script>
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('input');
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            div.innerHTML = '<div class="bubble">' + text + '</div>';
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        async function send() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMessage(text, true);
            addMessage('Thinking...', false);
            
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                messagesDiv.lastChild.remove();
                addMessage(data.reply, false);
            } catch(err) {
                messagesDiv.lastChild.remove();
                addMessage('Error. Please try again.', false);
            }
        }
        input.addEventListener('keypress', (e) => { if (e.key === 'Enter') send(); });
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
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_msg}],
            max_tokens=300
        )
        reply = response['choices'][0]['message']['content']
        print(f"Success: {reply[:50]}")  # Debug print
        return jsonify({'reply': reply})
    except Exception as e:
        error_message = str(e)
        print(f"ERROR: {error_message}")  # This will show in PowerShell
        return jsonify({'reply': f'Debug - Error: {error_message[:200]}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
