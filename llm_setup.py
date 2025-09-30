#!/usr/bin/env python3
"""
LLM Setup Utility for the Logistics Insight System.
Helps users configure and test LLM integration with multiple provider options.
"""

import os
import sys
import json
from typing import Dict, Any, Optional

def print_header():
    """Print setup utility header."""
    print("🤖 Logistics Insight System - LLM Integration Setup")
    print("=" * 55)
    print()

def check_environment():
    """Check current environment configuration."""
    print("📋 Current Environment Configuration:")
    print("-" * 35)
    
    # Check for .env file
    env_file_exists = os.path.exists('.env')
    print(f"Environment file (.env): {'✅ Found' if env_file_exists else '❌ Not found'}")
    
    # Check environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    llm_provider = os.getenv('LLM_PROVIDER')
    
    print(f"OpenAI API Key: {'✅ Configured' if openai_key else '❌ Not set'}")
    print(f"LLM Provider: {llm_provider if llm_provider else '❌ Not set (will auto-detect)'}")
    print()

def check_dependencies():
    """Check installed dependencies for LLM providers."""
    print("📦 Dependency Status:")
    print("-" * 20)
    
    # Check OpenAI
    try:
        import openai
        print("✅ OpenAI library: Installed")
        openai_available = True
    except ImportError:
        print("❌ OpenAI library: Not installed")
        print("   Install with: pip install openai>=1.0.0")
        openai_available = False
    
    # Check Ollama
    try:
        import ollama
        print("✅ Ollama library: Installed")
        ollama_available = True
    except ImportError:
        print("❌ Ollama library: Not installed")
        print("   Install with: pip install ollama>=0.1.0")
        ollama_available = False
    
    print()
    return openai_available, ollama_available

def test_openai_connection():
    """Test OpenAI API connection."""
    print("🔗 Testing OpenAI Connection:")
    print("-" * 28)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("❌ No API key found. Set OPENAI_API_KEY environment variable.")
        return False
    
    try:
        import openai
        client = openai.OpenAI(api_key=api_key)
        
        # Test with minimal request
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("✅ OpenAI API: Connection successful")
        print(f"   Model: gpt-3.5-turbo")
        print(f"   Tokens used: {response.usage.total_tokens}")
        print(f"   Estimated cost: ${response.usage.total_tokens * 0.0015 / 1000:.6f}")
        return True
        
    except ImportError:
        print("❌ OpenAI library not installed")
        return False
    except Exception as e:
        print(f"❌ OpenAI API: Connection failed - {str(e)}")
        return False

def test_ollama_connection():
    """Test Ollama local connection."""
    print("🔗 Testing Ollama Connection:")
    print("-" * 27)
    
    try:
        import ollama
        
        # List available models
        models = ollama.list()
        available_models = [m['name'] for m in models.get('models', [])]
        
        if not available_models:
            print("❌ No Ollama models found")
            print("   Install a model with: ollama pull llama2")
            return False
        
        print("✅ Ollama: Connection successful")
        print(f"   Available models: {', '.join(available_models[:3])}")
        
        # Test with first available model
        test_model = available_models[0]
        try:
            response = ollama.generate(
                model=test_model,
                prompt="Hello",
                options={'num_predict': 5}
            )
            print(f"   Test generation: Success with {test_model}")
            return True
        except Exception as e:
            print(f"   Test generation: Failed - {str(e)}")
            return False
            
    except ImportError:
        print("❌ Ollama library not installed")
        return False
    except Exception as e:
        print(f"❌ Ollama: Connection failed - {str(e)}")
        return False

def test_system_integration():
    """Test the complete system integration."""
    print("🧪 Testing System Integration:")
    print("-" * 29)
    
    try:
        # Import system components
        from src.llm_integration import LLMIntegration
        
        # Initialize LLM integration
        llm = LLMIntegration()
        
        # Get provider status
        status = llm.get_provider_status()
        
        print(f"Active provider: {status['active_provider']}")
        print("Provider availability:")
        for provider, info in status['providers'].items():
            available = info.get('available', False)
            print(f"  {provider}: {'✅' if available else '❌'}")
        
        # Test query enhancement
        test_query = "Why were deliveries delayed in Mumbai yesterday?"
        result = llm.enhance_query_understanding(test_query)
        
        print(f"\nTest query processing:")
        print(f"  Query: {test_query}")
        print(f"  Intent detected: {result.get('intent', 'unknown')}")
        print(f"  Provider used: {result.get('provider', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ System integration test failed: {str(e)}")
        return False

