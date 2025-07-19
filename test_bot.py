#!/usr/bin/env python3
"""
Test script for Calorie Tracking Bot
Run this to verify all components work correctly
"""

import sys
import traceback
from notion_integration import NotionCalorieTracker
from nutrition_api import NutritionAPI
from web_scraper import NutritionWebScraper
import config

def test_config():
    """Test configuration loading"""
    print("🔧 Testing Configuration...")
    try:
        assert config.TELEGRAM_TOKEN, "Telegram token not found"
        assert config.NOTION_TOKEN, "Notion token not found"
        assert config.NOTION_DATABASE_ID, "Notion database ID not found"
        print("✅ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_notion_connection():
    """Test Notion API connection"""
    print("\n📊 Testing Notion Connection...")
    try:
        notion = NotionCalorieTracker()
        db_info = notion.get_database_info()
        
        if db_info["success"]:
            print("✅ Notion connection successful")
            print(f"   Database: {db_info['database'].get('title', [{}])[0].get('text', {}).get('content', 'Unknown')}")
            return True
        else:
            print(f"❌ Notion connection failed: {db_info['error']}")
            return False
    except Exception as e:
        print(f"❌ Notion connection error: {e}")
        return False

def test_nutrition_api():
    """Test nutrition API functionality"""
    print("\n🍎 Testing Nutrition API...")
    try:
        nutrition_api = NutritionAPI()
        
        # Test food parsing
        test_messages = [
            "I just ate chicken wing 6-piece",
            "I ate dal roti and subzi",
            "Just ate 2 cups of rice"
        ]
        
        for message in test_messages:
            print(f"\n   Testing: '{message}'")
            parsed_food, nutrition_data = nutrition_api.get_food_nutrition(message)
            
            print(f"   Parsed: {parsed_food['food_name']} (qty: {parsed_food['quantity']})")
            
            if nutrition_data:
                print(f"   Found nutrition data from: {nutrition_data['source']}")
                print(f"   Calories: {nutrition_data['calories']:.0f}")
                print(f"   Protein: {nutrition_data['proteins']:.1f}g")
                print(f"   Carbs: {nutrition_data['carbs']:.1f}g")
                print(f"   Fats: {nutrition_data['fats']:.1f}g")
            else:
                print("   ❌ No nutrition data found")
        
        print("✅ Nutrition API test completed")
        return True
    except Exception as e:
        print(f"❌ Nutrition API error: {e}")
        traceback.print_exc()
        return False

def test_web_scraper():
    """Test web scraper functionality"""
    print("\n🌐 Testing Web Scraper...")
    try:
        scraper = NutritionWebScraper()
        
        # Test estimated nutrition
        test_foods = ["rice", "chicken", "dal", "apple"]
        
        for food in test_foods:
            print(f"\n   Testing estimated nutrition for: {food}")
            nutrition = scraper.get_estimated_nutrition(food)
            
            if nutrition:
                print(f"   ✅ Found: {nutrition['calories']} calories")
            else:
                print(f"   ❌ Not found in estimates")
        
        print("✅ Web scraper test completed")
        return True
    except Exception as e:
        print(f"❌ Web scraper error: {e}")
        traceback.print_exc()
        return False

def test_notion_entry():
    """Test creating a Notion entry"""
    print("\n💾 Testing Notion Entry Creation...")
    try:
        notion = NotionCalorieTracker()
        
        # Test data
        test_food_data = {
            "food": "Test Food Entry",
            "calories": 100,
            "carbs": 20.0,
            "proteins": 5.0,
            "fats": 2.0,
            "meal": "Snack"
        }
        
        result = notion.create_food_entry(test_food_data)
        
        if result["success"]:
            print("✅ Test entry created successfully")
            print(f"   Entry URL: {result['url']}")
            return True
        else:
            print(f"❌ Failed to create test entry: {result['error']}")
            return False
    except Exception as e:
        print(f"❌ Notion entry creation error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🧪 Starting Calorie Tracking Bot Tests...\n")
    
    tests = [
        ("Configuration", test_config),
        ("Notion Connection", test_notion_connection),
        ("Nutrition API", test_nutrition_api),
        ("Web Scraper", test_web_scraper),
        ("Notion Entry Creation", test_notion_entry)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running: {test_name}")
        print('='*50)
        
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            traceback.print_exc()
    
    print(f"\n{'='*50}")
    print(f"Test Results: {passed}/{total} tests passed")
    print('='*50)
    
    if passed == total:
        print("🎉 All tests passed! Your bot is ready to run.")
        print("\nTo start the bot, run:")
        print("python telegram_bot.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nCommon issues:")
        print("- Check your API tokens in config.py")
        print("- Ensure Notion database exists and is accessible")
        print("- Verify internet connection")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 