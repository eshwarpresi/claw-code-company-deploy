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
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            position: relative;
        }

        /* Header */
        .header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 25px 20px;
            text-align: center;
        }

        .header h1 {
            font-size: 22px;
            font-weight: 600;
        }

        .header p {
            font-size: 12px;
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
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        /* Messages Area */
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f5f7fb;
        }

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
            font-size: 14px;
            line-height: 1.4;
            word-wrap: break-word;
        }

        .user-message .bubble {
            background: #2a5298;
            color: white;
            border-bottom-right-radius: 4px;
        }

        .bot-message .bubble {
            background: white;
            color: #333;
            border: 1px solid #e5e7eb;
            border-bottom-left-radius: 4px;
        }

        /* Typing Indicator */
        .typing {
            background: white;
            padding: 12px 16px;
            border-radius: 20px;
            display: inline-flex;
            gap: 4px;
            border: 1px solid #e5e7eb;
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

        /* Button Area */
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
            transition: transform 0.2s, box-shadow 0.2s;
        }

        .service-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        /* Input Area */
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
            transition: border-color 0.2s;
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
            transition: background 0.2s;
        }

        .input-area button:hover {
            background: #1e3c72;
        }

        /* Sub Buttons */
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
            transition: background 0.2s;
        }

        .sub-btn:hover {
            background: #2a5298;
        }

        /* Scrollbar */
        .messages::-webkit-scrollbar {
            width: 5px;
        }

        .messages::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        .messages::-webkit-scrollbar-thumb {
            background: #c1c1c1;
            border-radius: 5px;
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
            <div class="message bot-message">
                <div class="bubble">👋 Welcome to PAS Freight!<br><br>Please select a service below to get started.</div>
            </div>
        </div>

        <div class="button-area" id="buttonArea">
            <button class="service-btn" onclick="selectService('import')">📦 Import</button>
            <button class="service-btn" onclick="selectService('export')">🚢 Export</button>
            <button class="service-btn" onclick="selectService('customs')">📋 Customs</button>
            <button class="service-btn" onclick="selectService('domestic')">🚚 Domestics</button>
            <button class="service-btn" onclick="selectService('courier')">📮 Couriers</button>
            <button class="service-btn" onclick="selectService('about')">🏢 About Us</button>
        </div>

        <div class="input-area">
            <input type="text" id="userInput" placeholder="Or type your question..." autocomplete="off">
            <button onclick="sendText()">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const userInput = document.getElementById('userInput');
        let currentStep = null;
        let userData = { name: '', email: '', phone: '' };
        let selectedService = '';

        function addMessage(text, isUser, showButtons = false) {
            const div = document.createElement('div');
            div.className = message ;
            
            const bubble = document.createElement('div');
            bubble.className = 'bubble';
            bubble.innerHTML = text.replace(/\\n/g, '<br>');
            
            div.appendChild(bubble);
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function addSubButtons(service) {
            const div = document.createElement('div');
            div.className = 'message bot-message';
            div.id = 'subButtonsContainer';
            
            let buttonsHtml = '';
            if (service === 'import' || service === 'export') {
                buttonsHtml = 
                    <div class="bubble">
                        Select mode:
                        <div class="sub-buttons">
                            <button class="sub-btn" onclick="selectMode('air')">✈️ Air Freight</button>
                            <button class="sub-btn" onclick="selectMode('sea')">🚢 Sea Freight</button>
                        </div>
                    </div>
                ;
            } else if (service === 'domestic') {
                buttonsHtml = 
                    <div class="bubble">
                        Select type:
                        <div class="sub-buttons">
                            <button class="sub-btn" onclick="selectMode('full-truck')">🚛 Full Truck Load</button>
                            <button class="sub-btn" onclick="selectMode('less-truck')">📦 Less than Truck Load</button>
                        </div>
                    </div>
                ;
            } else if (service === 'courier') {
                buttonsHtml = 
                    <div class="bubble">
                        Select type:
                        <div class="sub-buttons">
                            <button class="sub-btn" onclick="selectMode('domestic-courier')">🇮🇳 Domestic Courier</button>
                            <button class="sub-btn" onclick="selectMode('international-courier')">🌍 International Courier</button>
                        </div>
                    </div>
                ;
            } else if (service === 'customs') {
                buttonsHtml = 
                    <div class="bubble">
                        Select type:
                        <div class="sub-buttons">
                            <button class="sub-btn" onclick="selectMode('import-customs')">📥 Import Customs</button>
                            <button class="sub-btn" onclick="selectMode('export-customs')">📤 Export Customs</button>
                        </div>
                    </div>
                ;
            }
            
            div.innerHTML = buttonsHtml;
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function selectService(service) {
            selectedService = service;
            
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

        function getServiceName(service) {
            const names = {
                'import': 'IMPORT',
                'export': 'EXPORT',
                'customs': 'CUSTOMS CLEARANCE',
                'domestic': 'DOMESTICS',
                'courier': 'COURIERS'
            };
            return names[service] || service;
        }

        function selectMode(mode) {
            const container = document.getElementById('subButtonsContainer');
            if (container) container.remove();
            
            addMessage(I need  service, true);
            currentStep = 'asking_name';
            addMessage('Great! Please share your full name to proceed.', false);
        }

        async function sendText() {
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
                
                addMessage(✅ Thank you ! Our team will contact you within 24 hours about  service., false);
                addMessage(📞 For immediate assistance, call us at +91 9071660066 or email shivu@pasfreight.com, false);
                
                currentStep = null;
                userData = { name: '', email: '', phone: '' };
                selectedService = '';
                return;
            }
            
            // Regular chat
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message';
            typingDiv.innerHTML = '<div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
            messagesDiv.appendChild(typingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({message: text})
            });
            const data = await res.json();
            typingDiv.remove();
            addMessage(data.reply, false);
        }

        userInput.addEventListener('keypress', (e) => {
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
    print("🚀 PAS Freight - Beautiful Button AI Assistant")
    print("📱 Open: http://localhost:5001")
    print("📊 Leads saved to: leads.json")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
