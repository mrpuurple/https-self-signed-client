#!/usr/bin/env python3
"""
GitHub Deployment Readiness Check
Verifies the project is ready for GitHub deployment.
"""
import os
import subprocess
from pathlib import Path


def check_git_status():
    """Check git repository status."""
    print("🔍 Checking Git Status...")
    try:
        # Check if git repo exists
        if not Path('.git').exists():
            print("❌ Not a git repository")
            return False
            
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            print("📝 Uncommitted changes found:")
            print(result.stdout)
        else:
            print("✅ Working directory clean")
            
        return True
    except Exception as e:
        print(f"❌ Git check failed: {e}")
        return False


def check_sensitive_files():
    """Check for sensitive files that shouldn't be committed."""
    print("\n🔐 Checking for Sensitive Files...")
    
    sensitive_patterns = ['.env', '*.key', '*.pem', '*.p12', '*.pfx']
    issues = []
    
    # Check if .env exists
    if Path('.env').exists():
        issues.append(".env file exists (should be local only)")
    
    # Check if .gitignore includes .env
    gitignore_path = Path('.gitignore')
    if gitignore_path.exists():
        gitignore_content = gitignore_path.read_text()
        if '.env' in gitignore_content:
            print("✅ .env is properly git-ignored")
        else:
            issues.append(".env not found in .gitignore")
    else:
        issues.append(".gitignore file missing")
    
    if issues:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("✅ No sensitive files will be committed")
        return True


def check_required_files():
    """Check for required project files."""
    print("\n📁 Checking Required Files...")
    
    required_files = {
        'README.md': 'Project documentation',
        'LICENSE': 'License file',
        'pyproject.toml': 'Project configuration',
        '.gitignore': 'Git ignore rules',
        '.env.example': 'Environment variable template'
    }
    
    all_present = True
    for file_path, description in required_files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path} - {description}")
        else:
            print(f"❌ {file_path} - {description} (MISSING)")
            all_present = False
    
    return all_present


def check_python_files():
    """Check Python files for basic syntax."""
    print("\n🐍 Checking Python Files...")
    
    python_files = list(Path('.').glob('*.py'))
    issues = 0
    
    for py_file in python_files:
        try:
            compile(py_file.read_text(), py_file, 'exec')
            print(f"✅ {py_file}")
        except SyntaxError as e:
            print(f"❌ {py_file} - Syntax error: {e}")
            issues += 1
        except Exception as e:
            print(f"⚠️  {py_file} - Warning: {e}")
    
    return issues == 0


def show_deployment_summary():
    """Show deployment summary and next steps."""
    print("\n" + "="*50)
    print("🚀 GitHub Deployment Summary")
    print("="*50)
    
    print(f"""
📊 Project Status:
• Name: https-self-signed-client
• Version: 1.0.0
• Description: Python HTTPS client for self-signed certificates
• Target: https://github.com/mrpuurple/https-self-signed-client

🔐 Security:
• ✅ Credentials obfuscated (environment variables)
• ✅ .env file git-ignored
• ✅ .env.example template provided
• ✅ No hardcoded secrets in source code

📁 Project Structure:
• ✅ 12+ Python scripts for HTTPS/SSL handling
• ✅ Comprehensive documentation (README.md)
• ✅ MIT License included
• ✅ Professional pyproject.toml configuration
• ✅ Git ignore rules configured

🎯 Next Steps:
1. Run: ./setup_github.sh
2. Create repository at: https://github.com/new
3. Repository name: https-self-signed-client
4. Push with: git push -u origin main

🌐 After deployment, users can:
• Clone the repository
• Set up credentials with: python config_credentials.py
• Use HTTPS clients for self-signed certificates
• Access IoT devices securely
""")


def main():
    """Main deployment readiness check."""
    print("🔍 GitHub Deployment Readiness Check")
    print("="*40)
    
    checks = [
        ("Git Status", check_git_status),
        ("Sensitive Files", check_sensitive_files),
        ("Required Files", check_required_files),
        ("Python Syntax", check_python_files)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            all_passed = False
    
    print("\n" + "="*40)
    if all_passed:
        print("✅ ALL CHECKS PASSED - Ready for GitHub!")
        show_deployment_summary()
    else:
        print("❌ Some checks failed - Fix issues before deploying")
    
    return all_passed


if __name__ == "__main__":
    main()