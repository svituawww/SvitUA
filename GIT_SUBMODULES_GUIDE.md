# Git Submodules Management Guide - SvitUA Project

## 🎯 **Project Structure with Git Submodules**

```
SvitUA/ (main repository)
├── svituawww.github.io/ (submodule - GitHub Pages site)
├── scripts-repo/ (submodule - tools and utilities)
├── ptb_parser/ (HTML parser with validation)
├── scripts/ (various HTML processing tools)
├── md_doc/ (project documentation)
└── requirements.txt (Python dependencies)
```

## 📋 **Repository Management**

### **Main Repository (SvitUA)**
- **Purpose**: Overall project management and documentation
- **Contains**: Project structure, documentation, configuration
- **Submodules**: Links to other repositories

### **Submodule 1: svituawww.github.io**
- **Purpose**: GitHub Pages website deployment
- **Remote**: https://github.com/svituawww/svituawww.github.io.git
- **Branch**: main
- **Deployment**: Automatic via GitHub Pages

### **Submodule 2: scripts-repo**
- **Purpose**: Tools, utilities, and scripts
- **Remote**: Local repository (can be pushed to GitHub later)
- **Branch**: master
- **Content**: HTML parsing tools, utilities

## 🚀 **Daily Workflow Commands**

### **1. Clone the Entire Project**
```bash
# Clone main repository with submodules
git clone --recursive https://github.com/yourusername/SvitUA.git
cd SvitUA

# Or if already cloned, initialize submodules
git submodule update --init --recursive
```

### **2. Update All Repositories**
```bash
# Update main repository
git pull origin master

# Update all submodules
git submodule update --remote

# Or update specific submodule
git submodule update --remote svituawww.github.io
git submodule update --remote scripts-repo
```

### **3. Work on Main Repository**
```bash
# Make changes to main repository files
git add .
git commit -m "Update main repository"
git push origin master
```

### **4. Work on Website (svituawww.github.io)**
```bash
# Enter submodule directory
cd svituawww.github.io

# Make changes to website
git add .
git commit -m "Update website"
git push origin main

# Return to main repository and update submodule reference
cd ..
git add svituawww.github.io
git commit -m "Update website submodule"
git push origin master
```

### **5. Work on Scripts (scripts-repo)**
```bash
# Enter submodule directory
cd scripts-repo

# Make changes to scripts
git add .
git commit -m "Update scripts"
git push origin master

# Return to main repository and update submodule reference
cd ..
git add scripts-repo
git commit -m "Update scripts submodule"
git push origin master
```

## 🔧 **Submodule Management Commands**

### **Add New Submodule**
```bash
git submodule add <repository-url> <path>
git add .gitmodules
git commit -m "Add new submodule"
```

### **Remove Submodule**
```bash
# Remove submodule
git submodule deinit <submodule-name>
git rm <submodule-name>
git commit -m "Remove submodule"

# Clean up
rm -rf .git/modules/<submodule-name>
```

### **Update Submodule to Latest**
```bash
# Update to latest commit
git submodule update --remote <submodule-name>

# Or update all submodules
git submodule update --remote
```

### **Check Submodule Status**
```bash
# Check all submodules
git submodule status

# Check specific submodule
git submodule status svituawww.github.io
```

## 📊 **Repository-Specific Workflows**

### **Website Development (svituawww.github.io)**
```bash
cd svituawww.github.io

# Normal git workflow
git add .
git commit -m "Update website"
git push origin main

# Changes will auto-deploy to GitHub Pages
```

### **Scripts Development (scripts-repo)**
```bash
cd scripts-repo

# Add new scripts
git add new_script.py
git commit -m "Add new script"
git push origin master

# Update existing scripts
git add updated_script.py
git commit -m "Update script functionality"
git push origin master
```

### **Main Project Development**
```bash
# Update documentation
git add md_doc/
git commit -m "Update documentation"

# Update configuration
git add requirements.txt
git commit -m "Update dependencies"

# Push changes
git push origin master
```

## 🔄 **Synchronization Workflow**

### **After Making Changes in Submodules**
```bash
# 1. Commit changes in submodule
cd svituawww.github.io
git add .
git commit -m "Website changes"
git push origin main

# 2. Update main repository to point to new submodule commit
cd ..
git add svituawww.github.io
git commit -m "Update website submodule to latest"
git push origin master
```

### **After Pulling Main Repository**
```bash
# 1. Pull main repository
git pull origin master

# 2. Update submodules to match
git submodule update --init --recursive
```

## 🎯 **Best Practices**

### **1. Commit Strategy**
- **Main Repository**: Project structure, documentation, configuration
- **Website Submodule**: Only website-related files
- **Scripts Submodule**: Only tools and utilities

### **2. Branch Strategy**
- **Main**: Use `master` or `main` branch
- **Website**: Use `main` branch (GitHub Pages requirement)
- **Scripts**: Use `master` branch

### **3. File Organization**
```
SvitUA/
├── svituawww.github.io/     # Website files only
├── scripts-repo/            # Scripts and tools only
├── ptb_parser/             # HTML parser project
├── scripts/                # Additional scripts
├── md_doc/                 # Documentation
└── requirements.txt        # Dependencies
```

### **4. Deployment Strategy**
- **Website**: Automatic deployment via GitHub Pages
- **Scripts**: Manual deployment or CI/CD pipeline
- **Main Project**: Documentation and project management

## 🚨 **Common Issues and Solutions**

### **Issue: Submodule Shows as Modified**
```bash
# Check what's modified
git submodule status

# Update submodule to latest
git submodule update --remote

# Or commit submodule changes
cd <submodule-name>
git add .
git commit -m "Update submodule"
git push origin <branch>
cd ..
git add <submodule-name>
git commit -m "Update submodule reference"
```

### **Issue: Submodule Not Updated After Pull**
```bash
# Update submodules after pull
git submodule update --init --recursive
```

### **Issue: Submodule Points to Wrong Commit**
```bash
# Reset submodule to correct commit
git submodule update --init --recursive
```

## 📈 **Benefits of This Setup**

### **✅ Advantages:**
1. **Separate Concerns**: Website and scripts are separate repositories
2. **Independent Deployment**: Website auto-deploys, scripts can have different deployment
3. **Clean History**: Each repository has focused commit history
4. **Team Collaboration**: Different teams can work on different repositories
5. **Version Control**: Each component has its own versioning
6. **Backup**: Multiple repositories provide redundancy

### **✅ Perfect for Your Use Case:**
- **Website**: Automatic GitHub Pages deployment
- **Scripts**: Independent version control and deployment
- **Main Project**: Overall project management and documentation

## 🎯 **Next Steps**

1. **Push Main Repository to GitHub**:
   ```bash
   git remote add origin https://github.com/yourusername/SvitUA.git
   git push -u origin master
   ```

2. **Push Scripts Repository to GitHub**:
   ```bash
   cd scripts-repo
   git remote add origin https://github.com/yourusername/scripts-repo.git
   git push -u origin master
   ```

3. **Update Submodule URLs**:
   ```bash
   git submodule set-url scripts-repo https://github.com/yourusername/scripts-repo.git
   git add .gitmodules
   git commit -m "Update scripts-repo submodule URL"
   ```

This setup gives you the best of both worlds: separate repositories for different concerns, but unified management through git submodules! 🚀 