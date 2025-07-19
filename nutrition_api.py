import requests
import re
from typing import Dict, List, Optional, Tuple
import config
from web_scraper import NutritionWebScraper

class NutritionAPI:
    def __init__(self):
        self.usda_api_key = config.USDA_API_KEY
        self.nutritionix_app_id = config.NUTRITIONIX_APP_ID
        self.nutritionix_app_key = config.NUTRITIONIX_APP_KEY
        self.web_scraper = NutritionWebScraper()
    
    def parse_food_message(self, message: str) -> Dict:
        """
        Parse a natural language food message to extract food items and quantities
        
        Args:
            message (str): User message like "I just ate chicken wing 6-piece"
            
        Returns:
            Dict: Parsed food information
        """
        # Remove common prefixes
        message = re.sub(r'^(i just ate|i ate|ate|just ate)\s+', '', message.lower())
        
        # Check if message contains calorie information
        calorie_pattern = r'(\d+)\s*cals?'
        calorie_matches = re.findall(calorie_pattern, message)
        
        # If calories are provided, extract them and the food names
        if calorie_matches:
            return self._parse_with_calories(message, calorie_matches)
        
        # Handle multiple items separated by "and" or "&"
        if ' and ' in message or ' & ' in message:
            return self._parse_multiple_items(message)
        
        # Extract quantities
        quantity_patterns = [
            r'(\d+)-piece',
            r'(\d+)\s+piece',
            r'(\d+)\s+cups?',
            r'(\d+)\s+servings?',
            r'(\d+)\s+grams?',
            r'(\d+)\s+oz',
            r'(\d+)\s+medium',
            r'(\d+)\s+large',
            r'(\d+)\s+small'
        ]
        
        quantity = 1
        food_name = message
        
        for pattern in quantity_patterns:
            match = re.search(pattern, message)
            if match:
                quantity = int(match.group(1))
                food_name = re.sub(pattern, '', message).strip()
                break
        
        return {
            "food_name": food_name,
            "quantity": quantity,
            "original_message": message,
            "total_calories": None
        }
    
    def _parse_with_calories(self, message: str, calorie_matches: List[str]) -> Dict:
        """
        Parse message that contains calorie information
        """
        # Extract food items and their calories
        items = []
        total_calories = 0
        
        # Split by common separators
        parts = re.split(r'\s+and\s+|\s*&\s*', message)
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
                
            # Look for calorie information in this part
            calorie_match = re.search(r'(\d+)\s*cals?', part)
            if calorie_match:
                calories = int(calorie_match.group(1))
                # Remove calorie info from food name
                food_name = re.sub(r'\(\d+\s*cals?\)', '', part).strip()
                food_name = re.sub(r'\d+\s*cals?', '', food_name).strip()
                
                items.append({
                    "food_name": food_name,
                    "calories": calories,
                    "quantity": 1
                })
                total_calories += calories
        
        return {
            "food_name": " + ".join([item["food_name"] for item in items]),
            "quantity": len(items),
            "original_message": message,
            "total_calories": total_calories,
            "items": items
        }
    
    def _parse_multiple_items(self, message: str) -> Dict:
        """
        Parse message with multiple food items
        """
        # Split by "and" or "&"
        parts = re.split(r'\s+and\s+|\s*&\s*', message)
        items = []
        
        for part in parts:
            part = part.strip()
            if not part:
                continue
            
            # Extract quantity for this item
            quantity = 1
            food_name = part
            
            quantity_patterns = [
                r'(\d+)-piece',
                r'(\d+)\s+piece',
                r'(\d+)\s+cups?',
                r'(\d+)\s+servings?',
                r'(\d+)\s+grams?',
                r'(\d+)\s+oz',
                r'(\d+)\s+medium',
                r'(\d+)\s+large',
                r'(\d+)\s+small'
            ]
            
            for pattern in quantity_patterns:
                match = re.search(pattern, part)
                if match:
                    quantity = int(match.group(1))
                    food_name = re.sub(pattern, '', part).strip()
                    break
            
            items.append({
                "food_name": food_name,
                "quantity": quantity
            })
        
        return {
            "food_name": " + ".join([item["food_name"] for item in items]),
            "quantity": len(items),
            "original_message": message,
            "total_calories": None,
            "items": items
        }
    
    def search_usda_food(self, food_name: str) -> Optional[Dict]:
        """
        Search USDA Food Database for nutritional information
        
        Args:
            food_name (str): Name of the food to search
            
        Returns:
            Dict: Nutritional information or None if not found
        """
        if not self.usda_api_key:
            return None
            
        try:
            url = "https://api.nal.usda.gov/fdc/v1/foods/search"
            params = {
                "api_key": self.usda_api_key,
                "query": food_name,
                "pageSize": 5,
                "dataType": ["Foundation", "SR Legacy"]
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("foods") and len(data["foods"]) > 0:
                food = data["foods"][0]
                
                # Extract nutrients
                nutrients = {}
                for nutrient in food.get("foodNutrients", []):
                    nutrient_id = nutrient.get("nutrientId")
                    if nutrient_id == 1008:  # Calories
                        nutrients["calories"] = nutrient.get("value", 0)
                    elif nutrient_id == 205:  # Carbohydrates
                        nutrients["carbs"] = nutrient.get("value", 0)
                    elif nutrient_id == 203:  # Protein
                        nutrients["proteins"] = nutrient.get("value", 0)
                    elif nutrient_id == 204:  # Fat
                        nutrients["fats"] = nutrient.get("value", 0)
                
                return {
                    "name": food.get("description", food_name),
                    "calories": nutrients.get("calories", 0),
                    "carbs": nutrients.get("carbs", 0),
                    "proteins": nutrients.get("proteins", 0),
                    "fats": nutrients.get("fats", 0),
                    "serving_size": food.get("servingSize", 100),
                    "source": "USDA"
                }
                
        except Exception as e:
            print(f"USDA API error: {e}")
            
        return None
    
    def search_nutritionix(self, food_name: str) -> Optional[Dict]:
        """
        Search Nutritionix API for nutritional information
        
        Args:
            food_name (str): Name of the food to search
            
        Returns:
            Dict: Nutritional information or None if not found
        """
        if not (self.nutritionix_app_id and self.nutritionix_app_key):
            return None
            
        try:
            url = "https://trackapi.nutritionix.com/v2/search/instant"
            headers = {
                "x-app-id": self.nutritionix_app_id,
                "x-app-key": self.nutritionix_app_key
            }
            params = {
                "query": food_name,
                "detailed": True
            }
            
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("common") or data.get("branded"):
                # Get the first result
                food_item = None
                if data.get("common"):
                    food_item = data["common"][0]
                elif data.get("branded"):
                    food_item = data["branded"][0]
                
                if food_item:
                    # Get detailed nutrition info
                    return self.get_nutritionix_nutrition(food_item.get("food_name", food_name))
                    
        except Exception as e:
            print(f"Nutritionix API error: {e}")
            
        return None
    
    def get_nutritionix_nutrition(self, food_name: str) -> Optional[Dict]:
        """
        Get detailed nutrition information from Nutritionix
        
        Args:
            food_name (str): Name of the food
            
        Returns:
            Dict: Nutritional information or None if not found
        """
        try:
            url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
            headers = {
                "x-app-id": self.nutritionix_app_id,
                "x-app-key": self.nutritionix_app_key,
                "Content-Type": "application/json"
            }
            data = {
                "query": food_name
            }
            
            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get("foods") and len(result["foods"]) > 0:
                food = result["foods"][0]
                
                return {
                    "name": food.get("food_name", food_name),
                    "calories": food.get("nf_calories", 0),
                    "carbs": food.get("nf_total_carbohydrate", 0),
                    "proteins": food.get("nf_protein", 0),
                    "fats": food.get("nf_total_fat", 0),
                    "serving_size": food.get("serving_qty", 1),
                    "source": "Nutritionix"
                }
                
        except Exception as e:
            print(f"Nutritionix nutrition error: {e}")
            
        return None
    
    def get_food_nutrition(self, message: str) -> Tuple[Dict, Optional[Dict]]:
        """
        Get nutritional information for a food message
        
        Args:
            message (str): User's food message
            
        Returns:
            Tuple: (parsed_food_info, nutrition_data)
        """
        # Parse the message
        parsed_food = self.parse_food_message(message)
        
        # If calories are already provided in the message, use them
        if parsed_food.get("total_calories"):
            # Create nutrition data from provided calories
            nutrition_data = {
                "name": parsed_food["food_name"],
                "calories": parsed_food["total_calories"],
                "carbs": 0,  # We don't have this info
                "proteins": 0,  # We don't have this info
                "fats": 0,  # We don't have this info
                "source": "User Provided",
                "note": "Calories provided by user"
            }
            return parsed_food, nutrition_data
        
        # Try different nutrition sources in order of preference
        nutrition_data = None
        
        # 1. Try USDA first (most reliable)
        nutrition_data = self.search_usda_food(parsed_food["food_name"])
        
        # 2. Try Nutritionix if USDA didn't work
        if not nutrition_data:
            nutrition_data = self.search_nutritionix(parsed_food["food_name"])
        
        # 3. Try web scraping as fallback
        if not nutrition_data:
            nutrition_data = self.web_scraper.search_generic_nutrition(parsed_food["food_name"])
        
        # 4. Try estimated nutrition as last resort
        if not nutrition_data:
            nutrition_data = self.web_scraper.get_estimated_nutrition(parsed_food["food_name"])
        
        # Apply quantity multiplier
        if nutrition_data:
            nutrition_data["calories"] *= parsed_food["quantity"]
            nutrition_data["carbs"] *= parsed_food["quantity"]
            nutrition_data["proteins"] *= parsed_food["quantity"]
            nutrition_data["fats"] *= parsed_food["quantity"]
        
        return parsed_food, nutrition_data 