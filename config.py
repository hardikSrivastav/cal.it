import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_TOKEN = "8196941788:AAFvmvxxgXoFunshnuNmu0r1gUu_OyMI2WE"

# Notion Configuration
NOTION_TOKEN = "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"
NOTION_DATABASE_ID = "23472f8c63128063af54eba9b26ecc1f"

# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-sonnet-20240229-v1:0")

# Exa Web Search Configuration
EXA_API_KEY = os.getenv("EXA_API_KEY")

# Nutrition API Keys (Optional - for fallback nutrition data)
USDA_API_KEY = os.getenv("USDA_API_KEY")
NUTRITIONIX_APP_ID = os.getenv("NUTRITIONIX_APP_ID")
NUTRITIONIX_APP_KEY = os.getenv("NUTRITIONIX_APP_KEY")

# OpenAI Configuration (for better food parsing)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Notion Database Field Mappings (updated to match actual database)
NOTION_FIELDS = {
    "calories": "Calories",
    "proteins": "Proteins",
    "carbs": "Carbs", 
    "fats": "Fats",
    "meal_type": "Meal",
    "date": "Date",
    "food_name": "Food"
}

# Meal Types
MEAL_TYPES = ["Breakfast", "Lunch", "Dinner", "Snack"] 