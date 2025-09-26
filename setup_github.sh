#!/bin/bash
# GitHub Repository Setup Script
# This script helps you create and push your project to GitHub

set -e  # Exit on any error

# Configuration
REPO_NAME="https-self-signed-client"
GITHUB_USERNAME="mrpuurple"
PROJECT_DESCRIPTION="Python HTTPS client for self-signed certificates with IoT device support"

echo "🚀 GitHub Repository Setup"
echo "=========================="
echo "Repository: $REPO_NAME"
echo "Username: $GITHUB_USERNAME"
echo "Description: $PROJECT_DESCRIPTION"
echo ""

# Step 1: Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "📁 Git repository already exists"
fi

# Step 2: Check if we have any changes to commit
echo "📋 Checking for changes to commit..."
if git diff --quiet && git diff --staged --quiet; then
    echo "⚠️  No changes to commit"
else
    echo "📝 Changes detected, preparing commit..."
fi

# Step 3: Add all files (respecting .gitignore)
echo "📦 Adding files to git..."
git add .
echo "✅ Files added"

# Step 4: Show what will be committed
echo "📋 Files to be committed:"
git status --porcelain

# Step 5: Create commit
echo ""
read -p "📝 Enter commit message (default: 'Initial commit - HTTPS self-signed certificate client'): " COMMIT_MESSAGE
COMMIT_MESSAGE=${COMMIT_MESSAGE:-"Initial commit - HTTPS self-signed certificate client"}

echo "💾 Creating commit..."
git commit -m "$COMMIT_MESSAGE"
echo "✅ Commit created"

# Step 6: Check if remote exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "🔗 Remote origin already exists:"
    git remote get-url origin
else
    echo "🔗 Adding remote origin..."
    git remote add origin "https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "✅ Remote origin added"
fi

# Step 7: Instructions for GitHub
echo ""
echo "🌐 Next Steps - Create GitHub Repository:"
echo "========================================="
echo ""
echo "1. Go to: https://github.com/new"
echo "2. Repository name: $REPO_NAME"
echo "3. Description: $PROJECT_DESCRIPTION"
echo "4. Set to Public (recommended) or Private"
echo "5. ⚠️  DO NOT initialize with README, .gitignore, or license (we already have them)"
echo "6. Click 'Create repository'"
echo ""
echo "7. After creating the repository, run:"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""
echo "Or copy and paste this complete setup:"
echo "======================================"
echo ""
echo "# Set main branch and push"
echo "git branch -M main"
echo "git push -u origin main"
echo ""
echo "🎉 Your repository will be available at:"
echo "https://github.com/$GITHUB_USERNAME/$REPO_NAME"
echo ""

# Step 8: Optional - open GitHub in browser
read -p "🌐 Open GitHub in browser to create repository? (y/N): " OPEN_BROWSER
if [[ $OPEN_BROWSER =~ ^[Yy]$ ]]; then
    if command -v open >/dev/null 2>&1; then
        open "https://github.com/new"
    elif command -v xdg-open >/dev/null 2>&1; then
        xdg-open "https://github.com/new"
    else
        echo "Please manually open: https://github.com/new"
    fi
fi

echo ""
echo "✨ Setup complete! Follow the instructions above to create your GitHub repository."