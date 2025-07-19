# 🤖 AI-Powered Calorie Tracking Bot

An intelligent Telegram bot that uses **AWS Bedrock** and **Exa web search** to automatically parse food messages, extract nutritional information, and log calories to your Notion database.

## ✨ Features

- **🤖 AI-Powered Food Parsing**: Uses AWS Bedrock (Claude) to intelligently understand natural language food descriptions
- **🌐 Smart Web Search**: Leverages Exa API for AI-optimized web search to find accurate nutrition data
- **📝 Notion Integration**: Automatically logs food entries to your Notion database
- **🎯 Multi-Item Support**: Handles complex food descriptions with multiple items and quantities
- **📊 Nutritional Breakdown**: Shows calories, protein, carbs, and fats before saving
- **🔄 Fallback Systems**: Multiple nutrition data sources for maximum accuracy

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd cal

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file based on `env_example.txt`:

```bash
# Required
TELEGRAM_TOKEN=your_telegram_bot_token
NOTION_TOKEN=your_notion_integration_token
NOTION_DATABASE_ID=your_notion_database_id

# Required for AI features
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1

# Recommended for enhanced nutrition lookup
EXA_API_KEY=your_exa_api_key

# Optional fallback APIs
USDA_API_KEY=your_usda_api_key
NUTRITIONIX_APP_ID=your_nutritionix_app_id
NUTRITIONIX_APP_KEY=your_nutritionix_app_key
```

### 3. Run Tests

```bash
python test_ai_bot.py
```

### 4. Start the Bot

```bash
python telegram_bot.py
```

## 🛠️ Setup Instructions

### Telegram Bot Setup

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the API token to your `.env` file

### Notion Database Setup

1. Create a Notion database with these fields:
   - **Food Name** (Title)
   - **Calories** (Number)
   - **Protein** (Number)
   - **Carbs** (Number)
   - **Fats** (Number)
   - **Meal Type** (Select: Breakfast, Lunch, Dinner, Snack)
   - **Date** (Date)

2. Create an internal integration:
   - Go to [Notion Integrations](https://www.notion.so/my-integrations)
   - Create new integration
   - Copy the token to your `.env` file
   - Share your database with the integration

### AWS Bedrock Setup

1. Create an AWS account
2. Enable Bedrock service in your region
3. Create IAM user with Bedrock permissions
4. Add credentials to your `.env` file

### Exa API Setup (Recommended)

1. Sign up at [Exa](https://exa.ai)
2. Get your API key
3. Add to your `.env` file

## 📱 Usage Examples

Send these messages to your bot:

```
I just ate chicken wing 6-piece
```
```
I ate dal roti and subzi
```
```
a double choco chip muffin (400 cals) and an iced cappuccino (173 cals)
```
```
pizza slice and coke
```

The bot will:
1. 🤖 Use AI to parse your food description
2. 🌐 Search the web for nutrition data if needed
3. 📊 Show you the nutritional breakdown
4. 📝 Save to your Notion database

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Telegram Bot  │───▶│  AI Food Parser │───▶│  AWS Bedrock    │
│                 │    │                 │    │   (Claude)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         │              │   Exa Web Search│              │
         │              │                 │              │
         │              └─────────────────┘              │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Notion API    │    │  Nutrition Data │    │  Fallback APIs  │
│                 │    │                 │    │  (USDA, etc.)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_TOKEN` | ✅ | Your Telegram bot token |
| `NOTION_TOKEN` | ✅ | Notion integration token |
| `NOTION_DATABASE_ID` | ✅ | Your Notion database ID |
| `AWS_ACCESS_KEY_ID` | ✅ | AWS access key for Bedrock |
| `AWS_SECRET_ACCESS_KEY` | ✅ | AWS secret key for Bedrock |
| `AWS_REGION` | ✅ | AWS region (default: us-east-1) |
| `EXA_API_KEY` | 🔶 | Exa API key for web search |
| `USDA_API_KEY` | 🔶 | USDA API key (fallback) |
| `NUTRITIONIX_APP_ID` | 🔶 | Nutritionix app ID (fallback) |
| `NUTRITIONIX_APP_KEY` | 🔶 | Nutritionix app key (fallback) |

### Notion Database Fields

The bot expects these field names in your Notion database:

```python
NOTION_FIELDS = {
    "calories": "Calories",
    "proteins": "Protein", 
    "carbs": "Carbs",
    "fats": "Fats",
    "meal_type": "Meal Type",
    "date": "Date",
    "food_name": "Food Name"
}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_ai_bot.py
```

This tests:
- ✅ Configuration loading
- ✅ AI food parser
- ✅ Exa web search
- ✅ Notion integration
- ✅ Telegram bot components

## 🚀 Deployment

### Local Development

```bash
# Start the bot
python telegram_bot.py
```

### Production Deployment

1. **Heroku**:
   ```bash
   heroku create your-bot-name
   heroku config:set TELEGRAM_TOKEN=your_token
   # ... set other environment variables
   git push heroku main
   ```

2. **AWS EC2**:
   ```bash
   # Install dependencies
   sudo apt update
   sudo apt install python3-pip
   pip3 install -r requirements.txt
   
   # Run with systemd
   sudo systemctl enable calorie-bot
   sudo systemctl start calorie-bot
   ```

3. **Docker**:
   ```bash
   docker build -t calorie-bot .
   docker run -d --env-file .env calorie-bot
   ```

## 🔍 Troubleshooting

### Common Issues

1. **"AWS credentials not found"**
   - Check your AWS credentials in `.env`
   - Ensure Bedrock is enabled in your region

2. **"Notion connection failed"**
   - Verify your Notion token
   - Check database permissions
   - Ensure field names match

3. **"No nutrition data found"**
   - Add Exa API key for better search results
   - Check if food description is clear enough

4. **"Telegram bot not responding"**
   - Verify bot token
   - Check if bot is running
   - Look for error logs

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- [AWS Bedrock](https://aws.amazon.com/bedrock/) for AI capabilities
- [Exa](https://exa.ai) for intelligent web search
- [Notion API](https://developers.notion.com/) for database integration
- [python-telegram-bot](https://python-telegram-bot.org/) for Telegram integration

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section
2. Run the test suite: `python test_ai_bot.py`
3. Check the logs for error messages
4. Open an issue with detailed information

---

**Happy calorie tracking! 🎯** 