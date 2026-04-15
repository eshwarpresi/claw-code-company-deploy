import openai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

# Simple HTML
HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI Test</title>
    <style>
        body { font-family: Arial; max-width: 800px; margin: 50px auto; padding: 20px; }
        .chat { border: 1px solid #ccc; height: 400px; overflow-y: auto; padding: 10px; margin-bottom: 10px; }
        .user { text-align: right; color: blue; margin: 10px; }
        .bot { text-align: left; color: green; margin: 10px; }
        input { width: 80%; padding: 10px; }
        button { padding: 10px 20px; }
    </style>
</head>
<body>
    <h2>PAS Freight AI Assistant</h2>
    <div class="chat" id="chat">
        <div class="bot">Hello! How can I help you with PAS Freight services?</div>
    </div>
    <input type="text" id="input" placeholder="Type your question...">
    <button onclick="send()">Send</button>

    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('input');
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = isUser ? 'user' : 'bot';
            div.textContent = text;
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
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
            chat.lastChild.remove();
            addMessage(data.reply, false);
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
            max_tokens=200
        )
        reply = response['choices'][0]['message']['content']
        print(f"Got reply: {reply[:50]}")  # Debug print
        return jsonify({'reply': reply})
    except Exception as e:
        error_msg = str(e)
        print(f"API ERROR: {error_msg}")
        return jsonify({'reply': f'Error: {error_msg[:200]}'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
