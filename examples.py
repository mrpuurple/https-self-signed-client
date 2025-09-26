import socket
import ssl
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx


def simple_https_get(url: str) -> None:
    """
    Simple HTTPS GET request example.
    
    Args:
        url: The HTTPS URL to fetch
    """
    print(f"🌐 Fetching: {url}")
    
    try:
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            
            print(f"✅ Status: {response.status_code}")
            print(f"📊 Content-Type: {response.headers.get('content-type')}")
            print(f"📏 Content Length: {len(response.content)} bytes")
            print(f"⏱️  Response Time: {response.elapsed.total_seconds():.3f}s")
            
            # Show first 300 characters of content
            content = response.text[:300]
            print(f"\n📄 Content Preview:\n{content}")
            if len(response.text) > 300:
                print("... (truncated)")
                
    except httpx.HTTPError as e:
        print(f"❌ HTTP Error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")


def get_ssl_certificate_info(hostname: str, port: int = 443) -> Dict[str, Any]:
    """
    Get SSL certificate information for a hostname.
    
    Args:
        hostname: The hostname to check
        port: The port to connect to
        
    Returns:
        Dictionary with certificate information
    """
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect and get certificate
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
                version = ssock.version()
                
                return {
                    'ssl_version': version,
                    'cipher_suite': cipher[0] if cipher else None,
                    'cipher_strength': cipher[2] if cipher else None,
                    'subject': dict(x[0] for x in cert.get('subject', [])),
                    'issuer': dict(x[0] for x in cert.get('issuer', [])),
                    'serial_number': cert.get('serialNumber'),
                    'valid_from': cert.get('notBefore'),
                    'valid_until': cert.get('notAfter'),
                    'san': cert.get('subjectAltName', [])
                }
    except Exception as e:
        return {'error': str(e)}


def https_with_ssl_info(url: str) -> None:
    """
    Make HTTPS request and show SSL certificate information.
    
    Args:
        url: The HTTPS URL to fetch
    """
    print(f"\n🔒 HTTPS Request with SSL Info: {url}")
    print("=" * 60)
    
    # Parse URL to get hostname
    parsed = urlparse(url)
    hostname = parsed.hostname
    
    if not hostname:
        print("❌ Invalid URL")
        return
    
    # Get SSL certificate info
    print("🔍 Checking SSL Certificate...")
    ssl_info = get_ssl_certificate_info(hostname)
    
    if 'error' not in ssl_info:
        print(f"🔒 SSL Version: {ssl_info['ssl_version']}")
        print(f"🔐 Cipher Suite: {ssl_info['cipher_suite']}")
        print(f"💪 Cipher Strength: {ssl_info['cipher_strength']} bits")
        print(f"📋 Subject: {ssl_info['subject'].get('commonName', 'N/A')}")
        print(f"🏢 Issuer: {ssl_info['issuer'].get('commonName', 'N/A')}")
        print(f"📅 Valid From: {ssl_info['valid_from']}")
        print(f"📅 Valid Until: {ssl_info['valid_until']}")
        
        # Show Subject Alternative Names if present
        if ssl_info['san']:
            print(f"🌐 SAN: {[name[1] for name in ssl_info['san'] if name[0] == 'DNS']}")
    else:
        print(f"❌ SSL Error: {ssl_info['error']}")
    
    print("\n📡 Making HTTPS Request...")
    simple_https_get(url)


def custom_headers_example() -> None:
    """Example of making HTTPS request with custom headers."""
    print("\n🎛️  Custom Headers Example")
    print("=" * 40)
    
    url = "https://api.github.com/users/octocat"
    headers = {
        "User-Agent": "HTTPS-Test-Client/1.0",
        "Accept": "application/vnd.github.v3+json",
        "X-Custom-Header": "test-value"
    }
    
    try:
        with httpx.Client() as client:
            response = client.get(url, headers=headers)
            response.raise_for_status()
            
            print(f"✅ GitHub API Response: {response.status_code}")
            
            # Parse JSON response
            data = response.json()
            print(f"👤 User: {data.get('login')}")
            print(f"📍 Location: {data.get('location', 'Not specified')}")
            print(f"🏢 Company: {data.get('company', 'Not specified')}")
            print(f"📊 Public Repos: {data.get('public_repos')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Main function demonstrating various HTTPS client examples."""
    print("🚀 HTTPS Client Examples with httpx")
    print("=" * 50)
    
    # Example 1: Simple HTTPS GET
    print("\n1️⃣  Simple HTTPS GET Request")
    print("-" * 30)
    simple_https_get("https://www.google.com")
    
    # Example 2: HTTPS with SSL certificate info
    https_with_ssl_info("https://github.com")
    
    # Example 3: API request with custom headers
    custom_headers_example()
    
    # Example 4: JSON API
    print("\n4️⃣  JSON API Example")
    print("-" * 25)
    simple_https_get("https://jsonplaceholder.typicode.com/users/1")
    
    print(f"\n{'='*50}")
    print("✨ All examples completed!")


if __name__ == "__main__":
    main()