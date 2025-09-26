# HTTPS Self-Signed Certificate Client

A comprehensive Python toolkit for making HTTPS requests to servers with self-signed certificates, featuring IoT device support, certificate management, and secure credential handling.

## Features

- ✅ Simple HTTPS GET requests
- 🔒 SSL/TLS certificate information extraction
- 🎛️ Custom headers and authentication
- 📊 JSON API interactions
- ⚡ Async support (httpx)
- 🛡️ Error handling and timeouts

## Files

- `main.py` - Basic HTTPS client with multiple test URLs
- `examples.py` - Comprehensive examples with SSL info and custom headers
- `advanced_client.py` - Advanced client class with full SSL inspection

## Installation

```bash
# Install dependencies
pip install httpx

# Or using the project setup
pip install -e .
```

## Configuration

### Set up Credentials

Before using the HTTPS client, configure your device credentials:

```bash
# Option 1: Use the configuration helper
python config_credentials.py

# Option 2: Create .env file manually
cp .env.example .env
# Edit .env with your actual credentials
```

The `.env` file should contain:
```bash
DEVICE_USERNAME=your_username
DEVICE_PASSWORD=your_password
DEVICE_IP=192.168.0.113
```

**⚠️ Security Note**: Never commit `.env` files to git! They are automatically ignored.

## Usage

### Basic Usage
```bash
python main.py
```

### Comprehensive Examples
```bash
python examples.py
```

### Advanced Client
```bash
python advanced_client.py
```

### Local Self-Signed Certificate Testing

For testing with your local device that has a self-signed certificate:

#### Quick API Test
```bash
# Test the specific API endpoint
python api_test.py
```

#### Interactive IoT Device Client
```bash
# Full-featured IoT device interaction
python iot_client.py
```

#### Direct Connection Test
```bash
# Simple connection test with hardcoded flow
python local_site_access.py
```

#### Certificate Management
```bash
# Download and optionally trust the certificate
python cert_utility.py

# Complete SSL demonstration (both methods)
python complete_example.py
```

**⚠️ Before Running**: Make sure to configure your credentials first:
```bash
python config_credentials.py
```

Or set environment variables:
```bash
export DEVICE_USERNAME="your_username"
export DEVICE_PASSWORD="your_password"
export DEVICE_IP="192.168.0.113"  # optional, defaults to this IP
```

## Examples

### Simple HTTPS Request
```python
import httpx

with httpx.Client() as client:
    response = client.get("https://api.github.com/users/octocat")
    print(f"Status: {response.status_code}")
    print(f"Content: {response.json()}")
```

### SSL Certificate Information
```python
import ssl
import socket

def get_ssl_info(hostname, port=443):
    context = ssl.create_default_context()
    with socket.create_connection((hostname, port)) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()
            return {
                'ssl_version': ssock.version(),
                'cipher': ssock.cipher(),
                'subject': dict(x[0] for x in cert['subject']),
                'issuer': dict(x[0] for x in cert['issuer'])
            }
```

### Custom Headers
```python
headers = {
    "User-Agent": "MyClient/1.0",
    "Accept": "application/json",
    "Authorization": "Bearer token"
}

response = client.get(url, headers=headers)
```

## Key Features Demonstrated

1. **Basic HTTPS Requests**: Simple GET requests to various endpoints
2. **SSL/TLS Inspection**: Extract certificate details, cipher suites, and protocol versions
3. **Error Handling**: Proper exception handling for HTTP and network errors
4. **Custom Configuration**: Timeouts, headers, and SSL verification options
5. **Response Processing**: Handle different content types (HTML, JSON, etc.)

## Dependencies

- `httpx` >= 0.24.0 - Modern HTTP client for Python
- `ssl` - Built-in SSL/TLS support
- `socket` - Low-level networking interface

## Security Notes

- Always verify SSL certificates in production (`verify=True`)
- Use proper timeout values to prevent hanging requests
- Be cautious with custom SSL contexts
- Validate and sanitize response data

## License

This project is for educational purposes.
