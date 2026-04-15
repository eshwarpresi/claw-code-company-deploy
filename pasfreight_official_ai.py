import openai
from flask import Flask, request, jsonify, render_template_string
import re

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

# Complete PAS Freight Information from website
PAS_INFO = """
PAS FREIGHT SERVICES PVT LTD - COMPLETE COMPANY PROFILE

ABOUT US:
PAS Freight Services Pvt Ltd is a prominent provider of logistics services in Bangalore and around India. We specialize in customs clearing and International freight transportation. We provide full trucking and transportation solutions to ensure seamless import and export operations. With over 8 years of expertise, we manage the entire logistics chain including air and sea freight, customs clearance, warehousing, insurance, and real-time cargo tracking.

HEAD OFFICE:
Site No:171, Arkavathey Layout, 7th Block, Sy No: 90/3, Jakkur-BDA, Bangalore - 560092, Karnataka, India

MANAGING DIRECTOR:
Siva Prasad (SHIVU)

CONTACT NUMBERS:
- +91 9071660066
- +91 9164466664
- +91 9036101201
- Import/Export Air: +91 93648 81371
- Import/Export Sea: +91 63615 21413
- Customs Clearance: +91 63615 26664
- Domestic & Courier: +91 96116 60204

EMAIL:
shivu@pasfreight.com

WEBSITE:
www.pasfreight.com

CERTIFICATIONS:
- WCA Member (ID: 115513)
- GLA Member (ID: 1166251)

SERVICES OFFERED:
1. Air Freight - Fast and reliable air transportation
2. Sea Freight - Cost-effective ocean shipping
3. Customs Clearance - Expert customs documentation
4. Trucking and Transportation - Full trucking solutions
5. Warehousing - Secure storage facilities
6. Insurance - Cargo insurance coverage
7. Real-time Cargo Tracking - Track your shipments
8. International Shipping - Global shipping solutions
9. Supply Chain Management - Complete logistics management

WHY CHOOSE PAS FREIGHT:
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

INDUSTRIES SERVED:
- Fashion/Apparel
- Publishing
- Telecom
- Automobile & Industrial
- Hi-Tech

SERVICE AREAS:
Bangalore, Chennai, Delhi, Mumbai, Hyderabad, and across India with international shipping capabilities

VISION:
To be recognized as Bangalore's most trusted logistics partner, delivering innovative and reliable end-to-end logistics solutions that power our clients' growth across India and global markets.

OPERATING HOURS:
24/7 Customer Support - Round the clock service
"""

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight - Official AI Assistant</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0a2647, #1a3c5e);
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
            box-shadow: 0 0 40px rgba(0,0,0,0.3);
        }
        .header {
            background: linear-gradient(135deg, #0a2647, #1a3c5e);
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 20px; }
        .header p { font-size: 11px; opacity: 0.9; margin-top: 5px; }
        .badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 10px;
            margin-top: 8px;
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f0f2f5;
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
        .user .bubble { background: #1a3c5e; color: white; border-bottom-right-radius: 4px; }
        .bot .bubble { background: white; color: #333; border: 1px solid #e0e0e0; border-bottom-left-radius: 4px; }
        .quick-buttons {
            padding: 12px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .quick-btn {
            background: #e8ecf1;
            border: none;
            padding: 8px 14px;
            border-radius: 25px;
            font-size: 12px;
            cursor: pointer;
            transition: all 0.2s;
        }
        .quick-btn:hover { background: #1a3c5e; color: white; }
        .input-area {
            padding: 12px;
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
            background: #1a3c5e;
            color: white;
            border: none;
            width: 46px;
            height: 46px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 18px;
        }
        .typing {
            background: white;
            padding: 10px 14px;
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
        .footer-note {
            text-align: center;
            padding: 8px;
            font-size: 9px;
            color: #888;
            background: white;
            border-top: 1px solid #eee;
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
            <div class="bubble">🚀 Namaste! I'm PAS Freight's Official AI Assistant.<br><br>I know EVERYTHING about our services:<br>✈️ Air & Sea Freight | 📋 Customs Clearance<br>🚚 Trucking | 🏭 Warehousing | 🌍 International Shipping<br><br>How can I help you with your logistics needs today?</div>
        </div>
    </div>
    <div class="quick-buttons">
        <button class="quick-btn" onclick="sendQuick('What services do you offer?')">📦 Services</button>
        <button class="quick-btn" onclick="sendQuick('What is your contact number?')">📞 Contact</button>
        <button class="quick-btn" onclick="sendQuick('Where is your office located?')">📍 Address</button>
        <button class="quick-btn" onclick="sendQuick('What are your certifications?')">✅ Certifications</button>
        <button class="quick-btn" onclick="sendQuick('Do you have 24/7 support?')">🕐 24/7 Support</button>
        <button class="quick-btn" onclick="sendQuick('Customs clearance process')">📋 Customs</button>
    </div>
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Ask about PAS Freight services...">
        <button id="sendBtn">➤</button>
    </div>
    <div class="footer-note">
        PAS Freight Services Pvt Ltd | WCA:115513 | GLA:1166251
    </div>
</div>

<script>
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
    
    system_prompt = f"""You are the OFFICIAL AI ASSISTANT for PAS Freight Services Pvt Ltd.

IMPORTANT RULES:
1. ONLY answer questions about PAS Freight, logistics, shipping, freight, customs, transportation
2. If user asks anything NOT related to logistics (personal questions, general knowledge, entertainment), POLITELY redirect to PAS Freight services
3. Use ONLY the company information provided below
4. Give accurate, helpful answers with specific details
5. ALWAYS include contact numbers when appropriate

COMPANY INFORMATION (USE THIS ONLY):
{PAS_INFO}

Response Guidelines:
- For service questions: List specific services with details
- For rates: "Please call +91 9071660066 for exact rates based on your shipment"
- For address: Give complete Bangalore address
- For certifications: Mention WCA ID 115513 and GLA ID 1166251
- For non-logistics questions: "I specialize in PAS Freight logistics. How can I help you with shipping or freight today?"

Answer professionally and helpfully based ONLY on PAS Freight information."""

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
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': '📞 For immediate assistance with PAS Freight services, please call +91 9071660066 or email shivu@pasfreight.com'})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PAS FREIGHT OFFICIAL AI ASSISTANT")
    print("📱 Open: http://localhost:5001")
    print("📋 Knowledge: Complete PAS Freight company information")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
