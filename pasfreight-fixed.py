import openai
from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)

# Configure OpenRouter
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

COMPANY_NAME = "PAS Freight Services Pvt Ltd"
COMPANY_LOGO = "📦"
COMPANY_COLOR = "#1e3c72"
COMPANY_TAGLINE = "Top-Rated Logistics Services in Bangalore & Across India"

HTML = f'''
<!DOCTYPE html>
<html>
<head>
    <title>{COMPANY_NAME} - AI Assistant</title>
    <meta charset="UTF-8">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        .chat {{
            width: 100%;
            max-width: 900px;
            height: 95vh;
            display: flex;
            flex-direction: column;
            background: #ffffff;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            padding: 20px;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            text-align: center;
        }}
        .header h1 {{ font-size: 24px; margin-bottom: 5px; }}
        .header p {{ font-size: 12px; opacity: 0.9; }}
        .logo {{ font-size: 40px; margin-bottom: 10px; }}
        .messages {{
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }}
        .msg {{
            margin-bottom: 20px;
            display: flex;
        }}
        .user {{ justify-content: flex-end; }}
        .bot {{ justify-content: flex-start; }}
        .bubble {{
            max-width: 80%;
            padding: 12px 16px;
            border-radius: 18px;
            line-height: 1.5;
            font-size: 14px;
        }}
        .user .bubble {{
            background: #2a5298;
            color: white;
            border-bottom-right-radius: 4px;
        }}
        .bot .bubble {{
            background: #e9ecef;
            color: #333;
            border-bottom-left-radius: 4px;
        }}
        .input-area {{
            padding: 20px;
            background: white;
            display: flex;
            gap: 10px;
            border-top: 1px solid #dee2e6;
        }}
        .input-area input {{
            flex: 1;
            padding: 12px;
            border: 1px solid #dee2e6;
            border-radius: 25px;
            font-size: 14px;
            outline: none;
        }}
        .input-area input:focus {{ border-color: #2a5298; }}
        .input-area button {{
            padding: 12px 24px;
            background: #2a5298;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
        }}
        .input-area button:hover {{ background: #1e3c72; }}
        .typing {{ color: #6c757d; font-style: italic; }}
        .quick-buttons {{
            padding: 10px 20px;
            background: #f8f9fa;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            border-top: 1px solid #dee2e6;
        }}
        .quick-btn {{
            padding: 6px 12px;
            background: #e9ecef;
            border: none;
            border-radius: 20px;
            cursor: pointer;
            font-size: 12px;
        }}
        .quick-btn:hover {{ background: #2a5298; color: white; }}
    </style>
</head>
<body>
    <div class="chat">
        <div class="header">
            <div class="logo">{COMPANY_LOGO}</div>
            <h1>{COMPANY_NAME}</h1>
            <p>{COMPANY_TAGLINE}</p>
        </div>
        <div class="messages" id="messages">
            <div class="msg bot">
                <div class="bubble">Namaste! Welcome to PAS Freight Services. How can I assist you with your logistics needs today?<br><br>I can help with:<br>📦 Freight forwarding<br>🚢 Sea freight & Air freight<br>📋 Customs clearance<br>🚚 Trucking & warehousing<br>🌍 International shipping</div>
            </div>
        </div>
        <div class="quick-buttons">
            <button class="quick-btn" onclick="sendQuick('What services do you offer?')">📦 Services</button>
            <button class="quick-btn" onclick="sendQuick('What is your contact information?')">📞 Contact</button>
            <button class="quick-btn" onclick="sendQuick('What are your shipping rates to Dubai?')">🚢 Shipping Rates</button>
            <button class="quick-btn" onclick="sendQuick('Explain customs clearance process')">📋 Customs</button>
            <button class="quick-btn" onclick="sendQuick('How can I track my shipment?')">📍 Track Shipment</button>
        </div>
        <div class="input-area">
            <input type="text" id="input" placeholder="Type your message..." autocomplete="off">
            <button onclick="send()">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const input = document.getElementById('input');
        
        function addMessage(text, isUser) {{
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            div.innerHTML = '<div class="bubble">' + text.replace(/\\n/g, '<br>') + '</div>';
            messagesDiv.appendChild(div);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }}
        
        function sendQuick(text) {{
            input.value = text;
            send();
        }}
        
        async function send() {{
            const text = input.value.trim();
            if (!text) return;
            
            input.value = '';
            addMessage(text, true);
            
            const typing = document.createElement('div');
            typing.className = 'msg bot';
            typing.innerHTML = '<div class="bubble typing">Typing...</div>';
            messagesDiv.appendChild(typing);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            try {{
                const res = await fetch('/chat', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{message: text}})
                }});
                const data = await res.json();
                typing.remove();
                addMessage(data.reply, false);
            }} catch(err) {{
                typing.remove();
                addMessage('Sorry, an error occurred. Please try again.', false);
            }}
        }}
        
        input.addEventListener('keypress', (e) => {{
            if (e.key === 'Enter') send();
        }});
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
    
    system_prompt = f"""You are {COMPANY_NAME} AI Assistant. Use this information:

COMPANY INFO:
- Name: PAS Freight Services Pvt Ltd
- Services: Freight forwarding (air and sea), Customs clearance, Trucking, Warehousing, International shipping
- Contact: +91 9071660066, +91 9164466664, Email: shivu@pasfreight.com
- Address: Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092
- WCA Member ID: 115513, GLA Member ID: 1166251

Respond professionally and helpfully about logistics. If asked about rates, explain they vary by weight/dimensions and offer to connect with their team. Always be courteous and solution-oriented."""
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=500,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except Exception as e:
        error_msg = str(e)
        return jsonify({'reply': f'Thank you for your inquiry. For immediate assistance with your logistics needs, please contact us directly at +91 9071660066 or email shivu@pasfreight.com. Our team will respond promptly.'})

if __name__ == '__main__':
    print('=' * 60)
    print(f'🚀 {COMPANY_NAME} AI Assistant Running!')
    print('📱 Open http://localhost:5000')
    print('=' * 60)
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
