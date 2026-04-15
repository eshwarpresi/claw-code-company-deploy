import openai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
    <style>
        body { font-family: 'Segoe UI', Arial; background: #1e3c72; margin: 0; padding: 20px; }
        .chat { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.2); }
        .header { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .header h2 { margin: 0; }
        .header p { margin: 5px 0 0; opacity: 0.9; }
        .messages { height: 500px; overflow-y: auto; padding: 20px; background: #f8f9fa; }
        .msg { margin-bottom: 15px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble { padding: 10px 15px; border-radius: 18px; max-width: 70%; line-height: 1.4; }
        .user .bubble { background: #2a5298; color: white; }
        .bot .bubble { background: white; color: #333; border: 1px solid #ddd; }
        .input-area { padding: 20px; display: flex; gap: 10px; background: white; border-top: 1px solid #ddd; }
        .input-area input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; font-size: 14px; }
        .input-area button { padding: 12px 25px; background: #2a5298; color: white; border: none; border-radius: 25px; cursor: pointer; }
        .typing { color: #999; font-style: italic; }
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <h2>📦 PAS Freight Services Pvt Ltd</h2>
            <p>Logistics & Freight Solutions | Bangalore | WCA & GLA Certified</p>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="bubble">Namaste! 👋 I'm PAS Freight's AI Assistant. I can help you with freight forwarding, customs clearance, shipping rates, and more. What would you like to know?</div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Ask about our logistics services..." autocomplete="off">
            <button onclick="send()">Send</button>
        </div>
    </div>
    <script>
        const messages = document.getElementById('messages');
        const input = document.getElementById('input');
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            div.innerHTML = '<div class="bubble">' + text.replace(/\\n/g, '<br>') + '</div>';
            messages.appendChild(div);
            messages.scrollTop = messages.scrollHeight;
        }
        async function send() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMessage(text, true);
            const typing = document.createElement('div');
            typing.className = 'msg bot';
            typing.innerHTML = '<div class="bubble typing">Thinking...</div>';
            messages.appendChild(typing);
            messages.scrollTop = messages.scrollHeight;
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            typing.remove();
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
    
    system_prompt = """You are the official AI assistant for PAS Freight Services Pvt Ltd, a logistics company based in Bangalore, India with over 8 years of experience.

COMPANY INFORMATION:
- Services: Air freight, Sea freight, Customs clearance, Trucking, Warehousing, International shipping, Supply chain management
- Contact: +91 9071660066, +91 9164466664
- Email: shivu@pasfreight.com
- Address: Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092
- Certifications: WCA Member ID 115513, GLA Member ID 1166251
- Website: https://pasfreight.com

When answering:
- Be helpful, professional, and friendly
- Provide accurate information about PAS Freight's services
- For rates: explain they vary by weight, dimensions, and destination, and offer to connect with the team
- Always include contact information when appropriate
- Answer naturally like a helpful customer service representative

Answer the user's question about PAS Freight services professionally and helpfully."""

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=500,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        print(f"✓ Answered: {user_msg[:50]}")
        return jsonify({'reply': reply})
    except Exception as e:
        print(f"✗ Error: {e}")
        return jsonify({'reply': f'For assistance with "{user_msg}", please call +91 9071660066 or email shivu@pasfreight.com'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 PAS Freight Professional AI Assistant")
    print("📱 Open: http://localhost:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)