def create_env_file():
    """Create .env file with user input."""
    print("📝 Creating Environment Configuration:")
    print("-" * 36)
    
    env_content = []
    
    # Ask for preferred provider
    print("Select preferred LLM provider:")
    print("1. OpenAI API (requires API key, ~$5 for demo)")
    print("2. Ollama (local, no API key needed)")
    print("3. Rule-based only (no LLM)")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        env_content.append("LLM_PROVIDER=openai")
        api_key = input("Enter your OpenAI API key: ").strip()
        if api_key:
            env_content.append(f"OPENAI_API_KEY={api_key}")
    elif choice == "2":
        env_content.append("LLM_PROVIDER=ollama")
        model = input("Enter Ollama model name (or press Enter for auto-detect): ").strip()
        if model:
            env_content.append(f"OLLAMA_MODEL={model}")
    elif choice == "3":
        env_content.append("LLM_PROVIDER=rule_based")
    else:
        print("Invalid choice, using auto-detection")
    
    # Write .env file
    if env_content:
        with open('.env', 'w') as f:
            f.write("# Logistics Insight System Configuration\n")
            f.write("# Generated by LLM Setup Utility\n\n")
            f.write('\n'.join(env_content))
            f.write('\n')
        
        print("✅ .env file created successfully")
    else:
        print("❌ No configuration to write")

def show_installation_guide():
    """Show installation guide for different options."""
    print("📚 Installation Guide:")
    print("-" * 20)
    print()
    
    print("OPTION A: OpenAI API Integration")
    print("1. Get API key from: https://platform.openai.com/api-keys")
    print("2. Install library: pip install openai>=1.0.0")
    print("3. Set environment: export OPENAI_API_KEY=your_key_here")
    print("4. Estimated cost: ~$5 for demo usage")
    print()
    
    print("OPTION B: Local LLM with Ollama")
    print("1. Install Ollama: https://ollama.ai/download")
    print("2. Install Python library: pip install ollama>=0.1.0")
    print("3. Download model: ollama pull llama2")
    print("4. No API key needed, runs locally")
    print()
    
    print("OPTION C: Rule-based Approach")
    print("1. No additional installation needed")
    print("2. Uses advanced pattern matching and templates")
    print("3. Always available as fallback")
    print()

def main():
    """Main setup utility function."""
    print_header()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "check":
            check_environment()
            check_dependencies()
            return
        elif command == "test":
            openai_available, ollama_available = check_dependencies()
            print()
            
            if openai_available:
                test_openai_connection()
                print()
            
            if ollama_available:
                test_ollama_connection()
                print()
            
            test_system_integration()
            return
        elif command == "guide":
            show_installation_guide()
            return
        elif command == "config":
            create_env_file()
            return
    
    # Interactive mode
    print("Welcome to the LLM Integration Setup Utility!")
    print()
    print("Available commands:")
    print("  check  - Check current configuration")
    print("  test   - Test LLM provider connections")
    print("  config - Create .env configuration file")
    print("  guide  - Show installation guide")
    print()
    
    while True:
        command = input("Enter command (or 'quit' to exit): ").strip().lower()
        
        if command == "quit":
            break
        elif command == "check":
            print()
            check_environment()
            check_dependencies()
        elif command == "test":
            print()
            openai_available, ollama_available = check_dependencies()
            print()
            
            if openai_available:
                test_openai_connection()
                print()
            
            if ollama_available:
                test_ollama_connection()
                print()
            
            test_system_integration()
        elif command == "config":
            print()
            create_env_file()
        elif command == "guide":
            print()
            show_installation_guide()
        else:
            print("Unknown command. Available: check, test, config, guide, quit")
        
        print()

if __name__ == "__main__":
    main()