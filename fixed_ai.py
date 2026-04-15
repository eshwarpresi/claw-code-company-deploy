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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .chat-card {
            max-width: 500px;
            width: 100%;
            height: 90vh;
            background: white;
            border-radius: 30px;
            box-shadow: 0 30px 60px rgba(0,0,0,0.3);
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

        .header h1 {
            font-size: 20px;
        }

        .header p {
            font-size: 11px;
            opacity: 0.9;
            margin-top: 5px;
        }

        .status {
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #4ade80;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f5f7fb;
        }

        .message {
            margin-bottom: 16px;
            display: flex;
        }

        .user {
            justify-content: flex-end;
        }

        .bot {
            justify-content: flex-start;
        }

        .bubble {
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 20px;
            font-size: 14px;
            line-height: 1.4;
        }

        .user .bubble {
            background: #2a5298;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .bot .bubble {
            background: white;
            color: #333;
            border: 1px solid #e5e7eb;
            border-bottom-left-radius: 4px;
        }

        .button-area {
            padding: 16px;
            background: white;
            border-top: 1px solid #e5e7eb;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }

        .service-btn {
            padding: 12px 18px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 13px;
            font-weight: 500;
            flex: 1;
            min-width: 100px;
        }

        .service-btn:active {
            transform: scale(0.98);
        }

        .sub-buttons {
            display: flex;
            gap: 10px;
            margin-top: 10px;
            flex-wrap: wrap;
        }

        .sub-btn {
            padding: 8px 16px;
            background: #4a6a8a;
            color: white;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
        }

        .input-area {
            padding: 16px;
            background: white;
            border-top: 1px solid #e5e7eb;
            display: flex;
            gap: 10px;
        }

        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #e5e7eb;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }

        .input-area input:focus {
            border-color: #2a5298;
        }

        .input-area button {
            padding: 12px 24px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 500;
        }

        .typing {
            background: white;
            padding: 12px 16px;
            border-radius: 20px;
            display: inline-flex;
            gap: 4px;
        }

        .typing span {
            width: 8px;
            height: 8px;
            background: #999;
            border-radius: 50%;
            animation: typing 1.4s infinite;
        }

        .typing span:nth-child(2) { animation-delay: 0.2s; }
        .typing span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-8px); }
        }
    </style>
