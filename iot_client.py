#!/usr/bin/env python3
"""
IoT Device API Client for your local device at 192.168.0.113
Based on the discovered API structure.
"""
import json
import os
import warnings
from datetime import datetime
from typing import Any, Dict, Optional

import httpx


def load_env_file(env_file=".env"):
    """Load environment variables from .env file"""
    env_vars = {}
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Warning: {env_file} file not found")
    return env_vars


class IoTDeviceClient:
    """Client for interacting with the IoT device API."""
    
    def __init__(self, 
                 device_ip: str = "192.168.0.113",
                 username: str = None,
                 password: str = None,
                 verify_ssl: bool = False):
        """
        Initialize IoT device client.
        
        Args:
            device_ip: IP address of the IoT device
            username: Authentication username
            password: Authentication password
            verify_ssl: Whether to verify SSL certificates
        """
        # Load credentials from .env file
        env_vars = load_env_file()
        
        self.device_ip = device_ip
        self.base_url = f"https://{device_ip}"
        self.username = username or env_vars.get("DEVICE_USERNAME") or os.getenv("DEVICE_USERNAME", "your_username")
        self.password = password or env_vars.get("DEVICE_PASSWORD") or os.getenv("DEVICE_PASSWORD", "your_password")
        self.verify_ssl = verify_ssl
        
        if not verify_ssl:
            warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make an authenticated request to the device API.
        
        Args:
            endpoint: API endpoint (e.g., "/api/v1/status")
            method: HTTP method
            data: Optional data for POST/PUT requests
            
        Returns:
            Response data dictionary
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            with httpx.Client(verify=self.verify_ssl, timeout=30.0) as client:
                
                headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'User-Agent': 'IoT-Device-Client/1.0'
                }
                
                if method.upper() == "GET":
                    response = client.get(url, auth=(self.username, self.password), headers=headers)
                elif method.upper() == "POST":
                    response = client.post(url, auth=(self.username, self.password), 
                                         headers=headers, json=data)
                elif method.upper() == "PUT":
                    response = client.put(url, auth=(self.username, self.password), 
                                        headers=headers, json=data)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")
                
                result = {
                    'success': response.status_code < 400,
                    'status_code': response.status_code,
                    'url': url,
                    'elapsed_time': response.elapsed.total_seconds()
                }
                
                # Parse response
                try:
                    if 'application/json' in response.headers.get('content-type', ''):
                        result['data'] = response.json()
                    else:
                        result['text'] = response.text
                except:
                    result['raw'] = response.content
                
                return result
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get device status information."""
        print("📊 Getting device status...")
        return self._make_request("/api/v1/status")
    
    def get_device_info(self) -> Dict[str, Any]:
        """Get general device information."""
        print("ℹ️  Getting device info...")
        return self._make_request("/info")
    
    def analyze_device_capabilities(self) -> Dict[str, Any]:
        """Analyze the device's capabilities based on status response."""
        status_result = self.get_status()
        
        if not status_result['success']:
            return {'error': 'Could not retrieve device status'}
        
        status_data = status_result.get('data', {})
        
        analysis = {
            'device_type': status_data.get('interface', 'Unknown'),
            'serial_number': status_data.get('serialNumber', 'Unknown'),
            'current_status': status_data.get('status', 'Unknown'),
            'last_updated': status_data.get('time', 'Unknown'),
            'connectivity': {
                'mqtt_broker': status_data.get('mqttBrokerConnectionStatus', 'Unknown'),
                'mqtt_tls': status_data.get('mqttTlsAuthentication', 'Unknown'),
                'kafka_cluster': status_data.get('kafkaClusterConnectionStatus', 'Unknown'),
                'webhooks': status_data.get('eventWebhookStatus', {}).get('status', 'Unknown')
            },
            'capabilities': []
        }
        
        # Determine capabilities based on available connections
        if 'mqttBrokerConnectionStatus' in status_data:
            analysis['capabilities'].append('MQTT Communication')
        if 'kafkaClusterConnectionStatus' in status_data:
            analysis['capabilities'].append('Kafka Streaming')
        if 'eventWebhookStatus' in status_data:
            analysis['capabilities'].append('Event Webhooks')
        
        return analysis
    
    def monitor_device(self, duration_seconds: int = 60, interval_seconds: int = 10):
        """
        Monitor device status over time.
        
        Args:
            duration_seconds: How long to monitor
            interval_seconds: Interval between checks
        """
        import time
        
        print(f"🔍 Monitoring device for {duration_seconds} seconds (every {interval_seconds}s)")
        print("=" * 60)
        
        start_time = time.time()
        checks = 0
        
        while time.time() - start_time < duration_seconds:
            checks += 1
            current_time = datetime.now().strftime("%H:%M:%S")
            
            result = self.get_status()
            
            if result['success']:
                data = result['data']
                print(f"[{current_time}] Check #{checks}: {data['status']} | "
                      f"MQTT: {data['mqttBrokerConnectionStatus']} | "
                      f"Kafka: {data['kafkaClusterConnectionStatus']}")
            else:
                print(f"[{current_time}] Check #{checks}: ERROR - {result.get('error', 'Unknown')}")
            
            time.sleep(interval_seconds)
        
        print(f"\n✅ Monitoring completed ({checks} checks)")


