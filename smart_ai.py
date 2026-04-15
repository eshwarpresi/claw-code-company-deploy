import openai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Your API key
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

# Test if API works
try:
    test = openai.ChatCompletion.create(
        model="openai/gpt-4o-mini",
        messages=[{"role": "user", "content": "Say OK"}],
        max_tokens=5
    )
    print("✅ API is WORKING!")
except Exception as e:
    print(f"❌ API Error: {e}")

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight Smart AI</title>
    <style>
        body { font-family: 'Segoe UI', Arial; background: #1e3c72; margin: 0; padding: 20px; }
        .chat { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; box-shadow: 0 5px 20px rgba(0,0,0,0.2); }
        .header { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }
        .header h2 { margin: 0; }
        .messages { height: 500px; overflow-y: auto; padding: 20px; background: #f8f9fa; }
        .msg { margin-bottom: 15px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble { padding: 10px 15px; border-radius: 18px; max-width: 70%; word-wrap: break-word; line-height: 1.4; }
        .user .bubble { background: #2a5298; color: white; }
        .bot .bubble { background: white; color: #333; border: 1px solid #ddd; }
        .input-area { padding: 20px; display: flex; gap: 10px; background: white; border-top: 1px solid #ddd; }
        .input-area input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; font-size: 14px; }
        .input-area button { padding: 12px 25px; background: #2a5298; color: white; border: none; border-radius: 25px; cursor: pointer; font-size: 14px; }
        .input-area button:hover { background: #1e3c72; }
        .typing { color: #999; font-style: italic; }
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <h2>📦 PAS Freight Smart AI Assistant</h2>
            <p>Logistics & Freight Solutions | Bangalore</p>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="bubble">Namaste! I'm your smart AI assistant for PAS Freight Services. I can help you with freight forwarding, customs clearance, shipping rates, and more. What would you like to know?</div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Ask me anything about logistics..." autocomplete="off">
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
            typing.innerHTML = '<div class="bubble typing">🤔 Thinking...</div>';
            messages.appendChild(typing);
            messages.scrollTop = messages.scrollHeight;
            
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
                addMessage('Sorry, I encountered an error. Please try again.', false);
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
    
    system_prompt = """You are a smart AI assistant for PAS Freight Services Pvt Ltd, a logistics company in Bangalore with 8+ years of experience.

Company Details:
- Services: Air freight, Sea freight, Customs clearance, Trucking, Warehousing, International shipping, Supply chain management
- Contact: +91 9071660066, +91 9164466664
- Email: shivu@pasfreight.com
- Address: Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092
- Certifications: WCA Member ID 115513, GLA Member ID 1166251

Response Guidelines:
- Answer naturally and conversationally like ChatGPT
- Be helpful, professional, and friendly
- Provide specific information about PAS Freight services
- For rates: explain they vary by weight, dimensions, and destination
- Always offer to connect with the team when appropriate

Answer the user's question intelligently and helpfully."""
    
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
        error_msg = str(e)
        print(f"✗ ERROR: {error_msg}")
        return jsonify({'reply': f"I apologize, but I'm having trouble connecting. Please contact PAS Freight directly at +91 9071660066 for immediate assistance with '{user_msg}'."})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 PAS Freight SMART AI Assistant")
    print("📱 Open: http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
