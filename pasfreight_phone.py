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
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: linear-gradient(135deg, #1e3c72, #2a5298); min-height: 100vh; display: flex; justify-content: center; align-items: center; padding: 20px; }
        .chat-box { max-width: 450px; width: 100%; height: 90vh; background: white; border-radius: 25px; display: flex; flex-direction: column; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.3); }
        .header { background: linear-gradient(135deg, #1e3c72, #2a5298); color: white; padding: 20px; text-align: center; }
        .header h1 { font-size: 18px; margin-bottom: 5px; }
        .header p { font-size: 10px; opacity: 0.9; margin-bottom: 8px; }
        .support-badge { display: inline-flex; align-items: center; gap: 6px; background: rgba(255,255,255,0.15); padding: 4px 12px; border-radius: 20px; font-size: 10px; margin-top: 5px; }
        .support-badge span { display: inline-block; width: 8px; height: 8px; background: #4ade80; border-radius: 50%; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .msgs { flex: 1; overflow-y: auto; padding: 20px; background: #f5f7fb; }
        .msg { margin-bottom: 15px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble { max-width: 75%; padding: 10px 15px; border-radius: 20px; font-size: 13px; line-height: 1.4; }
        .user .bubble { background: #2a5298; color: white; }
        .bot .bubble { background: white; color: #333; border: 1px solid #e0e0e0; }
        .btns { padding: 15px; background: white; border-top: 1px solid #eee; display: flex; flex-wrap: wrap; gap: 8px; }
        .btn { flex: 1; min-width: 85px; padding: 10px; background: #1e3c72; color: white; border: none; border-radius: 25px; cursor: pointer; font-size: 12px; font-weight: 500; }
        .btn:active { transform: scale(0.97); }
        .input-area { padding: 15px; background: white; border-top: 1px solid #eee; display: flex; gap: 10px; }
        .input-area input { flex: 1; padding: 10px 15px; border: 1px solid #ddd; border-radius: 25px; font-size: 13px; outline: none; }
        .input-area button { padding: 10px 20px; background: #2a5298; color: white; border: none; border-radius: 25px; cursor: pointer; font-weight: 500; }
        .sub-btns { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
        .sub-btn { padding: 6px 14px; background: #e9ecef; color: #333; border: none; border-radius: 20px; cursor: pointer; font-size: 11px; }
        .typing { background: white; padding: 10px 15px; border-radius: 20px; display: inline-flex; gap: 4px; }
        .typing span { width: 6px; height: 6px; background: #999; border-radius: 50%; animation: blink 1.4s infinite; }
        @keyframes blink { 0%, 60%, 100% { opacity: 0.3; } 30% { opacity: 1; } }
    </style>
</head>
<body>
<div class="chat-box">
    <div class="header">
        <h1>📦 PAS Freight Services Pvt Ltd</h1>
        <p>Logistics & Freight Solutions | Bangalore, India</p>
        <div class="support-badge"><span></span> 24/7 Customer Support | Immediate Assistance</div>
    </div>
    <div class="msgs" id="msgs">
        <div class="msg bot">
            <div class="bubble">🚀 Namaste! Welcome to PAS Freight Services Pvt Ltd.<br><br>I can help you with Import, Export, Customs Clearance, Domestics & Couriers.<br><br>👇 Select a service below to get started.</div>
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

function showOptions(service) {
    let html = '';
    if (service === 'import' || service === 'export') {
        html = '<div class="sub-btns"><button class="sub-btn" data-mode="air">✈️ Air Freight</button><button class="sub-btn" data-mode="sea">🚢 Sea Freight</button></div>';
    } else if (service === 'domestic') {
        html = '<div class="sub-btns"><button class="sub-btn" data-mode="full">🚛 Full Truck Load</button><button class="sub-btn" data-mode="less">📦 Less Truck Load</button></div>';
    } else if (service === 'courier') {
        html = '<div class="sub-btns"><button class="sub-btn" data-mode="domestic">🇮🇳 Domestic Courier</button><button class="sub-btn" data-mode="international">🌍 International Courier</button></div>';
    }
    
    const div = document.createElement('div');
    div.className = 'msg bot';
    div.innerHTML = '<div class="bubble">Select type:' + html + '</div>';
    document.getElementById('msgs').appendChild(div);
    div.scrollIntoView({ behavior: 'smooth' });
    
    document.querySelectorAll('.sub-btn').forEach(btn => {
        btn.onclick = function() { selectMode(this.getAttribute('data-mode')); };
    });
}

function showServiceContact(service, mode) {
    let phoneNumber = '';
    let serviceName = '';
    
    if (service === 'import' || service === 'export') {
        if (mode === 'air') {
            phoneNumber = '+91 93648 81371 / +91 90716 60066';
            serviceName = (service === 'import' ? 'IMPORT' : 'EXPORT') + ' (AIR FREIGHT)';
        } else if (mode === 'sea') {
            phoneNumber = '+91 63615 21413 / +91 90716 60066';
            serviceName = (service === 'import' ? 'IMPORT' : 'EXPORT') + ' (SEA FREIGHT)';
        }
    } else if (service === 'customs') {
        phoneNumber = '+91 63615 26664';
        serviceName = 'CUSTOMS CLEARANCE';
    } else if (service === 'domestic') {
        phoneNumber = '+91 96116 60204 / +91 90716 60066';
        serviceName = 'DOMESTICS';
    } else if (service === 'courier') {
        if (mode === 'domestic') {
            phoneNumber = '+91 96116 60204 / +91 90716 60066';
            serviceName = 'DOMESTIC COURIER';
        } else if (mode === 'international') {
            phoneNumber = '+91 96116 60204 / +91 90716 60066';
            serviceName = 'INTERNATIONAL COURIER';
        }
    }
    
    const div = document.createElement('div');
    div.className = 'msg bot';
    div.innerHTML = '<div class="bubble">📞 For ' + serviceName + ' service, please call us at <strong>' + phoneNumber + '</strong><br><br>📝 Or share your details below and we will call you back.</div>';
    document.getElementById('msgs').appendChild(div);
    div.scrollIntoView({ behavior: 'smooth' });
    step = 'name';
    addMsg('Please share your name:', false);
}

function selectService(service) {
    currentService = service;
    
    if (service === 'customs') {
        addMsg('I need CUSTOMS CLEARANCE service', true);
        showServiceContact('customs', '');
        return;
    }
    
    const names = { import:'IMPORT', export:'EXPORT', domestic:'DOMESTICS', courier:'COURIERS' };
    addMsg('I need ' + names[service] + ' service', true);
    showOptions(service);
}

function selectMode(mode) {
    addMsg(mode.toUpperCase() + ' service', true);
    showServiceContact(currentService, mode);
}

async function aboutCompany() {
    addMsg('Tell me about PAS Freight', true);
    const res = await fetch('/about');
    const data = await res.json();
    addMsg(data.info, false);
}

async function sendMsg() {
    const input = document.getElementById('userInput');
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    addMsg(text, true);
    
    if (step === 'name') {
        userName = text;
        step = 'email';
        addMsg('Your email address?', false);
        return;
    }
    
    if (step === 'email') {
        userEmail = text;
        step = 'phone';
        addMsg('Your phone number? (type "skip")', false);
        return;
    }
    
    if (step === 'phone') {
        if (text !== 'skip') userPhone = text;
        
        await fetch('/save_lead', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ service: currentService, name: userName, email: userEmail, phone: userPhone })
        });
        
        addMsg('Thanks ' + userName + '! Our team will call you back shortly.', false);
        addMsg('For immediate assistance, please call our support team.', false);
        
        step = null;
        currentService = '';
        userName = userEmail = userPhone = '';
        return;
    }
    
    const typing = document.createElement('div');
    typing.className = 'msg bot';
    typing.id = 'typing';
    typing.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
    document.getElementById('msgs').appendChild(typing);
    
    const res = await fetch('/chat', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({message: text}) });
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
document.getElementById('aboutBtn').onclick = () => aboutCompany();
document.getElementById('sendBtn').onclick = () => sendMsg();
document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMsg();
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
    info = '''🏢 <strong>PAS Freight Services Pvt Ltd</strong>

📍 <strong>Address:</strong> Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092

📞 <strong>Contact Numbers:</strong>
   • Import/Export (Air): +91 93648 81371 / +91 90716 60066
   • Import/Export (Sea): +91 63615 21413 / +91 90716 60066
   • Customs Clearance: +91 63615 26664
   • Domestic & Courier: +91 96116 60204 / +91 90716 60066

📧 <strong>Email:</strong> shivu@pasfreight.com

✅ <strong>Certifications:</strong> WCA (115513) | GLA (1166251)

🌟 <strong>Experience:</strong> Over 8 years in logistics

💼 <strong>Services:</strong> Import, Export, Customs Clearance, Domestics, Couriers, Air & Sea Freight, Warehousing

🌍 <strong>Service Areas:</strong> Bangalore, Chennai, Delhi, Mumbai, Hyderabad, and International

⏰ <strong>Support:</strong> 24/7 Customer Support

🎯 <strong>Vision:</strong> To be Bangalore's most trusted logistics partner

We provide end-to-end logistics solutions across India and internationally!'''
    return jsonify({'info': info})

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
            messages=[{"role": "system", "content": "You are PAS Freight assistant. Give short answers. Call our support numbers for rates."},
                      {"role": "user", "content": user_msg}],
            max_tokens=100
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except:
        return jsonify({'reply': 'Please call our support team for assistance.'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 PAS Freight AI - FINAL VERSION")
    print("📱 Open: http://localhost:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)
