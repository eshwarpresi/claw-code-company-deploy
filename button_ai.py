import openai
from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight Services - AI Assistant</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .chat-container {
            max-width: 500px;
            width: 100%;
            height: 90vh;
            background: white;
            border-radius: 25px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 20px; }
        .header p { font-size: 11px; opacity: 0.9; margin-top: 5px; }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .msg { margin-bottom: 16px; display: flex; }
        .user { justify-content: flex-end; }
        .bot { justify-content: flex-start; }
        .bubble {
            padding: 10px 16px;
            border-radius: 20px;
            max-width: 85%;
            font-size: 14px;
            line-height: 1.4;
        }
        .user .bubble { background: #2a5298; color: white; border-bottom-right-radius: 4px; }
        .bot .bubble { background: white; color: #333; border: 1px solid #e0e0e0; border-bottom-left-radius: 4px; }
        .button-area {
            padding: 15px;
            background: white;
            border-top: 1px solid #e5e5e5;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }
        .service-btn {
            padding: 10px 16px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            flex: 1;
            min-width: 100px;
        }
        .service-btn:hover { background: #1e3c72; }
        .input-area {
            padding: 15px;
            background: white;
            display: flex;
            gap: 10px;
            border-top: 1px solid #e5e5e5;
        }
        .input-area input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        .input-area input:focus { border-color: #2a5298; }
        .input-area button {
            padding: 10px 20px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
        }
        .typing { color: #999; font-style: italic; }
        .sub-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }
        .sub-btn {
            padding: 8px 15px;
            background: #4a6a8a;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .msg { animation: fadeIn 0.3s ease; }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="header">
            <h1>📦 PAS Freight Services Pvt Ltd</h1>
            <p>Select a service to get started | 24/7 Support</p>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="bubble">👋 Welcome to PAS Freight! Please select a service below to get started.</div>
            </div>
        </div>
        <div class="button-area">
            <button class="service-btn" onclick="selectService('import')">📦 Import</button>
            <button class="service-btn" onclick="selectService('export')">🚢 Export</button>
            <button class="service-btn" onclick="selectService('customs')">📋 Customs Clearance</button>
            <button class="service-btn" onclick="selectService('domestic')">🚚 Domestics</button>
            <button class="service-btn" onclick="selectService('courier')">📮 Couriers</button>
            <button class="service-btn" onclick="selectService('about')">🏢 About Us</button>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Or type your question..." autocomplete="off">
            <button onclick="sendText()">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('input');
        let currentService = null;
        let subStep = null;
        let userData = { name: '', email: '', phone: '' };
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            div.innerHTML = '<div class="bubble">' + text.replace(/\\n/g, '<br>') + '</div>';
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function addSubButtons(service) {
            const div = document.createElement('div');
            div.className = 'msg bot';
            div.id = 'sub-buttons';
            
            if (service === 'import') {
                div.innerHTML = '<div class="bubble">Select mode:<div class="sub-buttons"><button class="sub-btn" onclick="selectMode(\\'air\\')">✈️ Air Freight</button><button class="sub-btn" onclick="selectMode(\\'sea\\')">🚢 Sea Freight</button></div></div>';
            } else if (service === 'export') {
                div.innerHTML = '<div class="bubble">Select mode:<div class="sub-buttons"><button class="sub-btn" onclick="selectMode(\\'air\\')">✈️ Air Freight</button><button class="sub-btn" onclick="selectMode(\\'sea\\')">🚢 Sea Freight</button></div></div>';
            } else if (service === 'domestic') {
                div.innerHTML = '<div class="bubble">Select type:<div class="sub-buttons"><button class="sub-btn" onclick="selectMode(\\'full-truck\\')">🚛 Full Truck Load</button><button class="sub-btn" onclick="selectMode(\\'less-truck\\')">📦 Less than Truck Load</button></div></div>';
            } else if (service === 'courier') {
                div.innerHTML = '<div class="bubble">Select type:<div class="sub-buttons"><button class="sub-btn" onclick="selectMode(\\'domestic-courier\\')">🇮🇳 Domestic Courier</button><button class="sub-btn" onclick="selectMode(\\'international-courier\\')">🌍 International Courier</button></div></div>';
            }
            
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function selectService(service) {
            currentService = service;
            
            if (service === 'about') {
                fetch('/about')
                    .then(res => res.json())
                    .then(data => {
                        addMessage(data.info, false);
                    });
                return;
            }
            
            addMessage(I need help with , true);
            addSubButtons(service);
        }
        
        function selectMode(mode) {
            const subDiv = document.getElementById('sub-buttons');
            if (subDiv) subDiv.remove();
            
            addMessage(I need  service, true);
            subStep = 'asking_name';
            addMessage('Great! Please share your name to proceed.', false);
        }
        
        async function sendText() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMessage(text, true);
            
            if (subStep === 'asking_name') {
                userData.name = text;
                subStep = 'asking_email';
                addMessage('Thanks! What is your email address?', false);
                return;
            }
            
            if (subStep === 'asking_email') {
                userData.email = text;
                subStep = 'asking_phone';
                addMessage('Your phone number? (Optional - type "skip")', false);
                return;
            }
            
            if (subStep === 'asking_phone') {
                if (text.toLowerCase() !== 'skip') {
                    userData.phone = text;
                }
                
                await fetch('/save_lead', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        service: currentService,
                        name: userData.name,
                        email: userData.email,
                        phone: userData.phone,
                        time: new Date().toISOString()
                    })
                });
                
                addMessage(Thank you ! Our team will contact you within 24 hours about  service., false);
                addMessage('For immediate assistance, call us at +91 9071660066 or email shivu@pasfreight.com', false);
                
                currentService = null;
                subStep = null;
                userData = { name: '', email: '', phone: '' };
                return;
            }
            
            // Regular text query
            const typing = document.createElement('div');
            typing.className = 'msg bot';
            typing.innerHTML = '<div class="bubble typing">...</div>';
            messagesDiv.appendChild(typing);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            typing.remove();
            addMessage(data.reply, false);
        }
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendText();
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
    info = """🏢 **PAS Freight Services Pvt Ltd**

📍 **Address:** Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092

📞 **Contact:** +91 9071660066, +91 9164466664

📧 **Email:** shivu@pasfreight.com

🌟 **Experience:** Over 8 years in logistics

✅ **Certifications:** WCA Member (ID: 115513), GLA Member (ID: 1166251)

🎯 **Vision:** To be Bangalore's most trusted logistics partner

💼 **Services:** Import, Export, Customs Clearance, Domestics, Couriers, Air & Sea Freight, Warehousing

We provide end-to-end logistics solutions across India and internationally!"""
    return jsonify({'info': info})

@app.route('/save_lead', methods=['POST'])
def save_lead():
    data = request.get_json()
    with open('leads.json', 'a') as f:
        f.write(json.dumps(data) + '\\n')
    print(f"✓ LEAD SAVED: {data.get('name')} - {data.get('service')} - {data.get('email')}")
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are PAS Freight AI assistant. Give short, helpful answers about logistics. For specific rates or quotes, tell users to call +91 9071660066. Be friendly and conversational."},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=100,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': 'For assistance, call +91 9071660066 or email shivu@pasfreight.com'})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PAS Freight - Smart Button AI Assistant")
    print("📱 Open: http://localhost:5001")
    print("📊 Leads saved to: leads.json")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
