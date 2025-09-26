import socket
import ssl
from typing import Any, Dict, Optional

import httpx


class HTTPSClient:
    """Advanced HTTPS client with SSL/TLS information and custom options."""
    
    def __init__(self, timeout: float = 30.0, verify_ssl: bool = True):
        """
        Initialize the HTTPS client.
        
        Args:
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.timeout = timeout
        self.verify_ssl = verify_ssl
    
    def get_ssl_info(self, hostname: str, port: int = 443) -> Dict[str, Any]:
        """
        Get SSL/TLS certificate information for a hostname.
        
        Args:
            hostname: The hostname to check
            port: The port to connect to (default: 443)
            
        Returns:
            Dictionary containing SSL information
        """
        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate info
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    cipher = ssock.cipher()
                    version = ssock.version()
                    
                    return {
                        'hostname': hostname,
                        'port': port,
                        'ssl_version': version,
                        'cipher': cipher,
                        'certificate': {
                            'subject': dict(x[0] for x in cert['subject']),
                            'issuer': dict(x[0] for x in cert['issuer']),
                            'serial_number': cert['serialNumber'],
                            'not_before': cert['notBefore'],
                            'not_after': cert['notAfter'],
                            'version': cert['version']
                        }
                    }
        except Exception as e:
            return {'error': str(e)}
    
    def make_request(self, 
                    method: str,
                    url: str, 
                    headers: Optional[Dict[str, str]] = None,
                    data: Optional[Dict[str, Any]] = None,
                    show_ssl_info: bool = False) -> Dict[str, Any]:
        """
        Make an HTTPS request with detailed information.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            url: The URL to request
            headers: Optional headers to include
            data: Optional data to send (for POST/PUT requests)
            show_ssl_info: Whether to include SSL certificate information
            
        Returns:
            Dictionary containing response information
        """
        result = {
            'url': url,
            'method': method.upper(),
            'success': False
        }
        
        try:
            # Extract hostname for SSL info
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            hostname = parsed_url.hostname
            
            # Get SSL info if requested
            if show_ssl_info and hostname:
                result['ssl_info'] = self.get_ssl_info(hostname)
            
            # Make the request
            with httpx.Client(verify=self.verify_ssl, timeout=self.timeout) as client:
                response = client.request(
                    method=method,
                    url=url,
                    headers=headers or {},
                    json=data if data else None
                )
                
                # Process response
                response.raise_for_status()
                result.update({
                    'success': True,
                    'status_code': response.status_code,
                    'reason_phrase': response.reason_phrase,
                    'headers': dict(response.headers),
                    'content_type': response.headers.get('content-type', 'Unknown'),
                    'content_length': len(response.content),
                    'encoding': response.encoding,
                    'elapsed_time': response.elapsed.total_seconds(),
                    'http_version': response.http_version,
                    'content': response.text[:1000] + ('...' if len(response.text) > 1000 else '')
                })
                
        except httpx.HTTPStatusError as e:
            result.update({
                'error': f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
                'status_code': e.response.status_code
            })
        except httpx.RequestError as e:
            result['error'] = f"Request error: {str(e)}"
        except Exception as e:
            result['error'] = f"Unexpected error: {str(e)}"
        
        return result
    
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, show_ssl_info: bool = False):
        """Make a GET request."""
        return self.make_request('GET', url, headers=headers, show_ssl_info=show_ssl_info)
    
    def post(self, url: str, data: Optional[Dict[str, Any]] = None, 
             headers: Optional[Dict[str, str]] = None, show_ssl_info: bool = False):
        """Make a POST request."""
        return self.make_request('POST', url, headers=headers, data=data, show_ssl_info=show_ssl_info)


def print_response_info(response_info: Dict[str, Any]) -> None:
    """Pretty print response information."""
    print(f"🌐 {response_info['method']} {response_info['url']}")
    print("=" * 60)
    
    if response_info['success']:
        print(f"✅ Status: {response_info['status_code']} {response_info.get('reason_phrase', '')}")
        print(f"📊 Content Type: {response_info['content_type']}")
        print(f"📏 Content Length: {response_info['content_length']} bytes")
        print(f"⏱️  Response Time: {response_info['elapsed_time']:.3f} seconds")
        print(f"🔌 HTTP Version: {response_info['http_version']}")
        
        # SSL Information
        if 'ssl_info' in response_info and 'error' not in response_info['ssl_info']:
            ssl_info = response_info['ssl_info']
            print(f"\n🔒 SSL/TLS Information:")
            print(f"   Version: {ssl_info['ssl_version']}")
            print(f"   Cipher: {ssl_info['cipher']}")
            if 'certificate' in ssl_info:
                cert = ssl_info['certificate']
                print(f"   Certificate Subject: {cert['subject']}")
                print(f"   Certificate Issuer: {cert['issuer']}")
                print(f"   Valid From: {cert['not_before']}")
                print(f"   Valid Until: {cert['not_after']}")
        
        print(f"\n📄 Response Content Preview:")
        print(response_info['content'])
        
    else:
        print(f"❌ Error: {response_info['error']}")
    
    print("-" * 60)


def demo_advanced_client():
    """Demonstrate the advanced HTTPS client capabilities."""
    print("🚀 Advanced HTTPS Client Demo")
    print("=" * 60)
    
    client = HTTPSClient(timeout=30.0)
    
    # Test URLs with different features
    test_cases = [
        {
            'name': 'Simple GET with SSL info',
            'method': 'get',
            'url': 'https://httpbin.org/json',
            'show_ssl_info': True
        },
        {
            'name': 'GET with custom headers',
            'method': 'get',
            'url': 'https://httpbin.org/headers',
            'headers': {
                'User-Agent': 'Advanced-HTTPS-Client/1.0',
                'X-Custom-Header': 'Test-Value'
            }
        },
        {
            'name': 'POST with JSON data',
            'method': 'post',
            'url': 'https://httpbin.org/post',
            'data': {
                'message': 'Hello from HTTPS client!',
                'timestamp': '2024-01-01T12:00:00Z'
            }
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test['name']}")
        
        if test['method'] == 'get':
            result = client.get(
                test['url'], 
                headers=test.get('headers'),
                show_ssl_info=test.get('show_ssl_info', False)
            )
        elif test['method'] == 'post':
            result = client.post(
                test['url'],
                data=test.get('data'),
                headers=test.get('headers'),
                show_ssl_info=test.get('show_ssl_info', False)
            )
        
        print_response_info(result)


if __name__ == "__main__":
    demo_advanced_client()