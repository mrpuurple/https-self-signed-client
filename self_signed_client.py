import os
import socket
import ssl
import warnings
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx


class SelfSignedHTTPSClient:
    """HTTPS client specifically designed for self-signed certificates and local sites."""
    
    def __init__(self, 
                 timeout: float = 30.0,
                 verify_ssl: bool = False,
                 ca_cert_path: Optional[str] = None):
        """
        Initialize client for self-signed certificates.
        
        Args:
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates (False for self-signed)
            ca_cert_path: Path to custom CA certificate file
        """
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.ca_cert_path = ca_cert_path
        
        # Suppress SSL warnings when not verifying
        if not verify_ssl:
            warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    def create_ssl_context(self, hostname: str = None) -> ssl.SSLContext:
        """
        Create custom SSL context for self-signed certificates.
        
        Args:
            hostname: The hostname for SNI (Server Name Indication)
            
        Returns:
            Configured SSL context
        """
        context = ssl.create_default_context()
        
        if not self.verify_ssl:
            # Disable certificate verification for self-signed certificates
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        elif self.ca_cert_path and os.path.exists(self.ca_cert_path):
            # Load custom CA certificate
            context.load_verify_locations(self.ca_cert_path)
        
        return context
    
    def get_certificate_info(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """
        Get certificate information, including self-signed certificates.
        
        Args:
            hostname: The hostname/IP to check
            port: The port to connect to
            
        Returns:
            Certificate information dictionary
        """
        try:
            context = self.create_ssl_context(hostname)
            
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    # Extract certificate details
                    subject = dict(x[0] for x in cert.get('subject', [])) if cert else {}
                    issuer = dict(x[0] for x in cert.get('issuer', [])) if cert else {}
                    
                    # Check if self-signed (issuer == subject)
                    is_self_signed = subject.get('commonName') == issuer.get('commonName')
                    
                    return {
                        'hostname': hostname,
                        'port': port,
                        'ssl_version': version,
                        'cipher_suite': cipher[0] if cipher else None,
                        'cipher_strength': cipher[2] if cipher else None,
                        'is_self_signed': is_self_signed,
                        'subject': subject,
                        'issuer': issuer,
                        'serial_number': cert.get('serialNumber') if cert else None,
                        'valid_from': cert.get('notBefore') if cert else None,
                        'valid_until': cert.get('notAfter') if cert else None,
                        'san': cert.get('subjectAltName', []) if cert else []
                    }
        except Exception as e:
            return {'error': str(e), 'hostname': hostname, 'port': port}
    
    def make_request(self, 
                    method: str,
                    url: str,
                    headers: Optional[Dict[str, str]] = None,
                    data: Optional[Dict[str, Any]] = None,
                    auth: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Make HTTPS request to self-signed certificate site.
        
        Args:
            method: HTTP method
            url: Target URL
            headers: Optional headers
            data: Optional request data
            auth: Optional basic auth tuple (username, password)
            
        Returns:
            Response information dictionary
        """
        result = {
            'url': url,
            'method': method.upper(),
            'success': False
        }
        
        try:
            # Create httpx client with custom SSL context
            client_kwargs = {
                'timeout': self.timeout,
                'verify': self.verify_ssl
            }
            
            # Add custom CA certificate if provided
            if self.ca_cert_path and os.path.exists(self.ca_cert_path):
                client_kwargs['verify'] = self.ca_cert_path
            
            with httpx.Client(**client_kwargs) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers or {},
                    json=data if data else None,
                    auth=auth
                )
                
                response.raise_for_status()
                
                result.update({
                    'success': True,
                    'status_code': response.status_code,
                    'reason_phrase': response.reason_phrase,
                    'headers': dict(response.headers),
                    'content_type': response.headers.get('content-type', 'Unknown'),
                    'content_length': len(response.content),
                    'elapsed_time': response.elapsed.total_seconds(),
                    'content': response.text[:1000] + ('...' if len(response.text) > 1000 else '')
                })
                
        except httpx.HTTPStatusError as e:
            result.update({
                'error': f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
                'status_code': e.response.status_code,
                'response_content': e.response.text[:500] if hasattr(e.response, 'text') else None
            })
        except httpx.RequestError as e:
            result['error'] = f"Request error: {str(e)}"
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
        
        return result
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, auth: Optional[tuple] = None):
        """Make GET request."""
        return self.make_request('GET', url, headers=headers, auth=auth)
    
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, 
             headers: Optional[Dict[str, str]] = None, auth: Optional[tuple] = None):
        """Make POST request."""
        return self.make_request('POST', url, headers=headers, data=data, auth=auth)


def test_local_site(ip_address: str, port: int = 443, username: str = None, password: str = None):
    """
    Test connection to local site with self-signed certificate.
    
    Args:
        ip_address: IP address of the local site
        port: HTTPS port (default: 443)
        username: Username for basic auth (if required)
        password: Password for basic auth (if required)
    """
    print(f"🏠 Testing Local Site: {ip_address}:{port}")
    print("=" * 50)
    
    # Create client that accepts self-signed certificates
    client = SelfSignedHTTPSClient(verify_ssl=False)
    
    # Get certificate information
    print("🔍 Checking SSL Certificate...")
    cert_info = client.get_certificate_info(ip_address, port)
    
    if 'error' not in cert_info:
        print(f"🔒 SSL Version: {cert_info['ssl_version']}")
        print(f"🔐 Cipher Suite: {cert_info['cipher_suite']}")
        print(f"💪 Cipher Strength: {cert_info['cipher_strength']} bits")
        print(f"🏷️  Self-Signed: {'Yes' if cert_info['is_self_signed'] else 'No'}")
        print(f"📋 Subject CN: {cert_info['subject'].get('commonName', 'N/A')}")
        print(f"🏢 Issuer CN: {cert_info['issuer'].get('commonName', 'N/A')}")
        print(f"📅 Valid From: {cert_info['valid_from']}")
        print(f"📅 Valid Until: {cert_info['valid_until']}")
        
        if cert_info['san']:
            san_names = [name[1] for name in cert_info['san'] if name[0] == 'DNS']
            if san_names:
                print(f"🌐 SAN: {san_names}")
    else:
        print(f"❌ Certificate Error: {cert_info['error']}")
    
    # Test HTTPS connection
    print(f"\n📡 Making HTTPS Request...")
    url = f"https://{ip_address}:{port}" if port != 443 else f"https://{ip_address}"
    
    # Prepare authentication if provided
    auth = (username, password) if username and password else None
    
    # Add headers that might be needed for CAP authentication
    headers = {
        'User-Agent': 'Self-Signed-HTTPS-Client/1.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    result = client.get(url, headers=headers, auth=auth)
    
    if result['success']:
        print(f"✅ Status: {result['status_code']} {result['reason_phrase']}")
        print(f"📊 Content-Type: {result['content_type']}")
        print(f"📏 Content Length: {result['content_length']} bytes")
        print(f"⏱️  Response Time: {result['elapsed_time']:.3f}s")
        
        print(f"\n🔧 Response Headers:")
        for key, value in result['headers'].items():
            if key.lower() in ['server', 'www-authenticate', 'location', 'set-cookie']:
                print(f"   {key}: {value}")
        
        print(f"\n📄 Content Preview:")
        print(result['content'][:500])
        if len(result['content']) > 500:
            print("... (truncated)")
    else:
        print(f"❌ Request Failed: {result['error']}")
        if 'response_content' in result and result['response_content']:
            print(f"📄 Response Content: {result['response_content']}")


def create_trust_certificate_guide():
    """Display instructions for trusting self-signed certificates."""
    print("\n📖 Guide: Trusting Self-Signed Certificates")
    print("=" * 50)
    
    print("""
🔧 Method 1: Disable SSL Verification (Testing Only)
   - Use verify_ssl=False in the client
   - ⚠️  WARNING: Only for testing, not production!

🔧 Method 2: Add Certificate to Trust Store
   1. Download the certificate:
      openssl s_client -connect 192.168.0.113:443 -showcerts
   
   2. Save certificate to file (e.g., local-site.crt)
   
   3. On macOS:
      sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain local-site.crt
   
   4. On Linux:
      sudo cp local-site.crt /usr/local/share/ca-certificates/
      sudo update-ca-certificates

🔧 Method 3: Use Custom CA Bundle
   - Create HTTPSClient with ca_cert_path parameter
   - Point to your custom certificate file

🔧 Method 4: Environment Variable
   export REQUESTS_CA_BUNDLE=/path/to/certificate.pem
   export SSL_CERT_FILE=/path/to/certificate.pem
    """)


def main():
    """Main function for testing local self-signed HTTPS site."""
    print("🔐 Self-Signed HTTPS Client")
    print("=" * 40)
    
    # Test your local site
    ip_address = "192.168.0.113"
    
    # You can modify these as needed
    port = 443  # Change if using different port
    username = None  # Add username if CAP auth requires it
    password = None  # Add password if CAP auth requires it
    
    # Test the connection
    test_local_site(ip_address, port, username, password)
    
    # Show guide for trusting certificates
    create_trust_certificate_guide()


if __name__ == "__main__":
    main()