import openai
from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

def clean_response(text):
    # Remove bold markdown
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    # Remove numbers from lists
    text = re.sub(r'\d+\.\s+', '- ', text)
    # Ensure bullet points use dash
    text = re.sub(r'^[\s]*[-*+]\s+', '- ', text, flags=re.MULTILINE)
    return text

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #1e3c72; margin: 0; padding: 20px; }
        .chat { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; height: 90vh; display: flex; flex-direction: column; }
        .header { background: #1e3c72; color: white; padding: 15px; text-align: center; border-radius: 10px 10px 0 0; }
        .messages { flex: 1; overflow-y: auto; padding: 20px; background: #f8f9fa; }
        .msg { margin-bottom: 15px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble { padding: 10px 15px; border-radius: 15px; max-width: 70%; line-height: 1.4; white-space: pre-wrap; }
        .user .bubble { background: #2a5298; color: white; }
        .bot .bubble { background: white; color: black; border: 1px solid #ddd; }
        .input-area { padding: 15px; display: flex; gap: 10px; border-top: 1px solid #ddd; background: white; }
        .input-area input { flex: 1; padding: 10px; border: 1px solid #ddd; border-radius: 20px; }
        .input-area button { padding: 10px 20px; background: #2a5298; color: white; border: none; border-radius: 20px; cursor: pointer; }
        .typing { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <h2>📦 PAS Freight AI Assistant</h2>
            <p>Logistics & Freight Support</p>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="bubble">Namaste! Welcome to PAS Freight. How can I help you today?</div>
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
            typing.innerHTML = '<div class="bubble typing">Thinking...</div>';
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
                addMessage('Sorry, error occurred. Please try again.', false);
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
    
    system_prompt = """You are PAS Freight customer service. Respond with clean bullet points using only dashes. No bold, no numbers, no asterisks.

Company info:
PAS Freight Services in Bangalore offers:
- Freight forwarding for air and sea shipments
- Customs clearance services
- Trucking and transportation
- Warehousing solutions
- International shipping
- Supply chain management

Contact: +91 9071660066 or +91 9164466664
Email: shivu@pasfreight.com
Address: Jakkur-BDA, Bangalore - 560092
Experience: Over 8 years
Members: WCA and GLA certified

Always respond with clean bullet points using dashes. Keep it professional and helpful."""
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=400,
            temperature=0.5
        )
        reply = response['choices'][0]['message']['content']
        reply = clean_response(reply)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': 'For assistance, please call +91 9071660066 or email shivu@pasfreight.com'})

if __name__ == '__main__':
    print('🚀 PAS Freight AI Running at http://localhost:5000')
    app.run(host='0.0.0.0', port=5000, debug=False)
