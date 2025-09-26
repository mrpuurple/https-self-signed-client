import httpx


def fetch_webpage(url: str) -> None:
    """
    Fetch a webpage using HTTPS with httpx.
    
    Args:
        url: The URL to fetch (should be HTTPS)
    """
    try:
        print(f"Fetching: {url}")
        
        # Create an HTTPS client
        with httpx.Client() as client:
            response = client.get(url)
            
            # Check if request was successful
            response.raise_for_status()
            
            print(f"Status Code: {response.status_code}")
            print(f"Content Type: {response.headers.get('content-type', 'Unknown')}")
            print(f"Content Length: {len(response.content)} bytes")
            print(f"Response Headers: {dict(response.headers)}")
            print("\n--- Response Content (first 500 chars) ---")
            print(response.text[:500])
            if len(response.text) > 500:
                print("... (truncated)")
                
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e.response.status_code} - {e.response.reason_phrase}")
    except httpx.RequestError as e:
        print(f"Request error occurred: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def main():
    """Main function to demonstrate HTTPS client."""
    print("HTTPS Client with httpx")
    print("=" * 30)
    
    # Example HTTPS URLs to test
    test_urls = [
        "https://httpbin.org/get",  # Simple JSON response
        "https://www.google.com",   # Popular website
        "https://jsonplaceholder.typicode.com/posts/1"  # Sample API
    ]
    
    for url in test_urls:
        print(f"\n{'='*50}")
        fetch_webpage(url)
        print("-" * 50)


if __name__ == "__main__":
    main()
