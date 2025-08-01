# GitHub Multi-Account Setup Guide

## Current System Configuration

### Existing GitHub Accounts Setup
- **Personal Account SSH Key:** `~/.ssh/id_ed25519_github_personal`
- **Work Account SSH Key:** `~/.ssh/id_ed25519_github_account1`
- **Global Git Config:** 
  - Name: `nirslife`
  - Email: `nice.days.life@gmail.com`

### SSH Configuration (`~/.ssh/config`)
```bash
# Default GitHub account
Host github-personal
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github_personal

# Work GitHub account
Host github-work
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519_github_work
```

## Step-by-Step Guide: Create New Repository with Different GitHub Account

### Step 1: Choose Your Project Directory
```bash
# Navigate to desired location (not in existing project)
cd ~/Desktop/Projects
# or
cd ~/Documents/Projects
# or create new directory
mkdir ~/Desktop/NewProject && cd ~/Desktop/NewProject
```

### Step 2: Initialize Git Repository
```bash
# Initialize new git repository
git init

# Create initial files
touch README.md
echo "# New Project" > README.md
```

### Step 3: Configure Local Git Settings for This Repository
Choose which account to use and configure accordingly:

#### Option A: Use Personal Account
```bash
# Set local git config for personal account
git config user.name "nirslife"
git config user.email "nice.days.life@gmail.com"
```

#### Option B: Use Work Account
```bash
# Set local git config for work account
git config user.name "YourWorkUsername"
git config user.email "your.work@email.com"
```

### Step 4: Create Repository on GitHub
1. Go to GitHub.com
2. Log into the desired account (personal or work)
3. Click "New Repository"
4. Name your repository
5. Choose public/private
6. **DO NOT** initialize with README (we already have one)
7. Click "Create repository"

### Step 5: Add Remote Origin
Use the appropriate SSH host alias based on which account you want to use:

#### For Personal Account:
```bash
git remote add origin git@github-personal:nirslife/your-repository-name.git
```

#### For Work Account:
```bash
git remote add origin git@github-work:YourWorkUsername/your-repository-name.git
```

### Step 6: Add, Commit, and Push
```bash
# Add files
git add .

# Commit with message
git commit -m "Initial commit"

# Push to GitHub
git push -u origin main
```

## VS Code Integration

### Opening New Project in VS Code
```bash
# Open VS Code in the new project directory
code .
```

### VS Code Git Configuration
VS Code will automatically detect the local git configuration you set in Step 3.

### Recommended VS Code Extensions for Multi-Account Git
- **GitLens** - Enhanced Git capabilities
- **Git Graph** - Visualize Git repository
- **Git History** - View file history

## Verification Commands

### Check Current Repository Configuration
```bash
# Check which remote is configured
git remote -v

# Check local git settings
git config user.name
git config user.email

# Check which SSH key will be used
ssh -T git@github-personal  # For personal account
ssh -T git@github-work      # For work account
```

### Verify SSH Connection
```bash
# Test personal account connection
ssh -T git@github-personal

# Test work account connection  
ssh -T git@github-work
```

Expected response: `Hi [username]! You've successfully authenticated, but GitHub does not provide shell access.`

## Quick Reference Commands

### Clone Existing Repository
```bash
# Clone with personal account
git clone git@github-personal:username/repository.git

# Clone with work account
git clone git@github-work:username/repository.git
```

### Switch Account for Existing Repository
```bash
# Change remote URL to use different account
git remote set-url origin git@github-personal:username/repository.git
# or
git remote set-url origin git@github-work:username/repository.git

# Update local git config
git config user.name "NewUsername"
git config user.email "new.email@domain.com"
```

## Troubleshooting

### Common Issues

1. **Permission Denied (publickey)**
   - Check SSH key is added to correct GitHub account
   - Verify SSH agent: `ssh-add -l`
   - Add key if needed: `ssh-add ~/.ssh/id_ed25519_github_personal`

2. **Wrong Account Being Used**
   - Check remote URL: `git remote -v`
   - Verify local config: `git config user.email`
   - Test SSH connection: `ssh -T git@github-personal`

3. **SSH Host Not Found**
   - Verify `~/.ssh/config` file exists and is correctly formatted
   - Check SSH key file paths are correct

### Useful Git Commands
```bash
# View all configurations
git config --list

# View global configurations
git config --global --list

# View local repository configurations
git config --local --list

# Remove global configuration
git config --global --unset user.name

# See which files are tracked
git ls-files
```

## Security Best Practices

1. **Never commit sensitive information**
2. **Use different SSH keys for different accounts**
3. **Keep SSH keys secure and never share them**
4. **Regularly rotate SSH keys**
5. **Use repository-specific git configurations**

## Example Workflow

```bash
# 1. Create new project directory
mkdir ~/Desktop/MyNewProject
cd ~/Desktop/MyNewProject

# 2. Initialize git
git init

# 3. Set local git config for work account
git config user.name "WorkUsername"
git config user.email "work@company.com"

# 4. Create initial files
echo "# My New Project" > README.md
touch .gitignore

# 5. Add remote (work account)
git remote add origin git@github-work:WorkUsername/my-new-project.git

# 6. Initial commit and push
git add .
git commit -m "Initial commit"
git push -u origin main

# 7. Open in VS Code
code .
```

## Additional Commands for Your Current Setup

### Check Your Current SSH Keys
```bash
# List all SSH keys
ls -la ~/.ssh/

# Check which keys are loaded in SSH agent
ssh-add -l

# Add specific key to SSH agent if needed
ssh-add ~/.ssh/id_ed25519_github_personal
ssh-add ~/.ssh/id_ed25519_github_account1
```

### Test Both Accounts
```bash
# Test personal account
ssh -T git@github-personal

# Test work account (note: your config shows github-work but key file shows account1)
ssh -T git@github-work
```

## VS Code Workspace Settings for Multi-Account Projects

Create a `.vscode/settings.json` in each project to specify Git settings:

```json
{
    "git.defaultCloneDirectory": "./",
    "git.enableCommitSigning": false,
    "terminal.integrated.env.osx": {
        "GIT_AUTHOR_NAME": "YourSpecificName",
        "GIT_AUTHOR_EMAIL": "your.specific@email.com"
    }
}
```

---

**Created:** July 27, 2025  
**Last Updated:** July 27, 2025  
**System:** macOS with VS Code  
**Current Directory:** `/Users/nirsixadmin/Desktop/Python/TextToSpeech/venv`
