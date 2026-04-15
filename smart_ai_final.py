import openai
from flask import Flask, request, jsonify, render_template_string
import base64
import io

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

# Company information
COMPANY_INFO = """
PAS Freight Services Pvt Ltd - Bangalore's Leading Logistics Provider

CONTACT NUMBERS:
- Import/Export (Air): +91 93648 81371 / +91 90716 60066
- Import/Export (Sea): +91 63615 21413 / +91 90716 60066
- Customs Clearance: +91 63615 26664
- Domestic & Courier: +91 96116 60204 / +91 90716 60066

SERVICES:
- Air Freight (Import/Export)
- Sea Freight (Import/Export)
- Customs Clearance
- Full Truck Load (FTL)
- Less than Truck Load (LTL)
- Domestic Courier
- International Courier
- Warehousing

ADDRESS: Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092
EMAIL: shivu@pasfreight.com
"""

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI - Smart Assistant</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            width: 100%;
            max-width: 450px;
            height: 100vh;
            background: white;
            display: flex;
            flex-direction: column;
            box-shadow: 0 0 30px rgba(0,0,0,0.2);
        }
        .header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h2 { font-size: 18px; }
        .header p { font-size: 11px; opacity: 0.9; margin-top: 3px; }
        .online-badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 10px;
            margin-top: 6px;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f5f7fb;
        }
        .msg { margin-bottom: 16px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 20px;
            font-size: 13px;
            line-height: 1.4;
        }
        .user .bubble { background: #2a5298; color: white; border-bottom-right-radius: 4px; }
        .bot .bubble { background: white; color: #333; border: 1px solid #ddd; border-bottom-left-radius: 4px; }
        .tools-bar {
            padding: 10px 16px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 15px;
        }
        .tool-btn {
            background: none;
            border: none;
            font-size: 22px;
            cursor: pointer;
            padding: 5px;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .tool-btn:hover { background: #f0f0f0; }
        .input-area {
            padding: 12px 16px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        .input-area button {
            background: #2a5298;
            color: white;
            border: none;
            width: 44px;
            height: 44px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
        }
        .quick-buttons {
            padding: 10px 16px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .quick-btn {
            background: #f0f2f5;
            border: none;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 11px;
            cursor: pointer;
        }
        .image-preview {
            max-width: 150px;
            max-height: 100px;
            border-radius: 10px;
            margin-top: 5px;
        }
        .voice-active {
            background: #ef4444 !important;
            animation: pulse 1s infinite;
        }
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        .typing {
            background: white;
            padding: 12px 16px;
            border-radius: 20px;
            display: inline-flex;
            gap: 4px;
        }
        .typing span {
            width: 6px;
            height: 6px;
            background: #999;
            border-radius: 50%;
            animation: blink 1.4s infinite;
        }
        @keyframes blink {
            0%, 60%, 100% { opacity: 0.3; }
            30% { opacity: 1; }
        }
    </style>
</head>
<body>
<div class="chat-container">
    <div class="header">
        <h2>📦 PAS Freight Services Pvt Ltd</h2>
        <p>Smart AI Assistant | Logistics Expert</p>
        <div class="online-badge">🟢 24/7 | Voice | Image | Files</div>
    </div>
    <div class="messages" id="messages">
        <div class="msg bot">
            <div class="bubble">🚀 Namaste! I'm PAS Freight Smart AI.<br><br>✅ For logistics questions - I give PAS Freight specific answers<br>✅ For general questions - I give smart answers<br><br>📞 Need rates? Call +91 9071660066<br><br>How can I help you today?</div>
        </div>
    </div>
    <div class="quick-buttons">
        <button class="quick-btn" onclick="sendQuick('What are your air freight charges to Dubai?')">✈️ Air Freight</button>
        <button class="quick-btn" onclick="sendQuick('Sea freight rates to Chennai?')">🚢 Sea Freight</button>
        <button class="quick-btn" onclick="sendQuick('Customs clearance process time?')">📋 Customs</button>
        <button class="quick-btn" onclick="sendQuick('Truck load charges within Bangalore?')">🚚 Domestic</button>
        <button class="quick-btn" onclick="sendQuick('Courier rates for documents?')">📮 Courier</button>
    </div>
    <div class="tools-bar">
        <button class="tool-btn" id="voiceBtn" title="Voice Input">🎤</button>
        <button class="tool-btn" id="imageBtn" title="Upload Screenshot">📷</button>
        <button class="tool-btn" id="fileBtn" title="Upload File">📎</button>
        <input type="file" id="imageInput" style="display:none" accept="image/*">
        <input type="file" id="fileInput" style="display:none" accept=".pdf,.txt,.doc">
    </div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Ask about logistics or anything...">
        <button id="sendBtn">➤</button>
    </div>
</div>

<script>
    let recognition = null;
    let isListening = false;
    
    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-IN';
        
        recognition.onresult = function(event) {
            const text = event.results[0][0].transcript;
            document.getElementById('userInput').value = text;
            document.getElementById('voiceBtn').classList.remove('voice-active');
            isListening = false;
            sendMessage();
        };
        
        recognition.onerror = function() {
            document.getElementById('voiceBtn').classList.remove('voice-active');
            isListening = false;
        };
        
        recognition.onend = function() {
            document.getElementById('voiceBtn').classList.remove('voice-active');
            isListening = false;
        };
    }
    
    document.getElementById('voiceBtn').onclick = function() {
        if (!recognition) {
            alert('Voice not supported. Please use Chrome browser.');
            return;
        }
        if (isListening) {
            recognition.stop();
        } else {
            recognition.start();
            this.classList.add('voice-active');
            isListening = true;
        }
    };
    
    document.getElementById('imageBtn').onclick = () => document.getElementById('imageInput').click();
    document.getElementById('imageInput').onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const div = document.createElement('div');
                div.className = 'msg user';
                div.innerHTML = '<div class="bubble">📷 Screenshot uploaded<br><img src="' + event.target.result + '" class="image-preview"></div>';
                document.getElementById('messages').appendChild(div);
                div.scrollIntoView({ behavior: 'smooth' });
                
                setTimeout(() => {
                    const botDiv = document.createElement('div');
                    botDiv.className = 'msg bot';
                    botDiv.innerHTML = '<div class="bubble">✅ Image received! Our team will analyze it.<br><br>📞 For immediate assistance: +91 9071660066</div>';
                    document.getElementById('messages').appendChild(botDiv);
                    botDiv.scrollIntoView({ behavior: 'smooth' });
                }, 500);
            };
            reader.readAsDataURL(file);
        }
        this.value = '';
    };
    
    document.getElementById('fileBtn').onclick = () => document.getElementById('fileInput').click();
    document.getElementById('fileInput').onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const div = document.createElement('div');
            div.className = 'msg user';
            div.innerHTML = '<div class="bubble">📎 File: ' + file.name + '</div>';
            document.getElementById('messages').appendChild(div);
            div.scrollIntoView({ behavior: 'smooth' });
            
            setTimeout(() => {
                const botDiv = document.createElement('div');
                botDiv.className = 'msg bot';
                botDiv.innerHTML = '<div class="bubble">✅ File received! Our team will review and get back to you.<br><br>📞 Urgent? Call +91 9071660066</div>';
                document.getElementById('messages').appendChild(botDiv);
                botDiv.scrollIntoView({ behavior: 'smooth' });
            }, 500);
        }
        this.value = '';
    };
    
    function addMessage(text, isUser) {
        const div = document.createElement('div');
        div.className = 'msg ' + (isUser ? 'user' : 'bot');
        div.innerHTML = '<div class="bubble">' + text + '</div>';
        document.getElementById('messages').appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }
    
    function showTyping() {
        const div = document.createElement('div');
        div.className = 'msg bot';
        div.id = 'typing';
        div.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
        document.getElementById('messages').appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }
    
    function hideTyping() {
        const t = document.getElementById('typing');
        if (t) t.remove();
    }
    
    async function sendMessage() {
        const input = document.getElementById('userInput');
        const text = input.value.trim();
        if (!text) return;
        input.value = '';
        addMessage(text, true);
        showTyping();
        
        const res = await fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: text})
        });
        const data = await res.json();
        hideTyping();
        addMessage(data.reply, false);
        
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(data.reply);
            utterance.lang = 'en-IN';
            utterance.rate = 0.9;
            window.speechSynthesis.speak(utterance);
        }
    }
    
    function sendQuick(text) {
        document.getElementById('userInput').value = text;
        sendMessage();
    }
    
    document.getElementById('sendBtn').onclick = sendMessage;
    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
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
    
    system_prompt = f"""You are PAS Freight Smart AI Assistant. 

COMPANY RULES:
1. If user asks about logistics, freight, shipping, customs, transport - answer with PAS FREIGHT SPECIFIC information below.
2. If user asks general questions (friends, love, weather, sports, news, etc.) - answer like a friendly AI assistant.
3. Keep answers SHORT (2-3 sentences max) and conversational.

PAS FREIGHT COMPANY INFO:
{COMPANY_INFO}

Response Examples:
- Q: "air freight to Dubai?" → A: "For air freight to Dubai, call +91 93648 81371 or +91 90716 60066. Rates depend on weight and dimensions."
- Q: "what is love?" → A: "Love is a beautiful emotion! But for logistics help, I'm your expert. Need a freight quote?"
- Q: "best friend meaning" → A: "A best friend is someone who stands by you. Speaking of standing by you, PAS Freight is here for all your shipping needs! Call +91 9071660066"

Always be helpful and friendly. For PAS Freight queries, give specific contact numbers."""

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=150,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': '📞 For PAS Freight services, call +91 9071660066 or email shivu@pasfreight.com'})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PAS Freight SMART AI Assistant")
    print("📱 Logistics specific + General smart answers")
    print("📱 Open: http://localhost:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