</head>
<body>
    <div class="chat-card">
        <div class="header">
            <h1>📦 PAS Freight Services Pvt Ltd</h1>
            <p><span class="status"></span> Online | 24/7 Support</p>
        </div>

        <div class="messages" id="messages">
            <div class="message bot">
                <div class="bubble">👋 Welcome to PAS Freight! Please select a service below.</div>
            </div>
        </div>

        <div class="button-area">
            <button class="service-btn" onclick="window.handleService('import')">📦 Import</button>
            <button class="service-btn" onclick="window.handleService('export')">🚢 Export</button>
            <button class="service-btn" onclick="window.handleService('customs')">📋 Customs</button>
            <button class="service-btn" onclick="window.handleService('domestic')">🚚 Domestics</button>
            <button class="service-btn" onclick="window.handleService('courier')">📮 Couriers</button>
            <button class="service-btn" onclick="window.handleService('about')">🏢 About Us</button>
        </div>

        <div class="input-area">
            <input type="text" id="userInput" placeholder="Type your question..." autocomplete="off">
            <button onclick="window.sendMessage()">Send</button>
        </div>
    </div>

    <script>
        let currentStep = null;
        let userData = { name: '', email: '', phone: '' };
        let selectedService = '';
        
        const messagesDiv = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = message ;
            div.innerHTML = <div class="bubble"></div>;
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function showTyping() {
            const div = document.createElement('div');
            div.className = 'message bot';
            div.id = 'typingIndicator';
            div.innerHTML = '<div class="typing"><span></span><span></span><span></span></div>';
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        function hideTyping() {
            const typing = document.getElementById('typingIndicator');
            if (typing) typing.remove();
        }
        
        window.handleService = function(service) {
            selectedService = service;
            
            if (service === 'about') {
                fetch('/about')
                    .then(res => res.json())
                    .then(data => {
                        addMessage(data.info, false);
                    });
                return;
            }
            
            const serviceNames = {
                'import': 'IMPORT',
                'export': 'EXPORT',
                'customs': 'CUSTOMS CLEARANCE',
                'domestic': 'DOMESTICS',
                'courier': 'COURIERS'
            };
            
            addMessage(I need help with , true);
            
            let buttonsHtml = '';
            if (service === 'import' || service === 'export') {
                buttonsHtml = '<div class="sub-buttons"><button class="sub-btn" onclick="window.selectMode(\\'air\\')">✈️ Air Freight</button><button class="sub-btn" onclick="window.selectMode(\\'sea\\')">🚢 Sea Freight</button></div>';
            } else if (service === 'domestic') {
                buttonsHtml = '<div class="sub-buttons"><button class="sub-btn" onclick="window.selectMode(\\'full-truck\\')">🚛 Full Truck Load</button><button class="sub-btn" onclick="window.selectMode(\\'less-truck\\')">📦 Less than Truck Load</button></div>';
            } else if (service === 'courier') {
                buttonsHtml = '<div class="sub-buttons"><button class="sub-btn" onclick="window.selectMode(\\'domestic\\')">🇮🇳 Domestic</button><button class="sub-btn" onclick="window.selectMode(\\'international\\')">🌍 International</button></div>';
            } else if (service === 'customs') {
                buttonsHtml = '<div class="sub-buttons"><button class="sub-btn" onclick="window.selectMode(\\'import\\')">📥 Import Customs</button><button class="sub-btn" onclick="window.selectMode(\\'export\\')">📤 Export Customs</button></div>';
            }
            
            const div = document.createElement('div');
            div.className = 'message bot';
            div.innerHTML = <div class="bubble">Select option:</div>;
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        };
        
        window.selectMode = function(mode) {
            addMessage(I need  service, true);
            currentStep = 'asking_name';
            addMessage('Please share your full name:', false);
        };
        
        window.sendMessage = async function() {
            const text = userInput.value.trim();
            if (!text) return;
            userInput.value = '';
            addMessage(text, true);
            
            if (currentStep === 'asking_name') {
                userData.name = text;
                currentStep = 'asking_email';
                addMessage('Thanks! What is your email address?', false);
                return;
            }
            
            if (currentStep === 'asking_email') {
                userData.email = text;
                currentStep = 'asking_phone';
                addMessage('Your phone number? (Optional - type "skip")', false);
                return;
            }
            
            if (currentStep === 'asking_phone') {
                if (text.toLowerCase() !== 'skip') {
                    userData.phone = text;
                }
                
                await fetch('/save_lead', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        service: selectedService,
                        name: userData.name,
                        email: userData.email,
                        phone: userData.phone,
                        time: new Date().toISOString()
                    })
                });
                
                addMessage(✅ Thank you ! Our team will contact you within 24 hours., false);
                addMessage(📞 For immediate help, call +91 9071660066, false);
                
                currentStep = null;
                userData = { name: '', email: '', phone: '' };
                selectedService = '';
                return;
            }
            
            showTyping();
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            hideTyping();
            addMessage(data.reply, false);
        };
        
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') window.sendMessage();
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

🌟 **Experience:** Over 8 years

✅ **Certifications:** WCA (115513), GLA (1166251)

💼 **Services:** Import, Export, Customs, Domestics, Couriers, Air & Sea Freight"""
    return jsonify({'info': info})

@app.route('/save_lead', methods=['POST'])
def save_lead():
    data = request.get_json()
    with open('leads.json', 'a') as f:
        f.write(json.dumps(data) + '\\n')
    print(f"✓ LEAD: {data.get('name')} - {data.get('service')}")
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are PAS Freight AI. Give short, helpful answers. For rates, tell users to call +91 9071660066."},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=100
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': 'Call +91 9071660066 for assistance'})

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 PAS Freight AI - FIXED VERSION")
    print("📱 Open: http://localhost:5001")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5001, debug=False)
