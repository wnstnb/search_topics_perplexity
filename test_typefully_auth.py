#!/usr/bin/env python3
"""
Test script for Typefully Authentication System

This script demonstrates and tests the authentication functionality.
Run this after setting up your TYPEFULLY_API_KEY in a .env file.
"""

import os
import sys
from pathlib import Path

# Add the agents directory to the Python path
sys.path.append(str(Path(__file__).parent / "agents"))

from agents.typefully_auth import TypefullyAuth, TypefullyAuthError
from config import TYPEFULLY_CONFIG

def test_authentication():
    """Test the Typefully authentication system"""
    
    print("🔐 Testing Typefully Authentication System")
    print("=" * 50)
    
    try:
        # Initialize authentication
        print("1. Initializing authentication system...")
        auth = TypefullyAuth()
        print(f"   ✅ Authentication system initialized")
        
        # Check if we have any accounts
        accounts = auth.list_accounts()
        print(f"   📊 Found {len(accounts)} account(s)")
        
        if not accounts:
            print("   ⚠️  No accounts configured. Please add TYPEFULLY_API_KEY to your .env file")
            return False
        
        # Display account information
        print("\n2. Account Information:")
        for account in accounts:
            status = "🟢 Current" if account["is_current"] else "⚪ Available"
            print(f"   {status} Account: {account['account_id']}")
            print(f"     Active: {'Yes' if account['is_active'] else 'No'}")
            print(f"     Twitter: {account.get('twitter_username', 'Not set')}")
            print(f"     Last validated: {account.get('last_validated', 'Never')}")
        
        # Test getting authentication headers
        print("\n3. Testing authentication headers...")
        try:
            headers = auth.get_auth_headers()
            print("   ✅ Authentication headers generated successfully")
            print(f"   🔑 X-API-KEY: Bearer {headers['X-API-KEY'][-12:]}...")  # Show last 12 chars only
        except TypefullyAuthError as e:
            print(f"   ❌ Failed to get auth headers: {e}")
            return False
        
        # Test credential validation (this makes a real API call)
        print("\n4. Testing credential validation...")
        print("   🔄 Making test API call to Typefully...")
        
        is_valid = auth.validate_credentials()
        if is_valid:
            print("   ✅ Credentials are valid! API connection successful")
        else:
            print("   ❌ Credentials validation failed")
            print("   💡 Please check:")
            print("      - Your TYPEFULLY_API_KEY is correct")
            print("      - Your API key is active in Typefully settings")
            print("      - You have internet connectivity")
            return False
        
        # Test health check
        print("\n5. Performing health check...")
        health = auth.health_check()
        print(f"   Overall status: {health['overall_status'].upper()}")
        print(f"   Active accounts: {health['active_accounts']}/{health['total_accounts']}")
        
        # Display current account info
        print("\n6. Current Account Details:")
        current_account = auth.get_current_account_info()
        if current_account:
            print(f"   Account ID: {current_account['account_id']}")
            print(f"   Twitter Username: {current_account.get('twitter_username', 'Not set')}")
            print(f"   Created: {current_account.get('created_at', 'Unknown')}")
            print(f"   Last Validated: {current_account.get('last_validated', 'Never')}")
        
        print("\n🎉 All tests passed! Typefully authentication is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return False

def test_configuration():
    """Test the configuration system"""
    
    print("\n🔧 Testing Configuration System")
    print("=" * 50)
    
    try:
        # Test config validation
        status = TYPEFULLY_CONFIG.validate_config()
        
        print("Configuration Status:")
        print(f"  Valid: {'✅ Yes' if status['valid'] else '❌ No'}")
        
        if status['errors']:
            print("  Errors:")
            for error in status['errors']:
                print(f"    ❌ {error}")
        
        if status['warnings']:
            print("  Warnings:")
            for warning in status['warnings']:
                print(f"    ⚠️  {warning}")
        
        print("\nConfiguration Summary:")
        config = status['config_summary']
        print(f"  API Key Present: {'✅' if config['api_key_present'] else '❌'}")
        print(f"  Base URL: {config['base_url']}")
        print(f"  Timeout: {config['timeout']}s")
        print(f"  Max Retries: {config['max_retries']}")
        print(f"  Auto Retweet: {'✅' if config['auto_retweet'] else '❌'}")
        print(f"  Auto Plug: {'✅' if config['auto_plug'] else '❌'}")
        print(f"  Default Threadify: {'✅' if config['default_threadify'] else '❌'}")
        print(f"  Rate Limit: {config['rate_limit_per_minute']}/min")
        
        return status['valid']
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Typefully Authentication System Tests")
    print("=" * 60)
    
    # Test configuration first
    config_ok = test_configuration()
    
    if not config_ok:
        print("\n⚠️  Configuration issues detected. Some tests may fail.")
        print("💡 Make sure you have TYPEFULLY_API_KEY in your .env file")
    
    # Test authentication
    auth_ok = test_authentication()
    
    print("\n" + "=" * 60)
    if auth_ok:
        print("🎉 ALL TESTS PASSED! Typefully integration is ready to use.")
        print("\n🔗 Next steps:")
        print("   1. Start implementing the Typefully API client")
        print("   2. Test draft creation functionality")
        print("   3. Add scheduling and monitoring features")
    else:
        print("❌ SOME TESTS FAILED. Please fix the issues above.")
        print("\n💡 Common solutions:")
        print("   1. Add TYPEFULLY_API_KEY to your .env file")
        print("   2. Get your API key from: https://typefully.com/settings/integrations")
        print("   3. Check your internet connection")
        print("   4. Verify your API key is active in Typefully")

if __name__ == "__main__":
    main() 