#!/usr/bin/env python3
"""
Development helper script for the HTTPS Self-Signed Client project.
Shows available commands and helps with project setup.
"""

def main():
    """Display available development commands and usage."""
    print("🚀 HTTPS Self-Signed Client - Development Helper")
    print("=" * 50)
    
    print("\n📦 uv Commands:")
    print("   uv sync                    - Install/update all dependencies")
    print("   uv add <package>           - Add a new dependency")
    print("   uv remove <package>        - Remove a dependency") 
    print("   uv run python <script>     - Run script in managed environment")
    print("   uv shell                   - Enter managed environment shell")
    print("   uv tree                    - Show dependency tree")
    
    print("\n🧪 Available Scripts:")
    print("   main.py                    - Basic HTTPS client demo")
    print("   api_test.py                - Test IoT device API endpoints")
    print("   local_site_access.py       - Direct connection test")
    print("   iot_client.py              - Full IoT device client")
    print("   cert_utility.py            - Certificate management tools")
    print("   complete_example.py        - Comprehensive SSL demo")
    
    print("\n🏃 Quick Start:")
    print("   uv sync                              # Install dependencies")
    print("   cp .env.example .env                 # Create config file")
    print("   # Edit .env with your credentials")
    print("   uv run python local_site_access.py  # Test connection")
    
    print("\n🔧 Development:")
    print("   uv run python -m pytest             # Run tests (when added)")
    print("   uv run black .                      # Format code")
    print("   uv run ruff check .                 # Lint code")
    
    print("\n📚 More Info:")
    print("   See README.md for detailed usage instructions")
    print("   GitHub: https://github.com/mrpuurple/https-self-signed-client")

if __name__ == "__main__":
    main()