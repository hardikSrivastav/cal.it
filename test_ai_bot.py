#!/usr/bin/env python3
"""
Test suite for AI-powered Calorie Tracking Bot
Tests AWS Bedrock integration, web search, and Notion integration
"""

import os
import sys
import json
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_config():
    """Test configuration loading"""
    print("🔧 Testing configuration...")
    
    try:
        import config
        
        # Check required configs
        required_configs = [
            "TELEGRAM_TOKEN",
            "NOTION_TOKEN", 
            "NOTION_DATABASE_ID"
        ]
        
        for config_name in required_configs:
            if not getattr(config, config_name, None):
                print(f"❌ Missing required config: {config_name}")
                return False
        
        print("✅ Configuration loaded successfully")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_ai_parser():
    """Test AI food parser"""
    print("\n🤖 Testing AI Food Parser...")
    
    try:
        from ai_food_parser import AIFoodParser
        
        parser = AIFoodParser()
        
        # Test with various food messages
        test_messages = [
            "a double choco chip muffin (400 cals) and an iced cappuccino (173 cals)",
            "I just ate chicken wing 6-piece",
            "I ate dal roti and subzi",
            "pizza slice and coke"
        ]
        
        for message in test_messages:
            print(f"  Testing: '{message}'")
            result = parser.parse_food_with_ai(message)
            
            if result and result.get("food_name"):
                print(f"    ✅ Parsed: {result['food_name']}")
                if result.get("nutrition_data"):
                    nutrition = result["nutrition_data"]
                    print(f"    📊 Calories: {nutrition.get('calories', 0)}")
                    print(f"    🏷️ Source: {nutrition.get('source', 'Unknown')}")
                else:
                    print(f"    ⚠️ No nutrition data found")
            else:
                print(f"    ❌ Failed to parse")
        
        print("✅ AI Food Parser tests completed")
        return True
        
    except Exception as e:
        print(f"❌ AI Parser error: {e}")
        return False

def test_web_search():
    """Test web search functionality"""
    print("\n�� Testing Web Search (Exa)...")
    
    try:
        from ai_food_parser import WebSearchAPI
        
        search_api = WebSearchAPI()
        
        # Test search functionality
        test_query = "chocolate chip muffin nutrition facts calories"
        results = search_api.search(test_query)
        
        if results:
            print(f"✅ Exa web search returned {len(results)} results")
            for i, result in enumerate(results[:3]):
                print(f"  {i+1}. {result.get('title', 'No title')}")
                print(f"     URL: {result.get('url', 'No URL')}")
        else:
            print("⚠️ No web search results (Exa API key may not be configured)")
        
        return True
        
    except Exception as e:
        print(f"❌ Web search error: {e}")
        return False

def test_notion_integration():
    """Test Notion integration"""
    print("\n📝 Testing Notion Integration...")
    
    try:
        from notion_integration import NotionIntegration
        
        notion = NotionIntegration()
        
        # Test connection
        try:
            notion.test_connection()
            print("✅ Notion connection successful")
        except Exception as e:
            print(f"❌ Notion connection failed: {e}")
            return False
        
        # Test database info
        db_info = notion.get_database_info()
        if db_info["success"]:
            print(f"✅ Database: {db_info['title']}")
            print(f"✅ Properties: {', '.join(db_info['properties'])}")
        else:
            print(f"❌ Database info failed: {db_info['error']}")
            return False
        
        # Test creating an entry (optional - can be commented out to avoid test data)
        print("  Testing entry creation...")
        success = notion.create_food_entry(
            food_name="Test Food - AI Bot",
            calories=250,
            proteins=10.5,
            carbs=30.2,
            fats=8.1,
            meal_type="Snack"
        )
        
        if success:
            print("✅ Test entry created successfully")
        else:
            print("❌ Failed to create test entry")
        
        return True
        
    except Exception as e:
        print(f"❌ Notion integration error: {e}")
        return False

def test_telegram_bot():
    """Test Telegram bot components"""
    print("\n🤖 Testing Telegram Bot Components...")
    
    try:
        from telegram_bot import CalorieTrackingBot
        
        # Test bot initialization
        bot = CalorieTrackingBot()
        print("✅ Bot initialized successfully")
        
        # Test AI parser integration
        if bot.ai_parser:
            print("✅ AI parser integrated")
        else:
            print("❌ AI parser not available")
        
        # Test Notion integration
        if bot.notion_client:
            print("✅ Notion client integrated")
        else:
            print("❌ Notion client not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Telegram bot error: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting AI Calorie Tracking Bot Tests...\n")
    
    tests = [
        ("Configuration", test_config),
        ("AI Food Parser", test_ai_parser),
        ("Web Search", test_web_search),
        ("Notion Integration", test_notion_integration),
        ("Telegram Bot", test_telegram_bot)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name} Test")
        print(f"{'='*50}")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 All tests passed! Your AI Calorie Tracking Bot is ready to use.")
        print("\nNext steps:")
        print("1. Set up your AWS Bedrock credentials in .env file")
        print("2. Optionally add web search API keys for enhanced nutrition lookup")
        print("3. Run: python telegram_bot.py")
    else:
        print("⚠️ Some tests failed. Please check the configuration and try again.")
        print("\nRequired setup:")
        print("1. AWS Bedrock credentials (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)")
        print("2. Notion integration token and database ID")
        print("3. Telegram bot token")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 