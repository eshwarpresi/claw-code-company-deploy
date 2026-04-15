import openai
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# Your NEW working OpenRouter API key
openai.api_key = "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"
openai.api_base = "https://openrouter.ai/api/v1"

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PAS Freight AI Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
            background: #f7f7f8;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: white;
            border-bottom: 1px solid #e5e5e5;
            padding: 16px 32px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }

        .logo {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .logo-icon {
            font-size: 28px;
        }

        .logo-text h1 {
            font-size: 18px;
            font-weight: 600;
            color: #1e3c72;
        }

        .logo-text p {
            font-size: 12px;
            color: #666;
            margin-top: 2px;
        }

        .status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 12px;
            color: #10a37f;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            background: #10a37f;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }

        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px 0;
        }

        .messages {
            max-width: 800px;
            margin: 0 auto;
        }

        .message {
            display: flex;
            gap: 16px;
            padding: 20px 16px;
            animation: fadeIn 0.3s ease;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .user-message {
            background: white;
        }

        .bot-message {
            background: #f7f7f8;
        }

        .avatar {
            width: 32px;
            height: 32px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            flex-shrink: 0;
        }

        .user-avatar {
            background: #10a37f;
            color: white;
        }

        .bot-avatar {
            background: #1e3c72;
            color: white;
        }

        .content {
            flex: 1;
            line-height: 1.6;
            color: #2c3e50;
            font-size: 14px;
        }

        .content p {
            margin-bottom: 12px;
        }

        .content ul, .content ol {
            margin: 12px 0;
            padding-left: 24px;
        }

        .content li {
            margin: 6px 0;
        }

        .input-container {
            background: white;
            border-top: 1px solid #e5e5e5;
            padding: 20px 32px;
            flex-shrink: 0;
        }

        .input-wrapper {
            max-width: 800px;
            margin: 0 auto;
            position: relative;
        }

        .input-wrapper textarea {
            width: 100%;
            padding: 14px 50px 14px 18px;
            border: 1px solid #e5e5e5;
            border-radius: 12px;
            font-size: 14px;
            font-family: inherit;
            resize: none;
            outline: none;
            transition: border-color 0.2s;
        }

        .input-wrapper textarea:focus {
            border-color: #1e3c72;
        }

        .send-button {
            position: absolute;
            right: 12px;
            bottom: 10px;
            background: #1e3c72;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 6px 12px;
            cursor: pointer;
            font-size: 12px;
            transition: background 0.2s;
        }

        .send-button:hover {
            background: #2a5298;
        }

        .typing-indicator {
            display: flex;
            gap: 4px;
            padding: 8px 0;
        }

        .typing-indicator span {
            width: 8px;
            height: 8px;
            background: #999;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
        }

        .typing-indicator span:nth-child(1) { animation-delay: -0.32s; }
        .typing-indicator span:nth-child(2) { animation-delay: -0.16s; }

        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        ::-webkit-scrollbar {
            width: 8px;
        }

        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }

        ::-webkit-scrollbar-thumb {
            background: #ccc;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">
            <div class="logo-icon">📦</div>
            <div class="logo-text">
                <h1>PAS Freight Services Pvt Ltd</h1>
                <p>Logistics & Freight Solutions | Bangalore</p>
            </div>
        </div>
        <div class="status">
            <div class="status-dot"></div>
            <span>Online</span>
        </div>
    </div>

    <div class="chat-container" id="chatContainer">
        <div class="messages" id="messages">
            <div class="message bot-message">
                <div class="avatar bot-avatar">🤖</div>
                <div class="content">
                    <p>Namaste! 👋 I'm the PAS Freight AI Assistant.</p>
                    <p>I can help you with:</p>
                    <ul>
                        <li>Freight forwarding (Air & Sea)</li>
                        <li>Customs clearance</li>
                        <li>Trucking and transportation</li>
                        <li>Warehousing solutions</li>
                        <li>International shipping</li>
                    </ul>
                    <p>How can I assist you with your logistics needs today?</p>
                </div>
            </div>
        </div>
    </div>

    <div class="input-container">
        <div class="input-wrapper">
            <textarea id="userInput" rows="2" placeholder="Type your message here... Press Enter to send"></textarea>
            <button class="send-button" onclick="sendMessage()">Send</button>
        </div>
    </div>

    <script>
        const messagesDiv = document.getElementById('messages');
        const chatContainer = document.getElementById('chatContainer');
        const userInput = document.getElementById('userInput');

        function formatContent(text) {
            text = text.replace(/\\n/g, '<br>');
            text = text.replace(/^- (.*?)$/gm, '<li></li>');
            text = text.replace(/<li>.*?<\/li>/gs, (match) => <ul></ul>);
            text = text.replace(/<\/ul><ul>/g, '');
            return text;
        }

        function addMessage(content, isUser) {
            const messageDiv = document.createElement('div');
            messageDiv.className = message ;
            
            const avatar = document.createElement('div');
            avatar.className = vatar ;
            avatar.textContent = isUser ? '👤' : '🤖';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'content';
            
            if (isUser) {
                contentDiv.textContent = content;
            } else {
                contentDiv.innerHTML = formatContent(content);
            }
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(contentDiv);
            messagesDiv.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function showTyping() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message';
            typingDiv.id = 'typing-indicator';
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar bot-avatar';
            avatar.textContent = '🤖';
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'content';
            contentDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
            
            typingDiv.appendChild(avatar);
            typingDiv.appendChild(contentDiv);
            messagesDiv.appendChild(typingDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }

        function hideTyping() {
            const typing = document.getElementById('typing-indicator');
            if (typing) typing.remove();
        }

        async function sendMessage() {
            const text = userInput.value.trim();
            if (!text) return;
            
            userInput.value = '';
            addMessage(text, true);
            showTyping();
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: text})
                });
                const data = await response.json();
                hideTyping();
                addMessage(data.reply, false);
            } catch (error) {
                hideTyping();
                addMessage('I apologize, but I encountered an issue. Please contact us at +91 9071660066 for immediate assistance.', false);
            }
        }

        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
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
    
    system_prompt = """You are a professional customer service representative for PAS Freight Services Pvt Ltd.

Company Information:
- Services: Freight forwarding (Air & Sea), Customs clearance, Trucking and transportation, Warehousing, International shipping, Supply chain management
- Contact: +91 9071660066, +91 9164466664  
- Email: shivu@pasfreight.com
- Address: Site No:171, Arkavathey Layout, 7th Block, Jakkur-BDA, Bangalore - 560092
- Experience: Over 8 years in logistics
- Certifications: WCA Member ID 115513, GLA Member ID 1166251

Response Guidelines:
- Be professional, helpful, and friendly
- Provide accurate information about PAS Freight services
- Keep responses clear and easy to understand
- Always offer to connect with the team when needed
- For rates, explain they vary by weight, dimensions, and destination

Answer all questions professionally and helpfully."""
    
    try:
        response = openai.ChatCompletion.create(
            model="openai/gpt-4o-mini",
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
        print(f"Error: {error_msg}")
        return jsonify({'reply': 'Thank you for your inquiry. Please contact PAS Freight at +91 9071660066 or email shivu@pasfreight.com for immediate assistance.'})

if __name__ == '__main__':
    print('=' * 60)
    print('🚀 PAS Freight AI Assistant - FINAL WORKING VERSION')
    print('📱 Open in browser: http://localhost:5000')
    print('=' * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
