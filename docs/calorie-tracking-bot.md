# Calorie Tracking Telegram Bot - Technical Documentation

## Overview

The Calorie Tracking Telegram Bot is an intelligent automation tool that bridges the gap between natural language food descriptions and structured nutritional data storage in Notion. It eliminates the manual effort of calorie tracking by automatically parsing food messages, retrieving nutritional information from multiple sources, and populating a Notion database.

## Architecture

### System Components

1. **Telegram Bot Interface** (`telegram_bot.py`)
   - Handles user interactions via Telegram API
   - Processes natural language food messages
   - Manages conversation flow and user states
   - Provides interactive confirmation and meal selection

2. **Nutrition Data Engine** (`nutrition_api.py`)
   - Multi-source nutrition data retrieval
   - Natural language food parsing
   - Quantity extraction and calculation
   - Fallback mechanisms for data availability

3. **Notion Integration** (`notion_client.py`)
   - Database operations and entry creation
   - Field mapping and data formatting
   - Error handling and response management

4. **Web Scraping Fallback** (`web_scraper.py`)
   - Alternative nutrition data sources
   - Estimated nutrition database
   - Graceful degradation when APIs fail

5. **Configuration Management** (`config.py`)
   - API tokens and credentials
   - Database field mappings
   - Environment-specific settings

### Data Flow

```
User Message → Telegram Bot → Food Parser → Nutrition APIs → Data Processing → Notion Database
     ↓              ↓              ↓              ↓              ↓              ↓
"I ate chicken" → Message Handler → Extract "chicken" → USDA/Nutritionix → Apply quantities → Create entry
```

## Technical Implementation

### Food Message Parsing

The bot uses regex patterns to extract food items and quantities from natural language:

```python
# Quantity patterns
quantity_patterns = [
    r'(\d+)-piece',      # "6-piece"
    r'(\d+)\s+cups?',    # "2 cups"
    r'(\d+)\s+grams?',   # "100g"
    r'(\d+)\s+medium',   # "1 medium"
]

# Food name extraction
message = re.sub(r'^(i just ate|i ate|ate|just ate)\s+', '', message.lower())
```

### Multi-Source Nutrition Data

The system implements a cascading fallback strategy:

1. **USDA Food Database** (Primary)
   - Most comprehensive and reliable
   - Requires API key (optional)
   - Covers 300,000+ foods

2. **Nutritionix API** (Secondary)
   - Restaurant and branded foods
   - Natural language processing
   - Free tier available

3. **Web Scraping** (Tertiary)
   - FatSecret and MyFitnessPal
   - Generic nutrition websites
   - Rate-limited and respectful

4. **Estimated Database** (Fallback)
   - Common foods with standard values
   - Cultural foods (dal, roti, subzi)
   - Always available

### Notion Database Integration

The bot maps nutritional data to Notion database fields:

```python
NOTION_FIELDS = {
    "food": "Food",           # Title field
    "date": "Date",           # Date field (auto-filled)
    "calories": "Calories",   # Number field
    "meal": "Meal",           # Select field
    "carbs": "Carbs",         # Number field
    "proteins": "Proteins",   # Number field
    "fats": "Fats"           # Number field
}
```

## API Integrations

### Telegram Bot API
- **Library**: python-telegram-bot v20.7
- **Features**: Webhook support, inline keyboards, message editing
- **Authentication**: Bot token-based

### Notion API
- **Library**: notion-client v2.2.1
- **Authentication**: Internal integration token
- **Permissions**: Read/write access to specific database

### Nutrition APIs

#### USDA Food Database
- **Endpoint**: https://api.nal.usda.gov/fdc/v1/foods/search
- **Rate Limit**: 3,600 requests/day (with API key)
- **Data**: Comprehensive nutritional information
- **Format**: JSON with nutrient IDs

