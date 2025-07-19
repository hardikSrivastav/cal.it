import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
import config
from ai_food_parser import AIFoodParser
from notion_integration import NotionIntegration
from datetime import datetime

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class CalorieTrackingBot:
    def __init__(self):
        self.ai_parser = AIFoodParser()
        self.notion_client = NotionIntegration()
        self.user_data = {}  # Store user data temporarily
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /start is issued."""
        welcome_message = (
            "🤖 Welcome to the Calorie Tracking Bot!\n\n"
            "I can help you track your food intake and automatically log it to your Notion database.\n\n"
            "Just send me a message describing what you ate, for example:\n"
            "• 'I just ate chicken wing 6-piece'\n"
            "• 'I ate dal roti and subzi'\n"
            "• 'a double choco chip muffin (400 cals) and an iced cappuccino (173 cals)'\n\n"
            "I'll use AI to understand your food and find nutritional information!"
        )
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send a message when the command /help is issued."""
        help_message = (
            "📋 How to use this bot:\n\n"
            "1. Send me a message describing what you ate\n"
            "2. I'll use AI to parse your food and find nutrition info\n"
            "3. Review the nutritional breakdown\n"
            "4. Select the meal type and save to Notion\n\n"
            "Examples:\n"
            "• 'I just ate chicken wing 6-piece'\n"
            "• 'I ate dal roti and subzi'\n"
            "• 'a double choco chip muffin (400 cals) and an iced cappuccino (173 cals)'\n"
            "• 'pizza slice and coke'\n\n"
            "Commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n"
            "/status - Check bot status"
        )
        await update.message.reply_text(help_message)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check bot status and configuration."""
        status_message = "🤖 Bot Status:\n\n"
        
        # Check AI parser status
        if self.ai_parser.bedrock_client:
            status_message += "✅ AI Food Parser: Active (AWS Bedrock)\n"
        else:
            status_message += "⚠️ AI Food Parser: Fallback mode (no AWS credentials)\n"
        
        # Check Notion status
        try:
            self.notion_client.test_connection()
            status_message += "✅ Notion Integration: Connected\n"
        except Exception as e:
            status_message += f"❌ Notion Integration: Error - {str(e)}\n"
        
        # Check Exa web search status
        if config.EXA_API_KEY:
            status_message += "✅ Web Search: Available (Exa)\n"
        else:
            status_message += "⚠️ Web Search: Not configured (Exa API key missing)\n"
        
        await update.message.reply_text(status_message)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle incoming messages and parse food information."""
        message_text = update.message.text
        
        # Check if this looks like a food message
        food_indicators = ["ate", "eaten", "just ate", "i ate", "i just ate", "had", "consumed", "cals", "calories"]
        is_food_message = any(indicator in message_text.lower() for indicator in food_indicators)
        
        if not is_food_message:
            await update.message.reply_text(
                "🤔 That doesn't look like a food message. Try something like:\n"
                "• 'I just ate chicken wing 6-piece'\n"
                "• 'I ate dal roti and subzi'\n"
                "• 'a double choco chip muffin (400 cals) and an iced cappuccino (173 cals)'"
            )
            return
        
        # Send processing message
        processing_msg = await update.message.reply_text("🤖 Processing your food message with AI...")
        
        try:
            # Use AI to parse the food message
            parsed_data = self.ai_parser.parse_food_with_ai(message_text)
            
            if not parsed_data or not parsed_data.get("nutrition_data"):
                # Food not found - ask for clarification
                clarification_text = f"❓ I couldn't find nutritional information for '{parsed_data.get('food_name', 'your food')}'.\n\n"
                
                # Provide different suggestions based on the type of food
                food_name = parsed_data.get('food_name', '').lower()
                if 'muffin' in food_name:
                    clarification_text += "For baked goods, try:\n• 'chocolate muffin'\n• 'blueberry muffin'\n• 'muffin (300 cals)'"
                elif 'coffee' in food_name or 'cappuccino' in food_name:
                    clarification_text += "For drinks, try:\n• 'coffee with milk'\n• 'cappuccino (150 cals)'\n• 'iced coffee'"
                elif ' and ' in food_name or '&' in food_name:
                    clarification_text += "For multiple items, try:\n• 'chicken and rice'\n• 'pizza slice (300 cals) and coke (150 cals)'\n• 'salad and bread'"
                else:
                    clarification_text += "Could you please be more specific? For example:\n• 'chicken breast grilled'\n• 'white rice cooked'\n• 'dal makhani'"
                
                await processing_msg.edit_text(clarification_text)
                return
            
            # Store parsed data for later use
            user_id = update.effective_user.id
            self.user_data[user_id] = parsed_data
            
            # Show nutrition breakdown
            nutrition_data = parsed_data["nutrition_data"]
            confidence = parsed_data.get("confidence", "low")
            source = nutrition_data.get("source", "Unknown")
            
            nutrition_text = (
                f"🍽️ **Food Analysis Results**\n\n"
                f"**Food:** {parsed_data['food_name']}\n"
                f"**Quantity:** {parsed_data['quantity']} {parsed_data.get('unit', 'serving')}\n\n"
                f"📊 **Nutritional Information:**\n"
                f"• Calories: {nutrition_data['calories']:.0f} kcal\n"
                f"• Protein: {nutrition_data['proteins']:.1f}g\n"
                f"• Carbs: {nutrition_data['carbs']:.1f}g\n"
                f"• Fats: {nutrition_data['fats']:.1f}g\n\n"
                f"**Source:** {source}\n"
                f"**Confidence:** {confidence.title()}\n"
            )
            
            if nutrition_data.get("notes"):
                nutrition_text += f"**Notes:** {nutrition_data['notes']}\n\n"
            
            nutrition_text += "Select the meal type to save to Notion:"
            
            # Create meal type selection keyboard
            keyboard = []
            for meal_type in config.MEAL_TYPES:
                keyboard.append([InlineKeyboardButton(meal_type, callback_data=f"meal_{meal_type}")])
            
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await processing_msg.edit_text(nutrition_text, reply_markup=reply_markup, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await processing_msg.edit_text(
                f"❌ Sorry, I encountered an error while processing your message: {str(e)}\n\n"
                "Please try again or contact support if the problem persists."
            )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks for meal type selection."""
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        
        if user_id not in self.user_data:
            await query.edit_message_text("❌ No food data found. Please send a food message first.")
            return
        
        if query.data.startswith("meal_"):
            meal_type = query.data.replace("meal_", "")
            
            try:
                # Save to Notion
                parsed_data = self.user_data[user_id]
                nutrition_data = parsed_data["nutrition_data"]
                
                success = self.notion_client.create_food_entry(
                    food_name=parsed_data["food_name"],
                    calories=nutrition_data["calories"],
                    proteins=nutrition_data["proteins"],
                    carbs=nutrition_data["carbs"],
                    fats=nutrition_data["fats"],
                    meal_type=meal_type
                )
                
                if success:
                    success_message = (
                        f"✅ **Successfully saved to Notion!**\n\n"
                        f"**Food:** {parsed_data['food_name']}\n"
                        f"**Meal Type:** {meal_type}\n"
                        f"**Calories:** {nutrition_data['calories']:.0f} kcal\n\n"
                        f"Your food has been logged to your Notion database. Keep tracking! 🎯"
                    )
                    await query.edit_message_text(success_message, parse_mode='Markdown')
                else:
                    await query.edit_message_text("❌ Failed to save to Notion. Please try again.")
                
                # Clean up user data
                del self.user_data[user_id]
                
            except Exception as e:
                logger.error(f"Error saving to Notion: {e}")
                await query.edit_message_text(
                    f"❌ Error saving to Notion: {str(e)}\n\n"
                    "Please try again or check your Notion configuration."
                )

def main():
    """Start the bot."""
    print("🤖 Starting Calorie Tracking Bot...")
    
    # Create bot instance
    bot = CalorieTrackingBot()
    
    # Create application
    application = Application.builder().token(config.TELEGRAM_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", bot.start))
    application.add_handler(CommandHandler("help", bot.help_command))
    application.add_handler(CommandHandler("status", bot.status_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_message))
    application.add_handler(CallbackQueryHandler(bot.handle_callback))
    
    # Start the bot
    print("✅ Bot is running. Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 