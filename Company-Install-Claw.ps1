# Company Claw-Code Installer for Windows
Write-Host "Installing Claw-Code for Company Use..." -ForegroundColor Green

# Check if Rust is installed
if (!(Get-Command cargo -ErrorAction SilentlyContinue)) {
    Write-Host "Installing Rust..." -ForegroundColor Yellow
    winget install Rustlang.Rustup --accept-package-agreements --silent
    Write-Host "Please restart PowerShell after installation" -ForegroundColor Red
    exit
}

# Install claw-code
Write-Host "Building claw-code..." -ForegroundColor Yellow
cd ~
git clone https://github.com/ultraworkers/claw-code.git
cd claw-code\rust
cargo build --release
cargo install --path crates/rusty-claude-cli

# Create config directory
New-Item -ItemType Directory -Force -Path "C:\Users\prave\.claw"

# Create config file
@'
{
  "model": "openai/gpt-4o-mini",
  "permission_mode": "workspace-write",
  "trusted_roots": ["C:\\temp", "C:\\Users"]
}
'@ | Out-File -FilePath "C:\Users\prave\.claw\config.json" -Encoding UTF8

# Create desktop shortcut
@'
@echo off
C:\Users\' + prave + '\.cargo\bin\claw.exe --model openai/gpt-4o-mini
'@ | Out-File -FilePath "C:\Users\prave\Desktop\Claw-Code-Chat.bat" -Encoding ASCII

Write-Host "Installation Complete!" -ForegroundColor Green
Write-Host "Double-click Claw-Code-Chat.bat on your desktop to start" -ForegroundColor Cyan