def main():
    """Main function demonstrating IoT device interaction."""
    print("🤖 IoT Device API Client")
    print("=" * 30)
    
    # Create device client
    device = IoTDeviceClient()
    
    print(f"🔗 Connecting to device at {device.device_ip}")
    print(f"👤 Using credentials: {device.username}:{'*' * len(device.password)}")
    print()
    
    # 1. Get current status
    print("1️⃣  Current Device Status")
    print("-" * 25)
    status_result = device.get_status()
    
    if status_result['success']:
        data = status_result['data']
        print(f"✅ Device Online: {status_result['elapsed_time']:.3f}s response time")
        print(f"🏷️  Interface: {data['interface']}")
        print(f"📟 Serial Number: {data['serialNumber']}")
        print(f"⚡ Status: {data['status']}")
        print(f"🕐 Last Update: {data['time']}")
        print()
        print("🔌 Connectivity Status:")
        print(f"   MQTT Broker: {data['mqttBrokerConnectionStatus']}")
        print(f"   MQTT TLS: {data['mqttTlsAuthentication']}")
        print(f"   Kafka Cluster: {data['kafkaClusterConnectionStatus']}")
        print(f"   Event Webhooks: {data['eventWebhookStatus']['status']}")
    else:
        print(f"❌ Failed to get status: {status_result.get('error')}")
    
    # 2. Analyze device capabilities
    print(f"\n2️⃣  Device Analysis")
    print("-" * 20)
    analysis = device.analyze_device_capabilities()
    
    if 'error' not in analysis:
        print(f"🤖 Device Type: {analysis['device_type']}")
        print(f"🔢 Serial: {analysis['serial_number']}")
        print(f"⚡ Current Status: {analysis['current_status']}")
        print(f"📅 Last Seen: {analysis['last_updated']}")
        print()
        print("🛠️  Capabilities:")
        for capability in analysis['capabilities']:
            print(f"   ✅ {capability}")
        print()
        print("🌐 Connectivity:")
        for service, status in analysis['connectivity'].items():
            status_emoji = "🟢" if status == "connected" else "🔴" if status == "disconnected" else "🟡"
            print(f"   {status_emoji} {service.replace('_', ' ').title()}: {status}")
    else:
        print(f"❌ Analysis failed: {analysis['error']}")
    
    # 3. Ask if user wants to monitor
    print(f"\n3️⃣  Device Monitoring")
    print("-" * 20)
    
    try:
        monitor = input("Would you like to monitor the device for 30 seconds? (y/N): ").strip().lower()
        if monitor in ['y', 'yes']:
            device.monitor_device(duration_seconds=30, interval_seconds=5)
        else:
            print("⏭️  Skipping monitoring")
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring cancelled")
    
    print(f"\n{'='*40}")
    print("✨ IoT device interaction completed!")
    
    # Show some additional tips
    print(f"\n💡 Tips for further exploration:")
    print(f"   • The device is an IoT interface with serial {analysis.get('serial_number', 'Unknown')}")
    print(f"   • It supports MQTT, Kafka, and webhook integrations")
    print(f"   • Try exploring other API endpoints like /api/v1/config or /api/v1/settings")
    print(f"   • Monitor connectivity status changes over time")


if __name__ == "__main__":
    main()