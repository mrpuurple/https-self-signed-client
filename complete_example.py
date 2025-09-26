#!/usr/bin/env python3
"""
Complete example for accessing your local site with self-signed certificate.
This shows both methods: with and without trusting the certificate.
"""
import getpass
import ssl
import warnings
from pathlib import Path

import httpx


def test_without_verification():
    """Test connection without SSL verification (quick and dirty)."""
    print("🔓 Method 1: Disable SSL Verification (Testing Only)")
    print("-" * 50)
    
    # Disable SSL warnings 
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    url = "https://192.168.0.113"
    
    try:
        with httpx.Client(verify=False, follow_redirects=True, timeout=30) as client:
            
            # First, try without authentication
            print("🌐 Testing initial connection...")
            response = client.get(url)
            
            print(f"📊 Status: {response.status_code} {response.reason_phrase}")
            print(f"🌐 Final URL: {response.url}")
            
            if response.status_code == 401:
                print("🔐 Authentication required")
                auth_header = response.headers.get('www-authenticate', 'Unknown')
                print(f"   Auth method: {auth_header}")
                
                # Get credentials
                username = input("\n👤 Username: ")
                password = getpass.getpass("🔑 Password: ")
                
                # Try with authentication
                print("\n🔐 Attempting authentication...")
                auth_response = client.get(url, auth=(username, password))
                
                print(f"📊 Auth Status: {auth_response.status_code} {auth_response.reason_phrase}")
                print(f"🌐 Final URL: {auth_response.url}")
                print(f"📄 Content Type: {auth_response.headers.get('content-type', 'Unknown')}")
                print(f"📏 Content Length: {len(auth_response.content)} bytes")
                
                # Show content preview
                if auth_response.status_code == 200:
                    print("\n📄 Content Preview:")
                    content = auth_response.text[:500]
                    print(content)
                    if len(auth_response.text) > 500:
                        print("... (truncated)")
                
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_with_custom_certificate():
    """Test connection using the downloaded certificate."""
    print("\n🔒 Method 2: Use Downloaded Certificate")
    print("-" * 50)
    
    cert_file = "192_168_0_113_cert.pem"
    
    if not Path(cert_file).exists():
        print(f"❌ Certificate file not found: {cert_file}")
        print("   Run cert_utility.py first to download the certificate")
        return False
    
    print(f"📜 Using certificate: {cert_file}")
    
    url = "https://192.168.0.113"
    
    try:
        # Create client with custom certificate
        with httpx.Client(
            verify=cert_file,  # Use our downloaded certificate
            follow_redirects=True,
            timeout=30
        ) as client:
            
            print("🌐 Testing connection with trusted certificate...")
            response = client.get(url)
            
            print(f"📊 Status: {response.status_code} {response.reason_phrase}")
            print(f"🌐 Final URL: {response.url}")
            print(f"✅ SSL Verification: PASSED")
            
            if response.status_code == 401:
                print("🔐 Authentication required")
                
                # Get credentials
                username = input("\n👤 Username: ")
                password = getpass.getpass("🔑 Password: ")
                
                # Try with authentication
                print("\n🔐 Attempting authentication with SSL verification...")
                auth_response = client.get(url, auth=(username, password))
                
                print(f"📊 Auth Status: {auth_response.status_code} {auth_response.reason_phrase}")
                print(f"🌐 Final URL: {auth_response.url}")
                print(f"📄 Content Type: {auth_response.headers.get('content-type', 'Unknown')}")
                print(f"📏 Content Length: {len(auth_response.content)} bytes")
                
                # Show content preview
                if auth_response.status_code == 200:
                    print("\n📄 Content Preview:")
                    content = auth_response.text[:500]
                    print(content)
                    if len(auth_response.text) > 500:
                        print("... (truncated)")
                
            return True
            
    except httpx.ConnectError as e:
        print(f"❌ Connection Error: {e}")
        print("   This might happen if the certificate doesn't match the hostname")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def show_certificate_info():
    """Show information about the downloaded certificate."""
    print("\n📜 Certificate Information")
    print("-" * 30)
    
    cert_file = "192_168_0_113_cert.pem"
    
    if not Path(cert_file).exists():
        print(f"❌ Certificate file not found: {cert_file}")
        return
    
    try:
        # Read and parse certificate
        with open(cert_file, 'rb') as f:
            cert_data = f.read()
        
        # Load certificate using SSL module
        cert = ssl.PEM_cert_to_DER_cert(cert_data.decode())
        
        print(f"📁 File: {cert_file}")
        print(f"📏 Size: {len(cert_data)} bytes")
        print(f"🔐 Format: PEM")
        
        # Try to get more details using openssl if available
        import subprocess
        try:
            result = subprocess.run([
                'openssl', 'x509', '-in', cert_file, '-text', '-noout'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'Subject:' in line:
                        print(f"👤 {line.strip()}")
                    elif 'Issuer:' in line:
                        print(f"🏢 {line.strip()}")
                    elif 'Not Before:' in line:
                        print(f"📅 {line.strip()}")
                    elif 'Not After :' in line:
                        print(f"📅 {line.strip()}")
                        
        except (subprocess.TimeoutExpired, FileNotFoundError):
            print("ℹ️  Install OpenSSL for detailed certificate information")
            
    except Exception as e:
        print(f"❌ Error reading certificate: {e}")


def main():
    """Main function demonstrating both approaches."""
    print("🏠 Local Site HTTPS Access Guide")
    print("=" * 40)
    
    print("""
This example shows two ways to access your local site with self-signed certificate:

1. 🔓 Disable SSL verification (quick but insecure)
2. 🔒 Use the downloaded certificate (secure)

Your local site details:
• IP: 192.168.0.113
• Protocol: HTTPS (TLS 1.3)
• Certificate: Self-signed
• Authentication: Basic Auth (CAP)
    """)
    
    # Show certificate info
    show_certificate_info()
    
    # Ask user which method to try
    print("\n" + "="*40)
    choice = input("Which method would you like to try? (1 or 2, or 'both'): ").strip().lower()
    
    if choice in ['1', 'both']:
        success1 = test_without_verification()
    else:
        success1 = True
    
    if choice in ['2', 'both']:
        success2 = test_with_custom_certificate()
    else:
        success2 = True
    
    print("\n" + "="*40)
    print("✨ Testing completed!")
    
    if choice == 'both':
        print(f"Method 1 (No verification): {'✅ Success' if success1 else '❌ Failed'}")
        print(f"Method 2 (Custom cert): {'✅ Success' if success2 else '❌ Failed'}")
    
    print("""
💡 Tips for production use:
• Method 1 is only for testing - never use verify=False in production
• Method 2 is secure and recommended
• Consider adding the certificate to your system's trust store for system-wide trust
• For automation, store credentials securely (environment variables, key management)
    """)


if __name__ == "__main__":
    main()