#!/usr/bin/env python3
"""
Credential configuration helper for HTTPS client project.
This script helps users set up their credentials securely.
"""
import getpass
import os
from pathlib import Path


def create_env_file():
    """Create a .env file with user credentials."""
    print("🔐 HTTPS Client Credential Setup")
    print("=" * 40)
    
    env_file = Path(".env")
    
    if env_file.exists():
        overwrite = input("❓ .env file already exists. Overwrite? (y/N): ").strip().lower()
        if overwrite not in ['y', 'yes']:
            print("✅ Keeping existing .env file")
            return
    
    print("\n📝 Please enter your device credentials:")
    print("   (These will be stored in .env file)")
    
    # Get device IP
    device_ip = input("🌐 Device IP (default: 192.168.0.113): ").strip()
    if not device_ip:
        device_ip = "192.168.0.113"
    
    # Get username
    username = input("👤 Username: ").strip()
    if not username:
        print("❌ Username is required")
        return
    
    # Get password securely
    password = getpass.getpass("🔑 Password: ").strip()
    if not password:
        print("❌ Password is required")
        return
    
    # Create .env file
    env_content = f"""# HTTPS Client Environment Variables
# Generated automatically - do not commit to git!

# Device connection details
DEVICE_IP={device_ip}
DEVICE_USERNAME={username}
DEVICE_PASSWORD={password}

# Optional: Enable debug logging
# DEBUG=true
"""
    
    try:
        with open(".env", "w") as f:
            f.write(env_content)
        
        print(f"\n✅ Created .env file successfully!")
        print(f"📁 Location: {Path('.env').absolute()}")
        print(f"⚠️  Remember: Never commit .env to git!")
        
        # Check if .gitignore exists and includes .env
        gitignore = Path(".gitignore")
        if gitignore.exists():
            gitignore_content = gitignore.read_text()
            if ".env" not in gitignore_content:
                with open(".gitignore", "a") as f:
                    f.write("\n# Environment variables\n.env\n")
                print("✅ Added .env to .gitignore")
        else:
            with open(".gitignore", "w") as f:
                f.write("# Environment variables\n.env\n")
            print("✅ Created .gitignore with .env")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")


def test_credentials():
    """Test the configured credentials."""
    print("\n🧪 Testing Credentials")
    print("=" * 25)
    
    # Load environment variables from .env if it exists
    env_file = Path(".env")
    if env_file.exists():
        print("📁 Loading credentials from .env file...")
        with open(".env") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ[key] = value
    
    # Get credentials
    device_ip = os.getenv("DEVICE_IP", "192.168.0.113")
    username = os.getenv("DEVICE_USERNAME")
    password = os.getenv("DEVICE_PASSWORD")
    
    if not username or not password:
        print("❌ Credentials not found. Run the setup first.")
        return
    
    print(f"🌐 Device IP: {device_ip}")
    print(f"👤 Username: {username}")
    print(f"🔑 Password: {'*' * len(password)}")
    
    # Test connection
    try:
        import warnings

        import httpx
        
        warnings.filterwarnings('ignore', message='Unverified HTTPS request')
        
        url = f"https://{device_ip}/api/v1/status"
        print(f"\n🔗 Testing connection to: {url}")
        
        with httpx.Client(verify=False, timeout=10) as client:
            response = client.get(url, auth=(username, password))
            
            if response.status_code == 200:
                print("✅ Connection successful!")
                data = response.json()
                print(f"📊 Device Status: {data.get('status', 'Unknown')}")
                print(f"🏷️  Interface: {data.get('interface', 'Unknown')}")
            elif response.status_code == 401:
                print("❌ Authentication failed - check credentials")
            else:
                print(f"⚠️  Unexpected response: {response.status_code}")
                
    except ImportError:
        print("⚠️  httpx not installed - install dependencies to test connection")
    except Exception as e:
        print(f"❌ Connection test failed: {e}")


def show_usage():
    """Show usage instructions."""
    print(f"""
💡 Usage Instructions:

1. Set up credentials:
   python config_credentials.py

2. Test your setup:
   python api_test.py

3. Use the IoT client:
   python iot_client.py

🔧 Manual setup (alternative):
   1. Copy .env.example to .env
   2. Edit .env with your credentials
   3. Run any script - it will use the .env values

📚 Available scripts:
   • api_test.py - API endpoint testing
   • iot_client.py - Full IoT device client
   • local_site_access.py - Direct site access
   • complete_example.py - SSL examples
""")


def main():
    """Main function for credential setup."""
    print("🚀 HTTPS Client Project - Credential Setup")
    print("=" * 50)
    
    choice = input("""
What would you like to do?
1. 🔧 Set up credentials (.env file)
2. 🧪 Test current credentials
3. 📖 Show usage instructions
4. 🚪 Exit

Choice (1-4): """).strip()
    
    if choice == "1":
        create_env_file()
    elif choice == "2":
        test_credentials()
    elif choice == "3":
        show_usage()
    elif choice == "4":
        print("👋 Goodbye!")
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    main()