#!/usr/bin/env python3
"""
Enhanced HTTPS client for local sites with self-signed certificates and CAP authentication.
"""
import base64
import getpass
import ssl
import warnings
from typing import Any, Dict, Optional

import httpx


class LocalSiteClient:
    """Specialized client for local sites with self-signed certificates."""
    
    def __init__(self, 
                 base_url: str,
                 verify_ssl: bool = False,
                 ca_cert_path: Optional[str] = None,
                 timeout: float = 30.0):
        """
        Initialize client for local site.
        
        Args:
            base_url: Base URL of the local site (e.g., "https://192.168.0.113")
            verify_ssl: Whether to verify SSL certificates
            ca_cert_path: Path to custom CA certificate
            timeout: Request timeout
        """
        self.base_url = base_url.rstrip('/')
        self.verify_ssl = verify_ssl
        self.ca_cert_path = ca_cert_path
        self.timeout = timeout
        self.session_cookies = {}
        
        if not verify_ssl:
            warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    def create_client(self) -> httpx.Client:
        """Create configured httpx client."""
        client_kwargs = {
            'timeout': self.timeout,
            'follow_redirects': True,
            'cookies': self.session_cookies
        }
        
        if self.verify_ssl and self.ca_cert_path:
            client_kwargs['verify'] = self.ca_cert_path
        else:
            client_kwargs['verify'] = self.verify_ssl
        
        return httpx.Client(**client_kwargs)
    
    def get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests."""
        return {
            'User-Agent': 'LocalSite-HTTPS-Client/1.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
    
    def test_connection(self, path: str = "/") -> Dict[str, Any]:
        """
        Test basic connection to the site.
        
        Args:
            path: Path to test (default: "/")
            
        Returns:
            Connection test results
        """
        url = f"{self.base_url}{path}"
        
        print(f"🧪 Testing connection to: {url}")
        
        try:
            with self.create_client() as client:
                response = client.get(url, headers=self.get_default_headers())
                
                result = {
                    'success': True,
                    'url': str(response.url),
                    'status_code': response.status_code,
                    'reason_phrase': response.reason_phrase,
                    'headers': dict(response.headers),
                    'content_length': len(response.content),
                    'elapsed_time': response.elapsed.total_seconds(),
                    'redirects': len(response.history),
                    'final_url': str(response.url)
                }
                
                # Store cookies for session
                if response.cookies:
                    self.session_cookies.update(dict(response.cookies))
                
                # Check for authentication requirements
                if response.status_code == 401:
                    result['requires_auth'] = True
                    result['auth_header'] = response.headers.get('www-authenticate')
                
                # Get content preview
                try:
                    result['content_preview'] = response.text[:1000]
                except:
                    result['content_preview'] = f"<Binary content: {len(response.content)} bytes>"
                
                return result
                
        except httpx.HTTPError as e:
            return {
                'success': False,
                'error': f"HTTP Error: {str(e)}",
                'error_type': 'http'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Connection Error: {str(e)}",
                'error_type': 'connection'
            }
    
    def authenticate_basic(self, username: str, password: str, path: str = "/") -> Dict[str, Any]:
        """
        Attempt basic authentication.
        
        Args:
            username: Username
            password: Password
            path: Path to authenticate against
            
        Returns:
            Authentication results
        """
        url = f"{self.base_url}{path}"
        
        print(f"🔐 Attempting basic authentication to: {url}")
        
        try:
            with self.create_client() as client:
                response = client.get(
                    url,
                    headers=self.get_default_headers(),
                    auth=(username, password)
                )
                
                result = {
                    'success': response.status_code < 400,
                    'status_code': response.status_code,
                    'final_url': str(response.url),
                    'headers': dict(response.headers)
                }
                
                # Store session cookies
                if response.cookies:
                    self.session_cookies.update(dict(response.cookies))
                    result['session_cookies'] = dict(response.cookies)
                
                # Content preview
                try:
                    result['content_preview'] = response.text[:500]
                except:
                    result['content_preview'] = f"<Binary content: {len(response.content)} bytes>"
                
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def explore_common_paths(self) -> Dict[str, Any]:
        """
        Explore common paths on the site.
        
        Returns:
            Results of path exploration
        """
        common_paths = [
            "/",
            "/login",
            "/admin",
            "/index.html",
            "/home",
            "/dashboard",
            "/api",
            "/status",
            "/health"
        ]
        
        results = {}
        
        print("🔍 Exploring common paths...")
        
        for path in common_paths:
            url = f"{self.base_url}{path}"
            
            try:
                with self.create_client() as client:
                    response = client.get(
                        url,
                        headers=self.get_default_headers(),
                        timeout=10  # Shorter timeout for exploration
                    )
                    
                    results[path] = {
                        'status_code': response.status_code,
                        'final_url': str(response.url),
                        'content_type': response.headers.get('content-type', 'Unknown'),
                        'content_length': len(response.content)
                    }
                    
                    print(f"   {path}: {response.status_code} ({response.headers.get('content-type', 'Unknown')})")
                    
            except Exception as e:
                results[path] = {'error': str(e)}
                print(f"   {path}: Error - {str(e)}")
        
        return results
    
    def interactive_session(self):
        """Start an interactive session with the site."""
        print(f"\n🚀 Interactive Session with {self.base_url}")
        print("=" * 50)
        
        # Test initial connection
        result = self.test_connection()
        
        if result['success']:
            print(f"✅ Connection successful!")
            print(f"📊 Status: {result['status_code']} {result['reason_phrase']}")
            print(f"🌐 Final URL: {result['final_url']}")
            
            if result.get('requires_auth'):
                print(f"\n🔐 Authentication required: {result.get('auth_header')}")
                
                username = input("Username: ")
                password = getpass.getpass("Password: ")
                
                auth_result = self.authenticate_basic(username, password)
                
                if auth_result['success']:
                    print(f"✅ Authentication successful!")
                    print(f"📊 Status: {auth_result['status_code']}")
                else:
                    print(f"❌ Authentication failed: {auth_result.get('error', 'Unknown error')}")
            
            # Explore common paths
            print(f"\n" + "="*30)
            self.explore_common_paths()
            
        else:
            print(f"❌ Connection failed: {result['error']}")


def main():
    """Main function for local site testing."""
    print("🏠 Local Site HTTPS Client")
    print("=" * 30)
    
    # Configuration for your local site
    base_url = "https://192.168.0.113"
    
    # Create client (you can set verify_ssl=True if you've trusted the certificate)
    client = LocalSiteClient(
        base_url=base_url,
        verify_ssl=False,  # Set to True if certificate is trusted
        timeout=30.0
    )
    
    # Start interactive session
    client.interactive_session()


if __name__ == "__main__":
    main()