#!/usr/bin/env python3
"""
Direct connection to your local site with known credentials.
"""
import os
import warnings
from typing import Any, Dict

import httpx


def connect_to_local_site() -> Dict[str, Any]:
    """
    Connect to your local site with the provided credentials.
    
    Returns:
        Connection results
    """
    # Your site details
    url = "https://192.168.0.113"
    username = os.getenv("DEVICE_USERNAME", "your_username")
    password = os.getenv("DEVICE_PASSWORD", "your_password")
    
    # Disable SSL warnings for self-signed certificate
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    print(f"🔗 Connecting to: {url}")
    print(f"👤 Username: {username}")
    print(f"🔑 Password: {'*' * len(password)}")
    print()
    
    try:
        with httpx.Client(
            verify=False,  # Accept self-signed certificate
            follow_redirects=True,
            timeout=30.0
        ) as client:
            
            # Make authenticated request
            response = client.get(
                url,
                auth=(username, password),
                headers={
                    'User-Agent': 'Local-Site-Client/1.0',
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive'
                }
            )
            
            # Process response
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'reason_phrase': response.reason_phrase,
                'final_url': str(response.url),
                'content_type': response.headers.get('content-type', 'Unknown'),
                'content_length': len(response.content),
                'elapsed_time': response.elapsed.total_seconds(),
                'server': response.headers.get('server', 'Unknown')
            }
            
            # Get important headers
            important_headers = {}
            for header in ['server', 'set-cookie', 'location', 'www-authenticate', 'content-security-policy']:
                if header in response.headers:
                    important_headers[header] = response.headers[header]
            result['important_headers'] = important_headers
            
            # Get content preview
            try:
                if 'text/' in response.headers.get('content-type', '') or 'application/json' in response.headers.get('content-type', ''):
                    result['content_preview'] = response.text[:1000]
                    result['full_content'] = response.text
                else:
                    result['content_preview'] = f"<Binary content: {len(response.content)} bytes>"
            except:
                result['content_preview'] = f"<Could not decode content: {len(response.content)} bytes>"
            
            # Store cookies if any
            if response.cookies:
                result['cookies'] = dict(response.cookies)
            
            return result
            
    except httpx.HTTPStatusError as e:
        return {
            'success': False,
            'error': f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
            'status_code': e.response.status_code,
            'response_content': e.response.text[:500] if hasattr(e.response, 'text') else None
        }
    except httpx.RequestError as e:
        return {
            'success': False,
            'error': f"Request error: {str(e)}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}"
        }


def explore_site_paths(base_url: str, username: str, password: str) -> Dict[str, Any]:
    """
    Explore common paths on the authenticated site.
    
    Args:
        base_url: Base URL of the site
        username: Username for authentication
        password: Password for authentication
        
    Returns:
        Results of path exploration
    """
    common_paths = [
        "/",
        "/ui",
        "/admin",
        "/dashboard",
        "/status",
        "/api",
        "/api/v1/status",  # Known valid endpoint
        "/config",
        "/settings",
        "/logs",
        "/monitor"
    ]
    
    results = {}
    
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    print("🗺️  Exploring site paths...")
    
    with httpx.Client(verify=False, follow_redirects=True, timeout=15) as client:
        for path in common_paths:
            url = f"{base_url}{path}"
            
            try:
                response = client.get(url, auth=(username, password))
                
                results[path] = {
                    'status_code': response.status_code,
                    'final_url': str(response.url),
                    'content_type': response.headers.get('content-type', 'Unknown'),
                    'content_length': len(response.content),
                    'server': response.headers.get('server', 'Unknown')
                }
                
                status_emoji = "✅" if response.status_code == 200 else "📄" if response.status_code < 400 else "❌"
                print(f"   {status_emoji} {path}: {response.status_code} ({response.headers.get('content-type', 'Unknown')})")
                
            except Exception as e:
                results[path] = {'error': str(e)}
                print(f"   ❌ {path}: Error - {str(e)}")
    
    return results


def main():
    """Main function to connect and explore the local site."""
    print("🏠 Local Site Access with Credentials")
    print("=" * 45)
    
    # Connect to the main site
    result = connect_to_local_site()
    
    if result['success']:
        print("✅ Connection Successful!")
        print(f"📊 Status: {result['status_code']} {result['reason_phrase']}")
        print(f"🌐 Final URL: {result['final_url']}")
        print(f"📄 Content Type: {result['content_type']}")
        print(f"📏 Content Length: {result['content_length']:,} bytes")
        print(f"⏱️  Response Time: {result['elapsed_time']:.3f} seconds")
        print(f"🖥️  Server: {result['server']}")
        
        # Show important headers
        if result['important_headers']:
            print(f"\n🔧 Important Headers:")
            for header, value in result['important_headers'].items():
                print(f"   {header}: {value}")
        
        # Show cookies if any
        if 'cookies' in result:
            print(f"\n🍪 Session Cookies:")
            for name, value in result['cookies'].items():
                print(f"   {name}: {value}")
        
        # Show content preview
        print(f"\n📄 Page Content Preview:")
        print("-" * 40)
        print(result['content_preview'])
        if len(result.get('full_content', '')) > 1000:
            print("... (truncated)")
        
        # Explore other paths
        print(f"\n{'='*45}")
        username = os.getenv("DEVICE_USERNAME", "your_username")
        password = os.getenv("DEVICE_PASSWORD", "your_password")
        explore_results = explore_site_paths("https://192.168.0.113", username, password)
        
        # Show successful paths
        successful_paths = [path for path, info in explore_results.items() 
                          if isinstance(info, dict) and info.get('status_code') == 200]
        
        if successful_paths:
            print(f"\n🎯 Accessible Paths ({len(successful_paths)} found):")
            for path in successful_paths:
                info = explore_results[path]
                print(f"   ✅ {path} - {info['content_type']} ({info['content_length']:,} bytes)")
        
    else:
        print("❌ Connection Failed!")
        print(f"🚫 Error: {result['error']}")
        
        if 'response_content' in result and result['response_content']:
            print(f"\n📄 Server Response:")
            print(result['response_content'])
    
    print(f"\n{'='*45}")
    print("✨ Local site access completed!")


if __name__ == "__main__":
    main()