import openai
from flask import Flask, request, jsonify, render_template_string
import base64
import io
import re

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

PAS_INFO = """
PAS FREIGHT SERVICES PVT LTD - Complete Company Profile

ABOUT: PAS Freight Services Pvt Ltd is a leading logistics provider in Bangalore with over 8 years of experience. We specialize in customs clearing and international freight transportation.

CONTACT:
- Main: +91 9071660066, +91 9164466664, +91 9036101201
- Air Freight: +91 93648 81371
- Sea Freight: +91 63615 21413
- Customs: +91 63615 26664
- Domestic/Courier: +91 96116 60204
- Email: shivu@pasfreight.com

ADDRESS: Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092

CERTIFICATIONS: WCA (ID:115513), GLA (ID:1166251)

SERVICES: Air Freight, Sea Freight, Customs Clearance, Trucking, Warehousing, International Shipping, Supply Chain Management

WHY CHOOSE US: 24/7 Support, Certified Team, Custom Solutions, Advanced Tracking, Industry Experts

VISION: To be Bangalore's most trusted logistics partner delivering innovative end-to-end solutions.
"""

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight - Pro AI Assistant</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            box-shadow: 0 0 40px rgba(0,0,0,0.2);
        }
        .header {
            background: linear-gradient(135deg, #0a2647, #1a3c5e);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 18px; }
        .header p { font-size: 10px; opacity: 0.9; margin-top: 4px; }
        .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 9px;
            margin-top: 6px;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f5f7fb;
        }
        .msg { margin-bottom: 16px; display: flex; animation: fadeIn 0.3s ease; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 22px;
            font-size: 14px;
            line-height: 1.45;
        }
        .user .bubble { background: #1a3c5e; color: white; border-bottom-right-radius: 4px; }
        .bot .bubble { background: white; color: #1a202c; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.05); }
        .quick-buttons {
            padding: 12px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .quick-btn {
            background: #f1f5f9;
            border: none;
            padding: 8px 14px;
            border-radius: 25px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
            font-weight: 500;
        }
        .quick-btn:hover { background: #1a3c5e; color: white; transform: scale(0.96); }
        .tools-bar {
            padding: 10px 16px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 20px;
            justify-content: space-around;
        }
        .tool-btn {
            background: none;
            border: none;
            font-size: 24px;
            cursor: pointer;
            padding: 8px;
            border-radius: 50%;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .tool-btn:hover { background: #f1f5f9; transform: scale(1.05); }
        .voice-active { background: #ef4444 !important; animation: pulse 1s infinite; }
        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.1); opacity: 0.8; }
        }
        .input-area {
            padding: 12px 16px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e2e8f0;
            border-radius: 30px;
            font-size: 14px;
            outline: none;
            transition: all 0.2s;
        }
        .input-area input:focus { border-color: #1a3c5e; box-shadow: 0 0 0 3px rgba(26,60,94,0.1); }
        .input-area button {
            background: #1a3c5e;
            color: white;
            border: none;
            width: 48px;
            height: 48px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
            transition: all 0.2s;
        }
        .input-area button:hover { background: #0f2b45; transform: scale(0.96); }
        .typing {
            background: white;
            padding: 10px 16px;
            border-radius: 20px;
            display: inline-flex;
            gap: 5px;
        }
        .typing span {
            width: 7px;
            height: 7px;
            background: #94a3b8;
            border-radius: 50%;
            animation: typingBounce 1.4s infinite;
        }
        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }
        .image-preview {
            max-width: 150px;
            max-height: 120px;
            border-radius: 12px;
            margin-top: 8px;
            cursor: pointer;
        }
        .footer {
            text-align: center;
            padding: 8px;
            font-size: 9px;
            color: #94a3b8;
            background: white;
            border-top: 1px solid #e2e8f0;
        }
    </style>
</head>
<body>
<div class="chat-container">
    <div class="header">
        <h1>📦 PAS Freight Services Pvt Ltd</h1>
        <p>Official AI Assistant | Logistics Expert</p>
        <div class="badge">🟢 WCA & GLA Certified | 24/7 Support</div>
    </div>
    <div class="messages" id="messages">
        <div class="msg bot">
            <div class="bubble">✨ <strong>Welcome to PAS Freight!</strong><br><br>I'm your intelligent logistics assistant. Here's what I can do:<br><br>📦 Answer any logistics questions<br>🎤 Listen to your voice commands<br>📷 Analyze screenshots & images<br>📎 Review your documents<br><br><strong>How can I help you today?</strong></div>
        </div>
    </div>
    <div class="quick-buttons">
        <button class="quick-btn" onclick="sendQuick('What services does PAS Freight offer?')">📦 Services</button>
        <button class="quick-btn" onclick="sendQuick('Give me contact numbers for PAS Freight')">📞 Contact</button>
        <button class="quick-btn" onclick="sendQuick('Where is PAS Freight office located?')">📍 Address</button>
        <button class="quick-btn" onclick="sendQuick('Tell me about customs clearance process')">📋 Customs</button>
        <button class="quick-btn" onclick="sendQuick('Air freight rates to Dubai')">✈️ Air Freight</button>
        <button class="quick-btn" onclick="sendQuick('Sea freight charges from Chennai')">🚢 Sea Freight</button>
    </div>
    <div class="tools-bar">
        <button class="tool-btn" id="voiceBtn" title="Voice Input">🎤</button>
        <button class="tool-btn" id="cameraBtn" title="Camera / Screenshot">📷</button>
        <button class="tool-btn" id="fileBtn" title="Upload Document">📎</button>
        <input type="file" id="cameraInput" style="display:none" accept="image/*" capture="environment">
        <input type="file" id="fileInput" style="display:none" accept=".pdf,.txt,.doc,.docx,.png,.jpg">
    </div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Ask me anything about logistics...">
        <button id="sendBtn">➤</button>
    </div>
    <div class="footer">PAS Freight | WCA:115513 | GLA:1166251 | 24/7 Support</div>
</div>

<script>
    let recognition = null;
    let isListening = false;
    
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
            sendMessage();
        };
        recognition.onerror = function() {
            document.getElementById('voiceBtn').classList.remove('voice-active');
            isListening = false;
            addMessage("🎤 Sorry, I couldn't hear you. Please try again or type your question.", false);
        };
        recognition.onend = function() {
            document.getElementById('voiceBtn').classList.remove('voice-active');
            isListening = false;
        };
    }
    
    document.getElementById('voiceBtn').onclick = function() {
        if (!recognition) {
            addMessage("🎤 Voice support requires Chrome browser. Please type your question.", false);
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
    
    // Camera/Screenshot
    document.getElementById('cameraBtn').onclick = () => document.getElementById('cameraInput').click();
    document.getElementById('cameraInput').onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(event) {
                const div = document.createElement('div');
                div.className = 'msg user';
                div.innerHTML = `<div class="bubble">📷 <strong>Image shared</strong><br><img src="${event.target.result}" class="image-preview" onclick="window.open(this.src)"></div>`;
                document.getElementById('messages').appendChild(div);
                div.scrollIntoView({ behavior: 'smooth' });
                
                setTimeout(() => {
                    addMessage("✅ Thanks for sharing! Our team will review your image. For immediate assistance, call +91 9071660066", false);
                }, 500);
            };
            reader.readAsDataURL(file);
        }
        this.value = '';
    };
    
    // File Upload
    document.getElementById('fileBtn').onclick = () => document.getElementById('fileInput').click();
    document.getElementById('fileInput').onchange = function(e) {
        const file = e.target.files[0];
        if (file) {
            addMessage(`📎 Attached: ${file.name}`, true);
            setTimeout(() => {
                addMessage(`✅ Received "${file.name}". Our team will analyze it and get back to you within 2 hours. For urgent help, call +91 9071660066`, false);
            }, 500);
        }
        this.value = '';
    };
    
    function addMessage(text, isUser) {
        const div = document.createElement('div');
        div.className = 'msg ' + (isUser ? 'user' : 'bot');
        div.innerHTML = '<div class="bubble">' + text.replace(/\\n/g, '<br>') + '</div>';
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
        
        // Text to speech
        if ('speechSynthesis' in window && !isUser) {
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
    
    system_prompt = f"""You are a friendly, professional AI assistant for PAS Freight Services Pvt Ltd.

YOUR PERSONALITY: Warm, helpful, enthusiastic, professional. Like a top-tier customer service representative.

ABOUT PAS FREIGHT (Use this information):
{PAS_INFO}

RESPONSE RULES:
1. Be conversational and engaging - use emojis occasionally
2. Give COMPLETE, HELPFUL answers with specific details
3. For services: List them with short descriptions
4. For contact: Give all relevant numbers
5. For rates: "Call +91 9071660066 for exact rates based on your shipment details"
6. ALWAYS sound helpful and solution-oriented

EXAMPLES OF GOOD RESPONSES:
- User: "What services do you offer?" 
  Reply: "We offer comprehensive logistics solutions! ✈️ Air Freight for urgent shipments, 🚢 Sea Freight for cost-effective bulk shipping, 📋 Customs Clearance to handle all documentation, 🚚 Trucking for door-to-door delivery, 🏭 Warehousing for storage, and 🌍 International Shipping. What specific service are you looking for?"

- User: "What's your contact number?"
  Reply: "You can reach us at 📞 +91 9071660066 or +91 9164466664. For air freight specifically, call +91 93648 81371. For sea freight, +91 63615 21413. Our customs team is at +91 63615 26664. We're available 24/7!"

- User: "Customs clearance process?"
  Reply: "Our customs team handles everything from documentation to duty calculation and clearance. We have 8+ years of expertise and WCA/GLA certifications. Call +91 63615 26664 for a free consultation about your shipment!"

Answer every question enthusiastically and professionally, focusing on PAS Freight's services and expertise."""

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=250,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': '📞 For immediate assistance with PAS Freight services, please call +91 9071660066 or email shivu@pasfreight.com. Our team is available 24/7!'})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PAS FREIGHT PRO AI ASSISTANT")
    print("📱 Voice | Camera | Files | Smart Responses")
    print("📱 Open: http://localhost:5001")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
