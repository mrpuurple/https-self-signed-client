#!/usr/bin/env python3
"""
Certificate utility for downloading and trusting self-signed certificates.
"""
import os
import socket
import ssl
import subprocess
import sys
from pathlib import Path

import httpx


def download_certificate(hostname: str, port: int = 443, output_file: str = None) -> str:
    """
    Download certificate from a server using OpenSSL.
    
    Args:
        hostname: Server hostname or IP
        port: Server port
        output_file: Output file path (optional)
        
    Returns:
        Path to the downloaded certificate file
    """
    if not output_file:
        output_file = f"{hostname.replace('.', '_')}_cert.pem"
    
    print(f"📥 Downloading certificate from {hostname}:{port}")
    
    try:
        # Use openssl to get the certificate
        cmd = [
            'openssl', 's_client', 
            '-connect', f'{hostname}:{port}',
            '-showcerts', '-servername', hostname
        ]
        
        print(f"🔧 Running: {' '.join(cmd)}")
        
        # Run openssl command
        result = subprocess.run(
            cmd, 
            input='',
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            # Extract certificate from output
            output_lines = result.stdout.split('\n')
            cert_lines = []
            in_cert = False
            
            for line in output_lines:
                if '-----BEGIN CERTIFICATE-----' in line:
                    in_cert = True
                    cert_lines.append(line)
                elif '-----END CERTIFICATE-----' in line:
                    cert_lines.append(line)
                    break  # Take only the first certificate
                elif in_cert:
                    cert_lines.append(line)
            
            if cert_lines:
                cert_content = '\n'.join(cert_lines)
                
                with open(output_file, 'w') as f:
                    f.write(cert_content)
                
                print(f"✅ Certificate saved to: {output_file}")
                return output_file
            else:
                print("❌ No certificate found in output")
                return None
        else:
            print(f"❌ OpenSSL failed: {result.stderr}")
            return None
            
    except subprocess.TimeoutExpired:
        print("❌ Timeout while downloading certificate")
        return None
    except FileNotFoundError:
        print("❌ OpenSSL not found. Please install OpenSSL.")
        return None
    except Exception as e:
        print(f"❌ Error downloading certificate: {e}")
        return None


def trust_certificate_macos(cert_file: str) -> bool:
    """
    Trust certificate on macOS by adding to system keychain.
    
    Args:
        cert_file: Path to certificate file
        
    Returns:
        True if successful
    """
    if not os.path.exists(cert_file):
        print(f"❌ Certificate file not found: {cert_file}")
        return False
    
    print(f"🔐 Adding certificate to macOS system keychain...")
    
    try:
        cmd = [
            'sudo', 'security', 'add-trusted-cert',
            '-d', '-r', 'trustRoot',
            '-k', '/Library/Keychains/System.keychain',
            cert_file
        ]
        
        print(f"🔧 Running: {' '.join(cmd)}")
        print("⚠️  You may be prompted for your admin password...")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Certificate added to system trust store")
            return True
        else:
            print(f"❌ Failed to add certificate: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error trusting certificate: {e}")
        return False


def test_with_trusted_cert(hostname: str, port: int = 443, follow_redirects: bool = True):
    """
    Test HTTPS connection after trusting certificate.
    
    Args:
        hostname: Server hostname or IP
        port: Server port
        follow_redirects: Whether to follow redirects
    """
    print(f"\n🧪 Testing connection to {hostname}:{port}")
    
    url = f"https://{hostname}:{port}" if port != 443 else f"https://{hostname}"
    
    try:
        with httpx.Client(
            verify=True,  # Now we should verify since cert is trusted
            follow_redirects=follow_redirects,
            timeout=30.0
        ) as client:
            
            response = client.get(url, headers={
                'User-Agent': 'Trusted-HTTPS-Client/1.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            })
            
            print(f"✅ Status: {response.status_code} {response.reason_phrase}")
            print(f"🌐 Final URL: {response.url}")
            print(f"📊 Content-Type: {response.headers.get('content-type', 'Unknown')}")
            print(f"📏 Content Length: {len(response.content)} bytes")
            
            # Show important headers
            important_headers = ['server', 'location', 'www-authenticate', 'set-cookie']
            print(f"\n🔧 Important Headers:")
            for header in important_headers:
                if header in response.headers:
                    print(f"   {header}: {response.headers[header]}")
            
            # Show content preview
            print(f"\n📄 Content Preview:")
            content = response.text[:500]
            print(content)
            if len(response.text) > 500:
                print("... (truncated)")
                
    except httpx.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function for certificate management."""
    hostname = "192.168.0.113"
    port = 443
    
    print("🔐 Certificate Trust Utility")
    print("=" * 40)
    
    # Step 1: Download certificate
    cert_file = download_certificate(hostname, port)
    
    if cert_file:
        print(f"\n📋 Certificate Information:")
        
        # Show certificate details
        try:
            with open(cert_file, 'r') as f:
                cert_content = f.read()
                print(f"Certificate saved with {len(cert_content)} characters")
        except Exception as e:
            print(f"❌ Error reading certificate: {e}")
        
        # Step 2: Ask user if they want to trust it
        response = input(f"\n❓ Do you want to trust this certificate system-wide? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            if sys.platform == 'darwin':  # macOS
                success = trust_certificate_macos(cert_file)
                if success:
                    print("\n🎉 Certificate trusted! Testing connection...")
                    test_with_trusted_cert(hostname, port)
                else:
                    print("\n⚠️  Certificate trust failed, but you can still use verify=False for testing")
            else:
                print("⚠️  Automatic trust is only implemented for macOS")
                print("📖 For Linux, manually copy the certificate to /usr/local/share/ca-certificates/")
                print("   and run: sudo update-ca-certificates")
        else:
            print("\n📖 Certificate downloaded but not trusted.")
            print("   You can use it with the SelfSignedHTTPSClient by setting:")
            print(f"   ca_cert_path='{cert_file}'")
    
    print(f"\n{'='*40}")
    print("✨ Certificate utility completed!")


if __name__ == "__main__":
    main()