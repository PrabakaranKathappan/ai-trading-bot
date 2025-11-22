# Quick Commands - GitHub Push

**IMPORTANT:** Close and reopen your terminal first!

## Quick Setup (Copy & Paste)

```powershell
# 1. Configure Git (replace with your info)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 2. Navigate to project
cd "c:\Users\Prabakaran K\Documents\antigravity_apps\AiTradingBot"

# 3. Initialize and commit
git init
git add .
git commit -m "Initial commit: AI Trading Bot for Nifty Options"

# 4. Create GitHub repo at: https://github.com/new
# Then connect (replace YOUR_USERNAME):
git remote add origin https://github.com/YOUR_USERNAME/ai-trading-bot.git
git branch -M main
git push -u origin main
```

## Authentication

When prompted for password, use a **Personal Access Token**:
1. Go to: https://github.com/settings/tokens
2. Generate new token (classic)
3. Select `repo` scope
4. Copy token and use as password

---

See `GITHUB_PUSH_GUIDE.md` for detailed instructions.
