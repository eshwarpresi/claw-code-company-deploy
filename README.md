# Claw-Code Company Setup Guide

## Quick Start for Employees

### First Time Setup (One Time Only)

1. **Run the installer as Administrator:**
   - Right-click on Company-Install-Claw.ps1
   - Select "Run with PowerShell"
   - Wait for installation to complete (5-10 minutes)

2. **Get your API Key:**
   - Go to https://openrouter.ai/keys
   - Sign up with your company email
   - Create a new key
   - Copy the key (starts with sk-or-v1-)

3. **Set your API Key (One Time):**
   - Open PowerShell as Administrator
   - Run: [Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "YOUR-KEY-HERE", "User")
   - Run: [Environment]::SetEnvironmentVariable("OPENAI_BASE_URL", "https://openrouter.ai/api/v1", "User")

### Daily Usage

**Option 1: Desktop Shortcut**
- Double-click Claw-Code-Chat.bat on your desktop

**Option 2: PowerShell Command**
- Type: i prompt "Your question here"

### Examples

\\\
# Chat interactively
claw --model openai/gpt-4o-mini

# Ask a question
ai prompt "What is a REST API?"

# Read a file
ai prompt "Read config.json and explain it"

# Create a file
ai prompt "Create a hello.py file with print('Hello')"
\\\

### Need Help?
- Type /help inside the chat
- Contact IT support

### Troubleshooting
- If 'claw' not found: Close and reopen PowerShell
- If API error: Check your API key is set correctly
- Run claw doctor to diagnose issues
