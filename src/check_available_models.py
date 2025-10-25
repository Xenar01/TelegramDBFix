#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check which Claude models are available to your API key
"""

import os
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic

client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

# List of all possible Claude models
all_models = [
    "claude-3-5-sonnet-latest",
    "claude-3-5-sonnet-20241022",
    "claude-3-5-sonnet-20240620",
    "claude-3-opus-latest",
    "claude-3-opus-20240229",
    "claude-3-sonnet-latest",
    "claude-3-sonnet-20240229",
    "claude-3-haiku-latest",
    "claude-3-haiku-20240307",
    "claude-2.1",
    "claude-2.0",
]

print("Testing which models work with your API key...\n")
print("="*60)

working_models = []

for model in all_models:
    try:
        message = client.messages.create(
            model=model,
            max_tokens=10,
            messages=[{"role": "user", "content": "Hi"}]
        )
        print(f"✅ {model} - WORKS")
        working_models.append(model)
    except Exception as e:
        error_msg = str(e)
        if "404" in error_msg or "not_found" in error_msg:
            print(f"❌ {model} - Not available")
        elif "permission" in error_msg.lower():
            print(f"🔒 {model} - No permission")
        else:
            print(f"⚠️  {model} - Error: {error_msg[:50]}")

print("\n" + "="*60)
print(f"\n✅ Working models: {len(working_models)}")
if working_models:
    print("\nYou can use these models:")
    for model in working_models:
        print(f"  • {model}")
else:
    print("\n❌ No models available!")
    print("\nPossible issues:")
    print("  1. API key is for Anthropic Console (web) not API")
    print("  2. No credits in API account")
    print("  3. Account not activated for API access")
    print("\nCheck: https://console.anthropic.com/settings/billing")
