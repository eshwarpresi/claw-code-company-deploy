from flask import Flask, request, jsonify, render_template_string
import openai
import json
from datetime import datetime

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight - AI Assistant</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0f1419 0%, #1a2a3a 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        /* Main Container */
        .chat-container {
            max-width: 480px;
            width: 100%;
            height: 95vh;
            background: #ffffff;
            border-radius: 28px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            display: flex;
            flex-direction: column;
            overflow: hidden;
            position: relative;
        }

        /* Header */
        .chat-header {
            background: linear-gradient(135deg, #0a2647, #1a3c5e);
            color: white;
            padding: 20px 24px;
            text-align: center;
        }

        .logo {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            margin-bottom: 8px;
        }

        .logo-icon {
            font-size: 28px;
        }

        .logo-text {
            font-size: 20px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }

        .tagline {
            font-size: 11px;
            opacity: 0.8;
            margin-top: 4px;
        }

        .status-badge {
            display: inline-block;
            background: rgba(255,255,255,0.15);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 10px;
            margin-top: 8px;
        }

        /* Messages Area */
        .messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8fafc;
        }

        /* Custom Scrollbar */
        .messages-area::-webkit-scrollbar {
            width: 4px;
        }
        .messages-area::-webkit-scrollbar-track {
            background: #e2e8f0;
        }
        .messages-area::-webkit-scrollbar-thumb {
            background: #94a3b8;
            border-radius: 4px;
        }

        /* Message Bubbles */
        .message {
            margin-bottom: 16px;
            display: flex;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user-message {
            justify-content: flex-end;
        }

        .bot-message {
            justify-content: flex-start;
        }

        .bubble {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 20px;
            font-size: 13px;
            line-height: 1.5;
            word-wrap: break-word;
        }

        .user-message .bubble {
            background: #1a3c5e;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .bot-message .bubble {
            background: white;
            color: #1e293b;
            border: 1px solid #e2e8f0;
            border-bottom-left-radius: 4px;
            box-shadow: 0 1px 2px rgba(0,0,0,0.03);
        }

        /* Quick Action Buttons */
        .quick-actions {
            padding: 16px 20px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }

        .action-btn {
            flex: 1;
            min-width: 90px;
            padding: 10px 12px;
            background: #f1f5f9;
            border: none;
            border-radius: 40px;
            font-size: 12px;
            font-weight: 500;
            color: #1e293b;
            cursor: pointer;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }

        .action-btn:hover {
            background: #1a3c5e;
            color: white;
            transform: translateY(-1px);
        }

        /* Input Area */
        .input-area {
            padding: 16px 20px;
            background: white;
            border-top: 1px solid #e2e8f0;
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e2e8f0;
            border-radius: 30px;
            font-size: 13px;
            outline: none;
            transition: all 0.2s ease;
            font-family: inherit;
        }

        .input-area input:focus {
            border-color: #1a3c5e;
            box-shadow: 0 0 0 3px rgba(26,60,94,0.1);
        }

        .input-area button {
            padding: 10px 20px;
            background: #1a3c5e;
            color: white;
            border: none;
            border-radius: 30px;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .input-area button:hover {
            background: #0f2b45;
            transform: scale(0.98);
        }

        /* Sub Buttons */
        .sub-buttons {
            display: flex;
            gap: 8px;
            margin-top: 10px;
            flex-wrap: wrap;
        }

        .sub-btn {
            padding: 6px 14px;
            background: #e2e8f0;
            color: #1e293b;
            border: none;
            border-radius: 30px;
            cursor: pointer;
            font-size: 11px;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        .sub-btn:hover {
            background: #cbd5e1;
            transform: translateY(-1px);
        }

        /* Typing Indicator */
        .typing-indicator {
            display: inline-flex;
            gap: 4px;
            padding: 4px 0;
        }
        .typing-indicator span {
            width: 6px;
            height: 6px;
            background: #94a3b8;
            border-radius: 50%;
            animation: pulse 1.4s infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes pulse {
            0%, 60%, 100% { transform: scale(1); opacity: 0.5; }
            30% { transform: scale(1.2); opacity: 1; }
        }

        /* Welcome Message Styling */
        .welcome-title {
            font-size: 16px;
            font-weight: 700;
            color: #0a2647;
            margin-bottom: 8px;
        }
        .welcome-text {
            font-size: 13px;
            color: #475569;
            line-height: 1.5;
        }
        .service-list {
            margin: 10px 0;
            padding-left: 20px;
        }
        .service-list li {
            margin: 5px 0;
            color: #334155;
        }
    </style>
</head>
<body>
<div class="chat-container">
    <div class="chat-header">
        <div class="logo">
            <span class="logo-icon">📦</span>
            <span class="logo-text">PAS Freight</span>
        </div>
        <div class="tagline">Logistics & Freight Solutions</div>
        <div class="status-badge">🟢 Online 24/7</div>
    </div>

    <div class="messages-area" id="messagesArea">
        <div class="message bot-message">
            <div class="bubble">
                <div class="welcome-title">✨ Welcome to PAS Freight Services</div>
                <div class="welcome-text">
                    India's trusted logistics partner since 2016.<br><br>
                    <strong>Our Services:</strong>
                    <ul class="service-list">
                        <li>✈️ International & Domestic Freight</li>
                        <li>📋 Customs Clearance</li>
                        <li>🚚 Full Truck Load / Less than Truck Load</li>
                        <li>📮 Courier Services</li>
                        <li>🏭 Warehousing & Distribution</li>
                    </ul>
                    <strong>How can I help you today?</strong>
                </div>
            </div>
        </div>
    </div>

    <div class="quick-actions">
        <button class="action-btn" id="importBtn">📦 Import</button>
        <button class="action-btn" id="exportBtn">🚢 Export</button>
        <button class="action-btn" id="customsBtn">📋 Customs</button>
        <button class="action-btn" id="domesticBtn">🚚 Domestic</button>
        <button class="action-btn" id="courierBtn">📮 Courier</button>
        <button class="action-btn" id="aboutBtn">🏢 About</button>
    </div>

    <div class="input-area">
        <input type="text" id="userInput" placeholder="Ask anything about logistics...">
        <button id="sendBtn">Send</button>
    </div>
</div>

<script>
let step = null;
let currentService = '';
let userName = '';
let userEmail = '';
let userPhone = '';

const messagesArea = document.getElementById('messagesArea');

function addMessage(text, isUser) {
    const div = document.createElement('div');
    div.className = message ;
    div.innerHTML = <div class="bubble"></div>;
    messagesArea.appendChild(div);
    div.scrollIntoView({ behavior: 'smooth' });
}

function showSubOptions(service) {
    let html = '';
    if (service === 'import' || service === 'export') {
        html = '<div class="sub-buttons"><button class="sub-btn" data-mode="air">✈️ Air Freight</button><button class="sub-btn" data-mode="sea">🚢 Sea Freight</button></div>';
    } else if (service === 'domestic') {
        html = '<div class="sub-buttons"><button class="sub-btn" data-mode="full">🚛 Full Truck Load</button><button class="sub-btn" data-mode="less">📦 Less than Truck Load</button></div>';
    } else if (service === 'courier') {
        html = '<div class="sub-buttons"><button class="sub-btn" data-mode="domestic">🇮🇳 Domestic</button><button class="sub-btn" data-mode="international">🌍 International</button></div>';
    }
    
    const div = document.createElement('div');
    div.className = 'message bot-message';
    div.innerHTML = <div class="bubble">Please select:</div>;
    messagesArea.appendChild(div);
    div.scrollIntoView({ behavior: 'smooth' });
    
    document.querySelectorAll('.sub-btn').forEach(btn => {
        btn.onclick = function() { selectMode(this.getAttribute('data-mode')); };
    });
}

function showCustomsOptions() {
    const div = document.createElement('div');
    div.className = 'message bot-message';
    div.innerHTML = <div class="bubble"><strong>📋 Customs Clearance</strong><br><br>Two ways to proceed:<br><br>📞 <strong>Call directly:</strong> <span style="color:#1a3c5e;font-weight:bold;">+91 96116 60204</span><br><br>📝 <strong>Share your details</strong> - Our expert will call you back.<br><br>👇 Please share your name:</div>;
    messagesArea.appendChild(div);
    div.scrollIntoView({ behavior: 'smooth' });
    step = 'name';
}

function selectService(service) {
    currentService = service;
    const names = { import:'IMPORT', export:'EXPORT', domestic:'DOMESTICS', courier:'COURIERS' };
    
    if (service === 'customs') {
        addMessage('I need help with CUSTOMS CLEARANCE', true);
        showCustomsOptions();
        return;
    }
    
    addMessage(I need help with  service, true);
    showSubOptions(service);
}

function selectMode(mode) {
    addMessage(${mode.toUpperCase()} service, true);
    step = 'name';
    addMessage('Please share your full name:', false);
}

async function showAbout() {
    addMessage('Tell me about PAS Freight', true);
    const res = await fetch('/about');
    const data = await res.json();
    addMessage(data.info, false);
}

async function sendChat() {
    const input = document.getElementById('userInput');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    addMessage(text, true);
    
    if (step === 'name') {
        userName = text;
        step = 'email';
        addMessage('What is your email address?', false);
        return;
    }
    
    if (step === 'email') {
        userEmail = text;
        step = 'phone';
        addMessage('Your phone number? (type "skip")', false);
        return;
    }
    
    if (step === 'phone') {
        if (text.toLowerCase() !== 'skip') userPhone = text;
        
        await fetch('/save_lead', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ service: currentService, name: userName, email: userEmail, phone: userPhone })
        });
        
        if (currentService === 'customs') {
            addMessage(Thank you ! Our customs team will call you back shortly., false);
            addMessage(For urgent queries: +91 96116 60204, false);
        } else {
            addMessage(Thank you ! Our team will contact you within 24 hours., false);
            addMessage(For immediate help: +91 9071660066, false);
        }
        
        step = null;
        currentService = '';
        userName = userEmail = userPhone = '';
        return;
    }
    
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typingMsg';
    typingDiv.innerHTML = '<div class="bubble"><div class="typing-indicator"><span></span><span></span><span></span></div></div>';
    messagesArea.appendChild(typingDiv);
    typingDiv.scrollIntoView({ behavior: 'smooth' });
    
    const res = await fetch('/chat', { 
        method: 'POST', 
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({message: text}) 
    });
    const data = await res.json();
    const typingElement = document.getElementById('typingMsg');
    if (typingElement) typingElement.remove();
    addMessage(data.reply, false);
}

document.getElementById('importBtn').onclick = () => selectService('import');
document.getElementById('exportBtn').onclick = () => selectService('export');
document.getElementById('customsBtn').onclick = () => selectService('customs');
document.getElementById('domesticBtn').onclick = () => selectService('domestic');
document.getElementById('courierBtn').onclick = () => selectService('courier');
document.getElementById('aboutBtn').onclick = showAbout;
document.getElementById('sendBtn').onclick = sendChat;
document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendChat();
});
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/about')
def about():
    return jsonify({'info': '🏢 <strong>PAS Freight Services Pvt Ltd</strong><br><br>📍 <strong>Address:</strong> Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092<br><br>📞 <strong>Contact:</strong> +91 9071660066, +91 9164466664<br>📞 <strong>Customs:</strong> +91 96116 60204<br><br>📧 <strong>Email:</strong> shivu@pasfreight.com<br><br>✅ <strong>Certifications:</strong> WCA (115513), GLA (1166251)<br><br>🌟 <strong>Experience:</strong> Over 8 years<br><br>💼 <strong>Services:</strong> Import, Export, Customs, Domestics, Couriers, Air & Sea Freight'})

@app.route('/save_lead', methods=['POST'])
def save_lead():
    data = request.get_json()
    with open('leads.json', 'a') as f:
        f.write(json.dumps(data) + '\n')
    print(f"LEAD: {data.get('name')} - {data.get('service')}")
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[{"role": "system", "content": "You are PAS Freight assistant. Give short, helpful answers. Call +91 9071660066 for rates."},
                      {"role": "user", "content": user_msg}],
            max_tokens=100
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except:
        return jsonify({'reply': 'Call +91 9071660066 for assistance'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 PAS Freight AI - PROFESSIONAL UI")
    print("📱 Open: http://localhost:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)
