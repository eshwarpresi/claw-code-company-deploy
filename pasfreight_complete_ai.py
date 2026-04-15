import openai
from flask import Flask, request, jsonify, render_template_string
import json
from datetime import datetime

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

# Complete company information from your website
COMPANY_INFO = """
PAS FREIGHT SERVICES PVT LTD - Complete Company Profile

FULL NAME: PAS Freight Services Pvt Ltd

ABOUT US:
PAS Freight Services Pvt Ltd is a prominent provider of logistics services in Bangalore and around India. We specialize in customs clearing and International freight transportation. We provide full trucking and transportation solutions for seamless import and export operations.

EXPERIENCE: Over 8 years of expertise in the industry

HEAD OFFICE LOCATION:
Site No:171, Arkavathey Layout, 7th Block, Sy No: 90/3, Jakkur-BDA, Bangalore - 560092, Karnataka, India

CONTACT INFORMATION:
- Phone: +91 9071660066, +91 9164466664, +91 9036101201
- Email: shivu@pasfreight.com
- Website: www.pasfreight.com

MANAGING DIRECTOR: Siva Prasad (SHIVU)

CERTIFICATIONS & MEMBERSHIPS:
- WCA Member (ID: 115513)
- GLA Member (ID: 1166251)

SERVICES WE OFFER:
1. Air Freight - Fast and reliable air transportation
2. Sea Freight - Cost-effective ocean shipping
3. Customs Clearance - Expert customs documentation and procedures
4. Trucking and Transportation - Full trucking solutions
5. Warehousing - Secure storage facilities
6. Insurance - Cargo insurance coverage
7. Real-time Cargo Tracking - Track your shipments
8. International Shipping - Global shipping solutions
9. Supply Chain Management - Complete logistics management

WHY CHOOSE US:
- 24/7 Customer Support
- Professional & Certified Team
- Flexible & Custom Solutions
- Proactive Supply Chain Management
- Advanced Tracking Technology
- Industry-Expert People
- End to End Solutions
- Dedicated Customer Service Desk
- E-invoicing
- Security
- Single Window Solution
- Industry expertise
- Save from currency fluctuations
- Complete Visibility

INDUSTRIES WE SERVE:
- Fashion/Apparel
- Publishing
- Telecom
- Automobile & Industrial
- Hi-Tech

VISION:
To be recognized as Bangalore's most trusted logistics partner, delivering innovative and reliable end-to-end logistics solutions that power our clients' growth across India and global markets.

OPERATING HOURS:
24/7 Customer Support - We operate round the clock

SERVICE AREAS:
Bangalore, Chennai, Delhi, Mumbai, Hyderabad, and across India with international shipping capabilities

BRANCHES:
We have a strong presence across India with our headquarters in Bangalore and services available in all major cities including Chennai, Delhi, Mumbai, Hyderabad.
"""

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight Services Pvt Ltd - Advanced AI</title>
    <meta charset="UTF-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .chat-container {
            max-width: 1000px;
            width: 100%;
            height: 90vh;
            background: white;
            border-radius: 20px;
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
        .header h1 { font-size: 22px; }
        .header p { font-size: 12px; opacity: 0.9; margin-top: 5px; }
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
            padding: 12px 18px;
            border-radius: 20px;
            max-width: 80%;
            font-size: 14px;
            line-height: 1.5;
        }
        .user .bubble { background: #2a5298; color: white; border-bottom-right-radius: 4px; }
        .bot .bubble { background: white; color: #333; border: 1px solid #e0e0e0; border-bottom-left-radius: 4px; }
        .input-area {
            padding: 20px;
            background: white;
            display: flex;
            gap: 12px;
            border-top: 1px solid #e5e5e5;
        }
        .input-area input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }
        .input-area input:focus { border-color: #2a5298; }
        .input-area button {
            padding: 12px 24px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
        }
        .typing { color: #999; font-style: italic; }
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
            <p>Advanced AI Assistant | 24/7 Logistics Support</p>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="bubble">👋 Namaste! Welcome to PAS Freight Services Pvt Ltd. I'm your advanced AI assistant. I know everything about our company. May I know your name please?</div>
            </div>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Ask anything about PAS Freight..." autocomplete="off">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('input');
        let step = 'asking_name';
        let userName = '';
        let userEmail = '';
        let userPhone = '';
        
        function addMessage(text, isUser) {
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            div.innerHTML = '<div class="bubble">' + text.replace(/\\n/g, '<br>') + '</div>';
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
        
        async function sendMessage() {
            const text = input.value.trim();
            if (!text) return;
            input.value = '';
            addMessage(text, true);
            
            if (step === 'asking_name') {
                userName = text;
                step = 'asking_email';
                addMessage('Thanks ' + userName + '! Could you please share your email address?', false);
                return;
            }
            
            if (step === 'asking_email') {
                userEmail = text;
                step = 'asking_phone';
                addMessage('Great! Your phone number? (Optional - type "skip" if you prefer not to share)', false);
                return;
            }
            
            if (step === 'asking_phone') {
                if (text.toLowerCase() !== 'skip') {
                    userPhone = text;
                }
                step = 'ready';
                
                await fetch('/save_user', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        name: userName,
                        email: userEmail,
                        phone: userPhone,
                        time: new Date().toISOString()
                    })
                });
                
                addMessage('Thank you ' + userName + '! 🎉 Now I can help you with any questions about PAS Freight Services. What would you like to know?', false);
                return;
            }
            
            const typing = document.createElement('div');
            typing.className = 'msg bot';
            typing.innerHTML = '<div class="bubble typing">...</div>';
            messagesDiv.appendChild(typing);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    message: text,
                    user_name: userName
                })
            });
            const data = await res.json();
            typing.remove();
            addMessage(data.reply, false);
        }
        
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/save_user', methods=['POST'])
def save_user():
    data = request.get_json()
    with open('user_details.json', 'a') as f:
        f.write(json.dumps(data) + '\\n')
    print(f"✓ Saved: {data.get('name')} - {data.get('email')}")
    return jsonify({'status': 'ok'})

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    user_name = data.get('user_name', '')
    
    system_prompt = f"""You are the official AI assistant for PAS Freight Services Pvt Ltd. Use this COMPLETE company information to answer:

{COMPANY_INFO}

RULES FOR ANSWERING:
1. Give ACCURATE, COMPLETE answers based ONLY on the company info above
2. Be friendly and conversational - use {user_name}'s name naturally
3. Answer in the same language as the user (English/Hindi/Kannada)
4. For any question about company, services, location, timings - answer directly from the information
5. If asked about address: Give the complete Jakkur-BDA address
6. If asked about branches: Mention Bangalore, Chennai, Delhi, Mumbai, Hyderabad
7. If asked about founder: Siva Prasad (SHIVU) is the Managing Director
8. If asked about certifications: Mention WCA ID 115513 and GLA ID 1166251
9. Keep answers helpful but conversational - 2-3 sentences usually sufficient

Answer the user's question accurately and helpfully."""

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=200,
            temperature=0.5
        )
        reply = response['choices'][0]['message']['content']
        print(f"✓ {user_name}: {user_msg[:50]}")
        return jsonify({'reply': reply})
    except Exception as e:
        print(f"✗ Error: {e}")
        return jsonify({'reply': f'Thanks {user_name}! For any PAS Freight inquiries, call +91 9071660066 or email shivu@pasfreight.com'})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PAS Freight Services Pvt Ltd - ADVANCED AI")
    print("📱 Open: http://localhost:5001")
    print("📊 User details saved to: user_details.json")
    print("💡 AI knows: Address, Services, Contact, Hours, Branches, Certifications")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
