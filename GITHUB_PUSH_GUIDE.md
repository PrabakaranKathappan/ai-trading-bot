# GitHub Push Guide

Git has been installed on your system. **Please close and reopen your terminal/PowerShell** for Git to work properly.

## Step 1: Configure Git (First Time Only)

Open a **new PowerShell window** and run these commands:

```powershell
# Set your name (replace with your actual name)
git config --global user.name "Your Name"

# Set your email (use your GitHub email)
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

## Step 2: Navigate to Project Directory

```powershell
cd "c:\Users\Prabakaran K\Documents\antigravity_apps\AiTradingBot"
```

## Step 3: Initialize Git Repository

```powershell
# Initialize Git
git init

# Check status (should show untracked files)
git status
```

## Step 4: Stage and Commit Files

```powershell
# Add all files (respects .gitignore)
git add .

# Create initial commit
git commit -m "Initial commit: AI Trading Bot for Nifty Options"

# Verify commit
git log --oneline
```

## Step 5: Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `ai-trading-bot` (or any name you prefer)
3. Description: "AI Trading Bot for Nifty Options with Upstox API"
4. Keep it **Private** (recommended for trading bots)
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

## Step 6: Connect to GitHub

After creating the repository, GitHub will show you commands. Use these:

```powershell
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/ai-trading-bot.git

# Rename branch to main (if needed)
git branch -M main

# Push code to GitHub
git push -u origin main
```

### If GitHub asks for authentication:

**Option A: Personal Access Token (Recommended)**
1. Go to https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Give it a name: "AI Trading Bot"
4. Select scopes: `repo` (all repo permissions)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. When pushing, use:
   - Username: Your GitHub username
   - Password: The token you just copied

**Option B: GitHub CLI**
```powershell
# Install GitHub CLI
winget install --id GitHub.cli

# Authenticate
gh auth login
```

## Step 7: Verify Upload

1. Go to your repository on GitHub
2. Verify all files are there
3. Check that `.env` is **NOT** uploaded (it should be ignored)

## Important Notes

✅ **What WILL be uploaded:**
- All Python files
- `requirements.txt`
- `Procfile`, `render.yaml`
- Documentation files
- `.env.example` (template)

❌ **What will NOT be uploaded (protected by .gitignore):**
- `.env` (your API keys are safe!)
- `*.db` (database files)
- `logs/` (log files)
- `__pycache__/` (Python cache)

## Next Steps After GitHub Push

Once your code is on GitHub:
1. Deploy to Render (follow `DEPLOY.md`)

## Troubleshooting

### "git: command not found"
- Close and reopen your terminal
- Or restart your computer

### Authentication failed
- Use Personal Access Token instead of password
- Make sure token has `repo` permissions

### Large files error
- Check if any large files are being committed
- Add them to `.gitignore` if needed

---

**Ready?** Close this terminal, open a new one, and start from Step 1!
