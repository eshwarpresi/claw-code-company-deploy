import openai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

PAS_INFO = """
PAS FREIGHT SERVICES PVT LTD

CONTACT:
- Main: +91 9071660066, +91 9164466664
- Air Freight: +91 93648 81371
- Sea Freight: +91 63615 21413
- Customs: +91 63615 26664
- Domestic/Courier: +91 96116 60204
- Email: shivu@pasfreight.com

ADDRESS: Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092

CERTIFICATIONS: WCA (ID:115513), GLA (ID:1166251)

SERVICES: Air Freight, Sea Freight, Customs Clearance, Trucking, Warehousing, International Shipping
"""

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #343541;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .chat-container {
            width: 100%;
            max-width: 800px;
            height: 100vh;
            background: #343541;
            display: flex;
            flex-direction: column;
        }
        .header {
            background: #202123;
            color: #ececec;
            padding: 12px 20px;
            text-align: center;
            border-bottom: 1px solid #4a4b53;
        }
        .header h1 { font-size: 16px; font-weight: 500; }
        .header p { font-size: 11px; opacity: 0.7; margin-top: 3px; }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .msg {
            margin-bottom: 20px;
            display: flex;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 16px;
            flex-shrink: 0;
        }
        .bot-avatar { background: #10a37f; color: white; margin-right: 12px; }
        .user-avatar { background: #5436da; color: white; margin-left: 12px; order: 2; }
        .bubble {
            max-width: 80%;
            padding: 10px 16px;
            border-radius: 20px;
            font-size: 14px;
            line-height: 1.5;
        }
        .user .bubble { background: #5436da; color: white; border-bottom-right-radius: 4px; }
        .bot .bubble { background: #444654; color: #ececec; border-bottom-left-radius: 4px; }
        .msg-actions {
            display: none;
            gap: 6px;
            align-items: center;
            margin-left: 8px;
        }
        .msg:hover .msg-actions { display: flex; }
        .action-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 14px;
            padding: 4px;
            border-radius: 6px;
            color: #8e8ea0;
        }
        .action-btn:hover { background: #40414f; color: white; }
        .edit-input {
            width: 100%;
            padding: 8px 12px;
            background: #40414f;
            border: 1px solid #565869;
            border-radius: 12px;
            color: white;
            font-size: 14px;
            outline: none;
        }
        .edit-buttons { display: flex; gap: 8px; margin-top: 8px; }
        .save-edit { background: #10a37f; color: white; border: none; padding: 4px 12px; border-radius: 15px; cursor: pointer; }
        .cancel-edit { background: #565869; color: white; border: none; padding: 4px 12px; border-radius: 15px; cursor: pointer; }
        .input-container {
            padding: 16px 20px;
            background: #40414f;
            border-top: 1px solid #4a4b53;
        }
        .input-wrapper {
            display: flex;
            gap: 12px;
            align-items: center;
            background: #40414f;
            border: 1px solid #565869;
            border-radius: 28px;
            padding: 6px 8px 6px 18px;
        }
        .input-wrapper input {
            flex: 1;
            background: none;
            border: none;
            color: white;
            font-size: 14px;
            outline: none;
        }
        .input-wrapper input::placeholder { color: #8e8ea0; }
        .tool-btn {
            background: none;
            border: none;
            cursor: pointer;
            font-size: 20px;
            padding: 6px;
            border-radius: 50%;
            color: #8e8ea0;
            width: 36px;
            height: 36px;
        }
        .tool-btn:hover { background: #565869; color: white; }
        .send-btn { background: #10a37f; color: white; border-radius: 50%; }
        .send-btn:hover { background: #1a7f64; }
        .voice-active { background: #ef4444 !important; color: white !important; animation: pulse 1s infinite; }
        @keyframes pulse { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.1); } }
        .typing { display: inline-flex; gap: 4px; padding: 4px 0; }
        .typing span { width: 6px; height: 6px; background: #8e8ea0; border-radius: 50%; animation: bounce 1.4s infinite; }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes bounce { 0%, 60%, 100% { transform: translateY(0); } 30% { transform: translateY(-6px); } }
        .quick-buttons {
            padding: 12px 20px;
            background: #343541;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            border-bottom: 1px solid #4a4b53;
        }
        .quick-btn {
            background: #40414f;
            border: 1px solid #565869;
            padding: 6px 14px;
            border-radius: 20px;
            font-size: 12px;
            cursor: pointer;
            color: #ececec;
        }
        .quick-btn:hover { background: #565869; }
        .footer {
            text-align: center;
            padding: 8px;
            font-size: 10px;
            color: #565869;
            background: #343541;
        }
        .messages::-webkit-scrollbar { width: 6px; }
        .messages::-webkit-scrollbar-track { background: #40414f; }
        .messages::-webkit-scrollbar-thumb { background: #565869; border-radius: 3px; }
    </style>
</head>
<body>
<div class="chat-container">
    <div class="header">
        <h1>📦 PAS Freight Services Pvt Ltd</h1>
        <p>WCA & GLA Certified | 24/7 Support</p>
    </div>

    <div class="messages" id="messages">
        <div class="msg bot">
            <div class="avatar bot-avatar">🤖</div>
            <div class="bubble">✨ Welcome to PAS Freight! I'm your AI assistant. I can help with air/sea freight, customs clearance, domestic transport, and courier services. How can I help you today?</div>
        </div>
    </div>

    <div class="quick-buttons">
        <button class="quick-btn" onclick="sendQuick('What services do you offer?')">📦 Services</button>
        <button class="quick-btn" onclick="sendQuick('Contact numbers')">📞 Contact</button>
        <button class="quick-btn" onclick="sendQuick('Office address')">📍 Address</button>
        <button class="quick-btn" onclick="sendQuick('Customs clearance process')">📋 Customs</button>
        <button class="quick-btn" onclick="sendQuick('Air freight to Dubai')">✈️ Air</button>
        <button class="quick-btn" onclick="sendQuick('Sea freight rates')">🚢 Sea</button>
    </div>

    <div class="input-container">
        <div class="input-wrapper">
            <input type="text" id="userInput" placeholder="Ask me anything about logistics...">
            <button class="tool-btn" id="voiceBtn" title="Voice Input (Speak)">🎤</button>
            <button class="tool-btn send-btn" id="sendBtn">➤</button>
        </div>
    </div>
    <div class="footer">PAS Freight | 24/7 Support | +91 9071660066</div>
</div>

<script>
    let recognition = null;
    let isListening = false;
    let isVoiceMode = false; // Track if current request came from voice
    
    // Voice Recognition
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
            isVoiceMode = true; // Set voice mode flag
            sendMessage();
        };
        
        recognition.onerror = function() {
            document.getElementById('voiceBtn').classList.remove('voice-active');
            isListening = false;
            addMessage("🎤 Sorry, couldn't hear you. Please type your question.", false);
        };
        
        recognition.onend = function() {
            document.getElementById('voiceBtn').classList.remove('voice-active');
            isListening = false;
        };
    }
    
    document.getElementById('voiceBtn').onclick = function() {
        if (!recognition) {
            addMessage("🎤 Voice support requires Chrome browser.", false);
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
    
    function addMessage(text, isUser) {
        const div = document.createElement('div');
        div.className = 'msg ' + (isUser ? 'user' : 'bot');
        const msgId = 'msg_' + Date.now() + '_' + Math.random();
        div.setAttribute('data-msg-id', msgId);
        
        if (isUser) {
            div.innerHTML = `<div class="avatar user-avatar">👤</div>
                            <div class="bubble" id="bubble-${msgId}">${text}</div>
                            <div class="msg-actions">
                                <button class="action-btn" onclick="editMessage(this)">✏️</button>
                                <button class="action-btn" onclick="copyMessage(this)">📋</button>
                                <button class="action-btn" onclick="deleteMessage(this)">🗑️</button>
                            </div>`;
        } else {
            div.innerHTML = `<div class="avatar bot-avatar">🤖</div>
                            <div class="bubble" id="bubble-${msgId}">${text}</div>
                            <div class="msg-actions">
                                <button class="action-btn" onclick="copyMessage(this)">📋</button>
                                <button class="action-btn" onclick="regenerateMessage(this)">🔄</button>
                                <button class="action-btn" onclick="deleteMessage(this)">🗑️</button>
                            </div>`;
        }
        
        document.getElementById('messages').appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
        return msgId;
    }
    
    function editMessage(btn) {
        const msgDiv = btn.closest('.msg');
        const bubble = msgDiv.querySelector('.bubble');
        const originalText = bubble.innerText;
        const msgId = msgDiv.getAttribute('data-msg-id');
        
        bubble.innerHTML = `<textarea class="edit-input" id="edit-${msgId}" rows="2">${originalText}</textarea>
                           <div class="edit-buttons">
                               <button class="save-edit" onclick="saveEdit('${msgId}')">Save</button>
                               <button class="cancel-edit" onclick="cancelEdit('${msgId}', '${originalText.replace(/'/g, "\\'")}')">Cancel</button>
                           </div>`;
    }
    
    function saveEdit(msgId) {
        const newText = document.getElementById(`edit-${msgId}`).value;
        const msgDiv = document.querySelector(`[data-msg-id="${msgId}"]`);
        const bubble = msgDiv.querySelector('.bubble');
        bubble.innerHTML = newText;
        
        showTyping();
        fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: newText})
        }).then(res => res.json()).then(data => {
            hideTyping();
            addMessage(data.reply, false);
        });
    }
    
    function cancelEdit(msgId, originalText) {
        const msgDiv = document.querySelector(`[data-msg-id="${msgId}"]`);
        const bubble = msgDiv.querySelector('.bubble');
        bubble.innerHTML = originalText;
    }
    
    function copyMessage(btn) {
        const msgDiv = btn.closest('.msg');
        const text = msgDiv.querySelector('.bubble').innerText;
        navigator.clipboard.writeText(text);
        btn.innerHTML = '✅';
        setTimeout(() => { btn.innerHTML = '📋'; }, 1000);
    }
    
    function deleteMessage(btn) {
        const msgDiv = btn.closest('.msg');
        msgDiv.remove();
    }
    
    async function regenerateMessage(btn) {
        const msgDiv = btn.closest('.msg');
        const previousMsg = msgDiv.previousElementSibling;
        if (previousMsg && previousMsg.classList.contains('user')) {
            const userText = previousMsg.querySelector('.bubble').innerText;
            msgDiv.remove();
            showTyping();
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: userText})
            });
            const data = await res.json();
            hideTyping();
            addMessage(data.reply, false);
        }
    }
    
    function showTyping() {
        const div = document.createElement('div');
        div.className = 'msg bot';
        div.id = 'typing';
        div.innerHTML = `<div class="avatar bot-avatar">🤖</div><div class="typing"><span></span><span></span><span></span></div>`;
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
        
        // ONLY speak if this was triggered by voice (isVoiceMode = true)
        if (isVoiceMode && 'speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(data.reply);
            utterance.lang = 'en-IN';
            utterance.rate = 0.9;
            window.speechSynthesis.speak(utterance);
            isVoiceMode = false; // Reset flag after speaking
        }
    }
    
    function sendQuick(text) {
        document.getElementById('userInput').value = text;
        isVoiceMode = false; // Quick buttons don't trigger voice
        sendMessage();
    }
    
    document.getElementById('sendBtn').onclick = () => {
        isVoiceMode = false;
        sendMessage();
    };
    document.getElementById('userInput').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            isVoiceMode = false;
            sendMessage();
        }
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
    
    system_prompt = f"""You are PAS Freight AI assistant. Use this company info:
{PAS_INFO}

IMPORTANT: If user asks about non-logistics topics (sports, weather, movies, etc.), politely redirect them to PAS Freight services.

Be friendly, helpful, and concise. Answer logistics questions professionally."""

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=200,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': '📞 Call +91 9071660066 for immediate assistance with PAS Freight services.'})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PAS Freight AI - Fixed Voice Output")
    print("📱 Voice output ONLY when you click mic and speak")
    print("📱 Text input = Text response only (no voice)")
    print("📱 Open: http://localhost:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
