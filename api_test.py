#!/usr/bin/env python3
"""
Test the specific API endpoint /api/v1/status on your local site.
"""
import json
import os
import warnings
from pathlib import Path
from typing import Any, Dict

import httpx


def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


# Load .env file at module level
load_env_file()


def test_api_endpoint() -> Dict[str, Any]:
    """
    Test the /api/v1/status endpoint specifically.
    
    Returns:
        API response details
    """
    # Your site details
    base_url = "https://192.168.0.113"
    endpoint = "/api/v1/status"
    full_url = f"{base_url}{endpoint}"
    username = os.getenv("DEVICE_USERNAME", "your_username")
    password = os.getenv("DEVICE_PASSWORD", "your_password")
    
    # Disable SSL warnings for self-signed certificate
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    print(f"🔗 Testing API Endpoint")
    print(f"📍 URL: {full_url}")
    print(f"👤 Auth: {username}:{'*' * len(password)}")
    print("=" * 50)
    
    try:
        with httpx.Client(
            verify=False,  # Accept self-signed certificate
            follow_redirects=True,
            timeout=30.0
        ) as client:
            
            # Make authenticated request to the API endpoint
            response = client.get(
                full_url,
                auth=(username, password),
                headers={
                    'User-Agent': 'API-Test-Client/1.0',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Content-Type': 'application/json'
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
                'server': response.headers.get('server', 'Unknown'),
                'headers': dict(response.headers)
            }
            
            # Try to parse JSON response
            try:
                if 'application/json' in response.headers.get('content-type', ''):
                    result['json_data'] = response.json()
                    result['formatted_json'] = json.dumps(response.json(), indent=2)
                else:
                    result['text_content'] = response.text
            except json.JSONDecodeError:
                result['text_content'] = response.text
            except Exception:
                result['raw_content'] = f"<Binary content: {len(response.content)} bytes>"
            
            return result
            
    except httpx.HTTPStatusError as e:
        return {
            'success': False,
            'error': f"HTTP {e.response.status_code}: {e.response.reason_phrase}",
            'status_code': e.response.status_code,
            'response_headers': dict(e.response.headers),
            'response_content': e.response.text[:1000] if hasattr(e.response, 'text') else None
        }
    except httpx.RequestError as e:
        return {
            'success': False,
            'error': f"Request error: {str(e)}",
            'error_type': 'connection'
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Unexpected error: {str(e)}",
            'error_type': 'unknown'
        }


def test_multiple_api_endpoints():
    """Test multiple potential API endpoints."""
    base_url = "https://192.168.0.113"
    username = os.getenv("DEVICE_USERNAME", "your_username")
    password = os.getenv("DEVICE_PASSWORD", "your_password")
    
    # Potential API endpoints to test
    api_endpoints = [
        "/api/v1/status",
        "/api/status",
        "/api/v1/info",
        "/api/v1/health",
        "/api/v1/version",
        "/status",
        "/health",
        "/info"
    ]
    
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    print(f"\n🔍 Testing Multiple API Endpoints")
    print("=" * 40)
    
    results = {}
    
    with httpx.Client(verify=False, follow_redirects=True, timeout=15) as client:
        for endpoint in api_endpoints:
            url = f"{base_url}{endpoint}"
            
            try:
                response = client.get(
                    url, 
                    auth=(username, password),
                    headers={'Accept': 'application/json, text/plain, */*'}
                )
                
                results[endpoint] = {
                    'status_code': response.status_code,
                    'content_type': response.headers.get('content-type', 'Unknown'),
                    'content_length': len(response.content),
                    'success': response.status_code == 200
                }
                
                # Try to get JSON if it's an API endpoint
                if response.status_code == 200 and 'json' in response.headers.get('content-type', ''):
                    try:
                        results[endpoint]['json_preview'] = response.json()
                    except:
                        results[endpoint]['text_preview'] = response.text[:200]
                elif response.status_code == 200:
                    results[endpoint]['text_preview'] = response.text[:200]
                
                status_emoji = "✅" if response.status_code == 200 else "📄" if response.status_code < 400 else "❌"
                print(f"   {status_emoji} {endpoint}: {response.status_code} ({response.headers.get('content-type', 'Unknown')})")
                
            except Exception as e:
                results[endpoint] = {'error': str(e)}
                print(f"   ❌ {endpoint}: Error - {str(e)}")
    
    return results


def main():
    """Main function to test the API endpoints."""
    print("🚀 API Endpoint Testing")
    print("=" * 25)
    
    # Test the specific known endpoint
    print("1️⃣  Testing Known Endpoint: /api/v1/status")
    result = test_api_endpoint()
    
    if result['success']:
        print("✅ API Request Successful!")
        print(f"📊 Status: {result['status_code']} {result['reason_phrase']}")
        print(f"🌐 Final URL: {result['final_url']}")
        print(f"📄 Content Type: {result['content_type']}")
        print(f"📏 Content Length: {result['content_length']:,} bytes")
        print(f"⏱️  Response Time: {result['elapsed_time']:.3f} seconds")
        print(f"🖥️  Server: {result['server']}")
        
        # Show the API response
        if 'json_data' in result:
            print(f"\n📋 JSON Response:")
            print(result['formatted_json'])
        elif 'text_content' in result:
            print(f"\n📄 Text Response:")
            print(result['text_content'][:1000])
        
        # Show response headers
        print(f"\n🔧 Response Headers:")
        for key, value in result['headers'].items():
            if key.lower() in ['content-type', 'server', 'date', 'cache-control', 'x-powered-by']:
                print(f"   {key}: {value}")
        
    else:
        print("❌ API Request Failed!")
        print(f"🚫 Error: {result['error']}")
        
        if 'response_content' in result and result['response_content']:
            print(f"\n📄 Server Response:")
            print(result['response_content'])
        
        if 'response_headers' in result:
            print(f"\n🔧 Response Headers:")
            for key, value in result['response_headers'].items():
                print(f"   {key}: {value}")
    
    # Test multiple endpoints to discover more
    print(f"\n{'='*50}")
    print("2️⃣  Discovering Other API Endpoints")
    endpoint_results = test_multiple_api_endpoints()
    
    # Show successful API endpoints
    successful_endpoints = [ep for ep, info in endpoint_results.items() 
                          if isinstance(info, dict) and info.get('success')]
    
    if successful_endpoints:
        print(f"\n🎯 Working API Endpoints ({len(successful_endpoints)} found):")
        for endpoint in successful_endpoints:
            info = endpoint_results[endpoint]
            print(f"   ✅ {endpoint}")
            print(f"      📄 {info['content_type']} ({info['content_length']:,} bytes)")
            
            # Show JSON preview if available
            if 'json_preview' in info:
                print(f"      🔍 Preview: {str(info['json_preview'])[:100]}...")
            elif 'text_preview' in info:
                print(f"      🔍 Preview: {info['text_preview'][:100]}...")
    else:
        print("\n❌ No working API endpoints found")
    
    print(f"\n{'='*50}")
    print("✨ API testing completed!")


if __name__ == "__main__":
    main()