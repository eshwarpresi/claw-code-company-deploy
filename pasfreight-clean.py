import openai
from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

# Your working OpenRouter API key
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

def clean_response(text):
    # Remove markdown bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    # Remove markdown code blocks
    text = re.sub(r'`[\s\S]*?`', '', text)
    text = re.sub(r'([^]+)', r'\1', text)
    # Remove markdown headers
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    # Convert bullet points to simple dashes
    text = re.sub(r'^\s*[-*+]\s+', '- ', text, flags=re.MULTILINE)
    # Remove numbered list formatting
    text = re.sub(r'^\s*\d+\.\s+', '- ', text, flags=re.MULTILINE)
    # Clean up extra spaces and newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

COMPANY_NAME = "PAS Freight Services Pvt Ltd"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
    <meta charset="UTF-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; background: #1e3c72; margin: 0; padding: 20px; }
        .chat { max-width: 800px; margin: 0 auto; background: white; border-radius: 10px; height: 90vh; display: flex; flex-direction: column; box-shadow: 0 10px 40px rgba(0,0,0,0.2); }
        .header { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 15px; text-align: center; border-radius: 10px 10px 0 0; }
        .header h2 { margin: 0; font-size: 20px; }
        .header p { margin: 5px 0 0; font-size: 12px; opacity: 0.9; }
        .messages { flex: 1; overflow-y: auto; padding: 20px; background: #f8f9fa; }
        .msg { margin-bottom: 15px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble { padding: 10px 15px; border-radius: 18px; max-width: 70%; line-height: 1.4; font-size: 14px; }
        .user .bubble { background: #2a5298; color: white; border-bottom-right-radius: 4px; }
        .bot .bubble { background: white; color: #333; border: 1px solid #dee2e6; border-bottom-left-radius: 4px; white-space: pre-wrap; }
        .input-area { padding: 15px; background: white; display: flex; gap: 10px; border-top: 1px solid #dee2e6; }
        .input-area input { flex: 1; padding: 10px; border: 1px solid #dee2e6; border-radius: 20px; font-size: 14px; outline: none; }
        .input-area input:focus { border-color: #2a5298; }
        .input-area button { padding: 10px 20px; background: #2a5298; color: white; border: none; border-radius: 20px; cursor: pointer; font-size: 14px; }
        .input-area button:hover { background: #1e3c72; }
        .typing { color: #6c757d; font-style: italic; }
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <h2>📦 PAS Freight AI Assistant</h2>
            <p>Logistics & Freight Support | Bangalore</p>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="bubble">Namaste! Welcome to PAS Freight Services. How can I help you with your logistics needs today?</div>
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
        
        function formatText(text) {
            return text.replace(/\\n/g, '<br>');
        }
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.innerHTML = formatText(text);
            div.appendChild(bubble);
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        async function send() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMessage(text, true);
            
            const typingDiv = document.createElement('div');
            typingDiv.className = 'msg bot';
            typingDiv.innerHTML = '<div class="bubble typing">Typing...</div>';
            messagesDiv.appendChild(typingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await res.json();
                typingDiv.remove();
                addMessage(data.reply, false);
            } catch(err) {
                typingDiv.remove();
                addMessage('Sorry, an error occurred. Please try again.', false);
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
    
    system_prompt = """You are PAS Freight Services AI Assistant. Provide clean, natural responses without any markdown formatting.

Company Information:
- Name: PAS Freight Services Pvt Ltd
- Location: Bangalore, India
- Experience: Over 8 years
- Services: Freight forwarding (Air and Sea), Customs clearance, Trucking and transportation, Warehousing, International shipping, Supply chain management
- Contact: +91 9071660066, +91 9164466664
- Email: shivu@pasfreight.com
- Address: Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092
- Memberships: WCA Member ID 115513, GLA Member ID 1166251

Response Guidelines:
- Use plain text only, no markdown, no asterisks, no bold, no italic
- Use simple bullet points with dashes or numbers
- Keep responses helpful, professional, and conversational
- For rates, explain they vary and offer to connect with team
- Always be courteous and solution-oriented

Provide clean, easy-to-read responses exactly like a helpful customer service agent would speak."""
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=500,
            temperature=0.5
        )
        reply = response['choices'][0]['message']['content']
        reply = clean_response(reply)
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'Thank you for your inquiry. For immediate assistance, please contact PAS Freight at +91 9071660066 or email shivu@pasfreight.com.'})

if __name__ == '__main__':
    print('=' * 50)
    print('🚀 PAS Freight AI Assistant (Clean Version)')
    print('📱 Open http://localhost:5000')
    print('=' * 50)
    app.run(host='0.0.0.0', port=5000, debug=False)