#### Nutritionix
- **Endpoints**: 
  - Search: https://trackapi.nutritionix.com/v2/search/instant
  - Nutrition: https://trackapi.nutritionix.com/v2/natural/nutrients
- **Rate Limit**: 1,000 requests/day (free tier)
- **Data**: Restaurant and branded foods
- **Format**: Natural language processing

## Error Handling

### Graceful Degradation
The system implements multiple fallback mechanisms:

1. **API Failures**: Automatic fallback to alternative sources
2. **Data Not Found**: User clarification requests
3. **Notion Errors**: Retry mechanisms and error reporting
4. **Network Issues**: Timeout handling and retry logic

### User Experience
- Clear error messages with actionable guidance
- Processing indicators during API calls
- Confirmation before database writes
- Session management for multi-step interactions

## Security Considerations

### Token Management
- API tokens stored in configuration
- Environment variable support for sensitive data
- No hardcoded credentials in source code

### Rate Limiting
- Respectful API usage with delays
- User-agent headers for web scraping
- Timeout handling for external services

### Data Privacy
- No persistent user data storage
- Session-based conversation states
- Minimal data logging

## Performance Optimization

### Caching Strategy
- User session state management
- API response caching (future enhancement)
- Database connection pooling

### Async Operations
- Non-blocking Telegram message handling
- Concurrent API requests where possible
- Efficient database operations

## Deployment

### Requirements
- Python 3.8+
- Internet connectivity
- Telegram bot token
- Notion integration token
- Optional: Nutrition API keys

### Installation
```bash
# Clone repository
git clone <repository-url>
cd cal

# Install dependencies
pip install -r requirements.txt

# Run setup
python setup.py

# Start bot
python telegram_bot.py
```

### Environment Variables
```bash
# Optional API keys for enhanced functionality
export USDA_API_KEY="your_usda_key"
export NUTRITIONIX_APP_ID="your_app_id"
export NUTRITIONIX_APP_KEY="your_app_key"
```

## Testing

### Test Coverage
- Configuration validation
- Notion API connectivity
- Nutrition data retrieval
- Web scraping functionality
- Database entry creation

### Test Execution
```bash
# Run all tests
python test_bot.py

# Individual component tests
python -c "from notion_client import NotionCalorieTracker; print('Notion test')"
```

## Monitoring and Logging

### Log Levels
- **INFO**: Normal operations and user interactions
- **WARNING**: API failures and fallback usage
- **ERROR**: Critical failures and exceptions

### Metrics (Future Enhancement)
- API response times
- Success/failure rates
- User interaction patterns
- Database operation performance

## Future Enhancements

### Planned Features
1. **Machine Learning**: Improved food recognition
2. **Image Recognition**: Photo-based food identification
3. **Barcode Scanning**: Product barcode lookup
4. **Meal Planning**: Automated meal suggestions
5. **Analytics Dashboard**: Nutritional insights and trends

### Technical Improvements
1. **Database Caching**: Reduce API calls
2. **Batch Processing**: Multiple food items
3. **Offline Mode**: Local nutrition database
4. **Multi-language Support**: International food recognition

## Troubleshooting

### Common Issues

#### Bot Not Responding
- Verify Telegram token in config.py
- Check internet connectivity
- Ensure bot is running and accessible

#### Nutrition Data Not Found
- Try more specific food descriptions
- Add optional API keys for better coverage
- Check estimated nutrition database

#### Notion Integration Errors
- Verify database ID and permissions
- Check field names match configuration
- Ensure integration token is valid

### Debug Mode
Enable detailed logging by modifying log level in telegram_bot.py:
```python
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

### Development Setup
1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

### Code Standards
- Follow PEP 8 style guidelines
- Add type hints for all functions
- Include docstrings for classes and methods
- Write unit tests for new features

## License

MIT License - See LICENSE file for details.

---

*This documentation is maintained in the local docs/ folder and synchronized with Notion Engineering Docs as per project requirements.* 