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
    <title>PAS Freight AI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .chat-box {
            max-width: 450px;
            width: 100%;
            height: 90vh;
            background: white;
            border-radius: 20px;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        }
        .header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 15px;
            text-align: center;
        }
        .header h1 { font-size: 18px; }
        .header p { font-size: 11px; margin-top: 3px; }
        .msgs {
            flex: 1;
            overflow-y: auto;
            padding: 15px;
            background: #f0f2f5;
        }
        .msg { margin-bottom: 12px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            max-width: 75%;
            padding: 10px 14px;
            border-radius: 18px;
            font-size: 13px;
        }
        .user .bubble { background: #2a5298; color: white; }
        .bot .bubble { background: white; color: #333; border: 1px solid #ddd; }
        .btns {
            padding: 12px;
            background: white;
            border-top: 1px solid #ddd;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .btn {
            flex: 1;
            min-width: 80px;
            padding: 10px;
            background: #1e3c72;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
        }
        .input-area {
            padding: 12px;
            background: white;
            border-top: 1px solid #ddd;
            display: flex;
            gap: 8px;
        }
        .input-area input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 13px;
            outline: none;
        }
        .input-area button {
            padding: 10px 18px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
        }
        .sub-btns { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }
        .sub-btn { padding: 6px 12px; background: #4a6a8a; color: white; border: none; border-radius: 15px; cursor: pointer; font-size: 11px; }
        .welcome-icon { font-size: 40px; text-align: center; margin-bottom: 5px; }
        .company-name { font-weight: bold; color: #1e3c72; }
    </style>
</head>
<body>
<div class="chat-box">
    <div class="header">
        <h1>📦 PAS Freight Services Pvt Ltd</h1>
        <p>24/7 Logistics Support | India's Leading Logistics Partner</p>
    </div>
    <div class="msgs" id="msgs">
        <div class="msg bot">
            <div class="bubble">
                <div class="welcome-icon">🚀</div>
                <strong>Namaste! Welcome to PAS Freight Services Pvt Ltd</strong><br><br>
                Your trusted logistics partner for:<br>
                ✈️ Air & Sea Freight | 📋 Customs Clearance | 🚚 Domestic Transport<br>
                🌍 International Shipping | 📮 Courier Services<br><br>
                <strong>How can I help you today?</strong><br><br>
                👇 Please select a service below or type your question.
            </div>
        </div>
    </div>
    <div class="btns">
        <button class="btn" id="importBtn">📦 Import</button>
        <button class="btn" id="exportBtn">🚢 Export</button>
        <button class="btn" id="customsBtn">📋 Customs</button>
        <button class="btn" id="domesticBtn">🚚 Domestic</button>
        <button class="btn" id="courierBtn">📮 Courier</button>
        <button class="btn" id="aboutBtn">🏢 About</button>
    </div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Type your question...">
        <button id="sendBtn">Send</button>
    </div>
</div>

<script>
let step = null;
let currentService = '';
let userName = '';
let userEmail = '';
let userPhone = '';

function addMsg(text, isUser) {
    const div = document.createElement('div');
    div.className = 'msg ' + (isUser ? 'user' : 'bot');
    div.innerHTML = '<div class="bubble">' + text + '</div>';
    document.getElementById('msgs').appendChild(div);
    div.scrollIntoView({ behavior: 'smooth' });
}

function showSubOptions(service) {
    let btns = '';
    if (service === 'import' || service === 'export') {
        btns = '<div class="sub-btns"><button class="sub-btn" data-mode="air">✈️ Air Freight</button><button class="sub-btn" data-mode="sea">🚢 Sea Freight</button></div>';
    } else if (service === 'domestic') {
        btns = '<div class="sub-btns"><button class="sub-btn" data-mode="full">🚛 Full Truck Load</button><button class="sub-btn" data-mode="less">📦 Less than Truck Load</button></div>';
    } else if (service === 'courier') {
        btns = '<div class="sub-btns"><button class="sub-btn" data-mode="domestic">🇮🇳 Domestic Courier</button><button class="sub-btn" data-mode="international">🌍 International Courier</button></div>';
    }
    
    const div = document.createElement('div');
    div.className = 'msg bot';
    div.innerHTML = '<div class="bubble">📌 Select option:' + btns + '</div>';
    document.getElementById('msgs').appendChild(div);
    div.scrollIntoView({ behavior: 'smooth' });
    
    document.querySelectorAll('.sub-btn').forEach(btn => {
        btn.onclick = function() {
            selectMode(this.getAttribute('data-mode'));
        };
    });
}

function showCustomsOptions() {
    const div = document.createElement('div');
    div.className = 'msg bot';
    div.innerHTML = '<div class="bubble">📋 <strong>Customs Clearance Service</strong><br><br>✅ Two ways to proceed:<br><br>📞 <strong>Call us directly:</strong> <a href="tel:+919611660204" style="color:#2a5298;">+91 96116 60204</a><br><br>📝 <strong>Share your details below</strong> - Our customs expert will call you back within 2 hours.<br><br>👇 Please share your name:</div>';
    document.getElementById('msgs').appendChild(div);
    div.scrollIntoView({ behavior: 'smooth' });
    
    step = 'name';
}

function selectService(service) {
    currentService = service;
    
    if (service === 'customs') {
        addMsg('I need help with CUSTOMS CLEARANCE', true);
        showCustomsOptions();
        return;
    }
    
    const names = { import:'IMPORT', export:'EXPORT', domestic:'DOMESTICS', courier:'COURIERS' };
    addMsg('I need help with ' + names[service] + ' service', true);
    showSubOptions(service);
}

function selectMode(mode) {
    addMsg(mode.toUpperCase() + ' service', true);
    step = 'name';
    addMsg('📝 Please share your full name:', false);
}

async function showAbout() {
    addMsg('Tell me about PAS Freight', true);
    const res = await fetch('/about');
    const data = await res.json();
    addMsg(data.info, false);
}

async function sendChat() {
    const input = document.getElementById('userInput');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    addMsg(text, true);
    
    if (step === 'name') {
        userName = text;
        step = 'email';
        addMsg('📧 What is your email address?', false);
        return;
    }
    
    if (step === 'email') {
        userEmail = text;
        step = 'phone';
        addMsg('📞 Your phone number? (type "skip" if not needed)', false);
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
            addMsg('✅ Thank you ' + userName + '! Our customs clearance expert will call you back shortly on ' + (userPhone !== 'skip' ? userPhone : 'your number') + '.', false);
            addMsg('📞 For urgent customs queries, please call +91 96116 60204 directly.', false);
        } else {
            addMsg('✅ Thank you ' + userName + '! Our team will contact you within 24 hours.', false);
            addMsg('📞 For immediate assistance, call +91 9071660066', false);
        }
        
        step = null;
        currentService = '';
        userName = userEmail = userPhone = '';
        return;
    }
    
    const typing = document.createElement('div');
    typing.className = 'msg bot';
    typing.id = 'typing';
    typing.innerHTML = '<div class="bubble">⏳ Thinking...</div>';
    document.getElementById('msgs').appendChild(typing);
    
    const res = await fetch('/chat', { 
        method: 'POST', 
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({message: text}) 
    });
    const data = await res.json();
    const typingDiv = document.getElementById('typing');
    if (typingDiv) typingDiv.remove();
    addMsg(data.reply, false);
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
    return jsonify({'info': '🏢 PAS Freight Services Pvt Ltd\n\n📍 Address: Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092\n\n📞 Contact: +91 9071660066, +91 9164466664\n📞 Customs: +91 96116 60204\n\n📧 Email: shivu@pasfreight.com\n\n✅ Certifications: WCA (115513), GLA (1166251)\n\n🌟 Experience: Over 8 years in logistics\n\n💼 Services: Import, Export, Customs, Domestics, Couriers, Air & Sea Freight\n\n🌍 Service Areas: Bangalore, Chennai, Delhi, Mumbai, Hyderabad, and International'})

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
    print("🚀 PAS Freight AI - PREMIUM VERSION")
    print("📱 Open: http://localhost:5001")
    print("📞 Customs: +91 96116 60204")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)
