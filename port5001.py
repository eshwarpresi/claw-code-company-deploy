import openai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight Smart AI</title>
    <style>
        body { font-family: Arial; background: #1e3c72; margin: 0; padding: 20px; }
        .chat { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; }
        .header { background: #1e3c72; color: white; padding: 20px; text-align: center; }
        .messages { height: 500px; overflow-y: auto; padding: 20px; background: #f8f9fa; }
        .msg { margin-bottom: 15px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble { padding: 10px 15px; border-radius: 18px; max-width: 70%; }
        .user .bubble { background: #2a5298; color: white; }
        .bot .bubble { background: white; color: black; border: 1px solid #ddd; }
        .input-area { padding: 20px; display: flex; gap: 10px; background: white; }
        .input-area input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; }
        .input-area button { padding: 12px 25px; background: #2a5298; color: white; border: none; border-radius: 25px; cursor: pointer; }
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <h2>📦 PAS Freight Smart AI</h2>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot"><div class="bubble">Hello! I'm your PAS Freight AI assistant. What would you like to know about our logistics services?</div></div>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Ask me anything..." autocomplete="off">
            <button onclick="send()">Send</button>
        </div>
    </div>
    <script>
        const messages = document.getElementById('messages');
        const input = document.getElementById('input');
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            div.innerHTML = '<div class="bubble">' + text + '</div>';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        async function send() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMessage(text, true);
            addMessage('Thinking...', false);
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            messages.lastChild.remove();
            addMessage(data.reply, false);
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
    print(f"Received: {user_msg}")
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "user", "content": user_msg}],
            max_tokens=300
        )
        reply = response['choices'][0]['message']['content']
        print(f"Replied: {reply[:50]}")
        return jsonify({'reply': reply})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'reply': f'Sorry, error: {str(e)}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
