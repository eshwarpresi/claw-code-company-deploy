import openai
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow any website to use this widget

openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

# Main HTML for the chat widget (popup window)
WIDGET_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>PAS Freight AI</title>
    <meta charset="UTF-8">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: white;
            width: 380px;
            height: 600px;
            overflow: hidden;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        
        /* Chat Container */
        .chat-widget {
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #ffffff;
        }
        
        /* Header */
        .widget-header {
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-radius: 16px 16px 0 0;
        }
        
        .header-info {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .avatar {
            width: 36px;
            height: 36px;
            background: rgba(255,255,255,0.2);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
        }
        
        .header-text h3 {
            font-size: 14px;
            font-weight: 600;
        }
        
        .header-text p {
            font-size: 10px;
            opacity: 0.8;
            margin-top: 2px;
        }
        
        .close-btn {
            background: none;
            border: none;
            color: white;
            font-size: 20px;
            cursor: pointer;
            padding: 4px;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .close-btn:hover {
            background: rgba(255,255,255,0.1);
        }
        
        /* Messages Area */
        .messages-area {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
            background: #f8f9fa;
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
            max-width: 85%;
            padding: 10px 14px;
            border-radius: 18px;
            font-size: 13px;
            line-height: 1.4;
        }
        
        .user-message .bubble {
            background: #2a5298;
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .bot-message .bubble {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        
        /* Quick Buttons */
        .quick-buttons {
            padding: 12px;
            background: white;
            border-top: 1px solid #e5e5e5;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        
        .quick-btn {
            background: #f0f2f5;
            border: none;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 11px;
            cursor: pointer;
            transition: all 0.2s;
        }
        
        .quick-btn:hover {
            background: #2a5298;
            color: white;
        }
        
        /* Input Area */
        .input-area {
            padding: 12px;
            background: white;
            border-top: 1px solid #e5e5e5;
            display: flex;
            gap: 8px;
        }
        
        .input-area input {
            flex: 1;
            padding: 10px 14px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 13px;
            outline: none;
        }
        
        .input-area input:focus {
            border-color: #2a5298;
        }
        
        .input-area button {
            background: #2a5298;
            color: white;
            border: none;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            cursor: pointer;
            font-size: 16px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .typing {
            display: inline-flex;
            gap: 4px;
            padding: 4px 0;
        }
        
        .typing span {
            width: 6px;
            height: 6px;
            background: #999;
            border-radius: 50%;
            animation: typingBounce 1.4s infinite;
        }
        
        @keyframes typingBounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }
        
        .messages-area::-webkit-scrollbar {
            width: 4px;
        }
        .messages-area::-webkit-scrollbar-track {
            background: #e5e5e5;
        }
        .messages-area::-webkit-scrollbar-thumb {
            background: #999;
            border-radius: 4px;
        }
    </style>
</head>
<body>
<div class="chat-widget">
    <div class="widget-header">
        <div class="header-info">
            <div class="avatar">📦</div>
            <div class="header-text">
                <h3>PAS Freight AI</h3>
                <p>Online | 24/7 Support</p>
            </div>
        </div>
        <button class="close-btn" onclick="parent.closeWidget()">✕</button>
    </div>
    
    <div class="messages-area" id="messagesArea">
        <div class="message bot-message">
            <div class="bubble">👋 Namaste! I'm PAS Freight AI Assistant.<br><br>How can I help you with logistics today?</div>
        </div>
    </div>
    
    <div class="quick-buttons">
        <button class="quick-btn" onclick="sendQuick('What services do you offer?')">📦 Services</button>
        <button class="quick-btn" onclick="sendQuick('Contact number')">📞 Contact</button>
        <button class="quick-btn" onclick="sendQuick('Office address')">📍 Address</button>
        <button class="quick-btn" onclick="sendQuick('Customs clearance')">📋 Customs</button>
    </div>
    
    <div class="input-area">
        <input type="text" id="userInput" placeholder="Type your message..." autocomplete="off">
        <button id="sendBtn">➤</button>
    </div>
</div>

<script>
    function addMessage(text, isUser) {
        const div = document.createElement('div');
        div.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        div.innerHTML = `<div class="bubble">${text}</div>`;
        document.getElementById('messagesArea').appendChild(div);
        div.scrollIntoView({ behavior: 'smooth' });
    }
    
    function showTyping() {
        const div = document.createElement('div');
        div.className = 'message bot-message';
        div.id = 'typing';
        div.innerHTML = '<div class="bubble"><div class="typing"><span></span><span></span><span></span></div></div>';
        document.getElementById('messagesArea').appendChild(div);
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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
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

# The embed code for website (floating button)
EMBED_CODE = '''
<!-- PAS Freight Chat Widget -->
<div id="pasfreight-chat-widget" style="position: fixed; bottom: 20px; right: 20px; z-index: 999999;">
    <style>
        #pasfreight-chat-btn {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            border-radius: 50%;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s ease;
            border: none;
            animation: pulse 2s infinite;
        }
        
        #pasfreight-chat-btn:hover {
            transform: scale(1.1);
        }
        
        @keyframes pulse {
            0%, 100% { box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
            50% { box-shadow: 0 4px 25px rgba(0,0,0,0.5); }
        }
        
        .chat-icon {
            font-size: 28px;
            color: white;
        }
        
        .notification-badge {
            position: absolute;
            top: -5px;
            right: -5px;
            background: #ef4444;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 11px;
            display: flex;
            align-items: center;
            justify-content: center;
            animation: blink 1s infinite;
        }
        
        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        #pasfreight-chat-frame {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 380px;
            height: 600px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            display: none;
            z-index: 999998;
            border: none;
            overflow: hidden;
        }
        
        @media (max-width: 500px) {
            #pasfreight-chat-frame {
                width: 100%;
                height: 100%;
                bottom: 0;
                right: 0;
                border-radius: 0;
            }
        }
    </style>
    <button id="pasfreight-chat-btn">
        <span class="chat-icon">💬</span>
        <span class="notification-badge" id="notificationBadge" style="display: none;">1</span>
    </button>
    <iframe id="pasfreight-chat-frame" src="https://YOUR_SERVER_URL" title="PAS Freight Chat"></iframe>
</div>

<script>
    (function() {
        const btn = document.getElementById('pasfreight-chat-btn');
        const frame = document.getElementById('pasfreight-chat-frame');
        const badge = document.getElementById('notificationBadge');
        let isOpen = false;
        
        // Close widget function (called from iframe)
        window.closeWidget = function() {
            frame.style.display = 'none';
            isOpen = false;
        };
        
        btn.addEventListener('click', function() {
            if (isOpen) {
                frame.style.display = 'none';
                isOpen = false;
            } else {
                frame.style.display = 'block';
                isOpen = true;
                badge.style.display = 'none';
            }
        });
        
        // Show notification badge after 30 seconds if not opened
        setTimeout(function() {
            if (!isOpen) {
                badge.style.display = 'flex';
            }
        }, 30000);
    })();
</script>
'''

@app.route('/')
def index():
    return render_template_string(WIDGET_HTML)

@app.route('/widget.js')
def widget_js():
    # Replace placeholder with actual server URL
    embed = EMBED_CODE.replace('https://YOUR_SERVER_URL', f'http://{request.host}')
    return embed, 200, {'Content-Type': 'application/javascript'}

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_msg = data.get('message', '')
    
    system_prompt = """You are PAS Freight AI Assistant. Give short, helpful answers about logistics.

Company Info:
PAS Freight Services Pvt Ltd - Bangalore
Services: Import/Export (Air/Sea), Customs Clearance, Domestics, Courier
Contact: +91 90361 01201
Email: shivu@pasfreight.com

Keep answers concise (1-2 sentences). Be helpful and professional."""

    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=100,
            temperature=0.7
        )
        reply = response['choices'][0]['message']['content']
        return jsonify({'reply': reply})
    except:
        return jsonify({'reply': 'For assistance, call +91 90361 01201 or email shivu@pasfreight.com'})

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 PAS Freight Floating Chat Widget")
    print("📱 Widget URL: http://localhost:5001")
    print("📋 Embed this script on your website:")
    print('<script src="http://localhost:5001/widget.js"></script>')
    print("=" * 60)
    app.run(host='0.0.0.0', port=5001, debug=False)
