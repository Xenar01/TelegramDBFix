#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API Connection Test - Verify Claude or OpenAI API is working
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ .env file loaded")
except ImportError:
    print("⚠️  python-dotenv not installed. Installing...")
    os.system("pip install python-dotenv")
    from dotenv import load_dotenv
    load_dotenv()

def test_claude_api():
    """Test Anthropic Claude API"""
    api_key = os.getenv('ANTHROPIC_API_KEY')

    if not api_key or api_key == 'your-api-key-here':
        return False, "API key not configured"

    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        # Test with simple Arabic message using Claude 3 Haiku
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": "قل 'مرحبا' بالعربية"
                }
            ]
        )

        response_text = message.content[0].text
        return True, f"Success! Response: {response_text}"

    except ImportError:
        return False, "anthropic package not installed. Run: pip install anthropic"
    except Exception as e:
        return False, f"Error: {str(e)}"

def test_openai_api():
    """Test OpenAI GPT API"""
    api_key = os.getenv('OPENAI_API_KEY')

    if not api_key or api_key == 'your-api-key-here':
        return False, "API key not configured"

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)

        # Test with simple Arabic message
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "قل 'مرحبا' بالعربية"
                }
            ],
            max_tokens=100
        )

        response_text = response.choices[0].message.content
        return True, f"Success! Response: {response_text}"

    except ImportError:
        return False, "openai package not installed. Run: pip install openai"
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Test API connection"""
    print("="*60)
    print("🧪 API Connection Test")
    print("="*60)

    # Check which API key is configured
    has_claude = os.getenv('ANTHROPIC_API_KEY') and os.getenv('ANTHROPIC_API_KEY') != 'your-api-key-here'
    has_openai = os.getenv('OPENAI_API_KEY') and os.getenv('OPENAI_API_KEY') != 'your-api-key-here'

    if not has_claude and not has_openai:
        print("\n❌ No API key configured!")
        print("\nPlease edit .env file and add your API key:")
        print("  - For Claude: ANTHROPIC_API_KEY=sk-ant-...")
        print("  - For OpenAI: OPENAI_API_KEY=sk-...")
        return

    # Test Claude
    if has_claude:
        print("\n🔍 Testing Claude API...")
        success, message = test_claude_api()

        if success:
            print(f"✅ Claude API: {message}")
            print("\n🎉 API is ready to use!")
            print("\n📝 You're using: Claude 3 Haiku")
            print("💰 Estimated cost for this project: ~$0.15 (even cheaper!)")
            print("⚡ Haiku is faster and works great for Arabic extraction")
            return
        else:
            print(f"❌ Claude API: {message}")

    # Test OpenAI
    if has_openai:
        print("\n🔍 Testing OpenAI API...")
        success, message = test_openai_api()

        if success:
            print(f"✅ OpenAI API: {message}")
            print("\n🎉 API is ready to use!")
            print("\n📝 You're using: GPT-4 Turbo")
            print("💰 Estimated cost for this project: ~$0.50")
            return
        else:
            print(f"❌ OpenAI API: {message}")

    print("\n❌ API test failed. Please check:")
    print("  1. API key is correct")
    print("  2. You have credits in your account")
    print("  3. Package is installed (pip install anthropic or pip install openai)")

if __name__ == "__main__":
    main()
