import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, Dict
import time

class NutritionWebScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def search_fatsecret(self, food_name: str) -> Optional[Dict]:
        """
        Search FatSecret for nutritional information
        
        Args:
            food_name (str): Name of the food to search
            
        Returns:
            Dict: Nutritional information or None if not found
        """
        try:
            # Search FatSecret
            search_url = f"https://www.fatsecret.com/calories-nutrition/search?q={food_name.replace(' ', '+')}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the first search result
            result_link = soup.find('a', href=re.compile(r'/calories-nutrition/'))
            if not result_link:
                return None
            
            # Get the detailed page
            detail_url = "https://www.fatsecret.com" + result_link['href']
            detail_response = self.session.get(detail_url, timeout=10)
            detail_response.raise_for_status()
            
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
            
            # Extract nutrition information
            nutrition_data = {}
            
            # Look for nutrition facts
            nutrition_section = detail_soup.find('div', class_='nutritionFacts')
            if nutrition_section:
                # Extract calories
                calories_elem = nutrition_section.find(text=re.compile(r'Calories'))
                if calories_elem:
                    calories_text = calories_elem.find_next().get_text()
                    calories = re.search(r'(\d+)', calories_text)
                    if calories:
                        nutrition_data['calories'] = int(calories.group(1))
                
                # Extract macronutrients
                for nutrient in ['Protein', 'Carbohydrate', 'Fat']:
                    nutrient_elem = nutrition_section.find(text=re.compile(nutrient))
                    if nutrient_elem:
                        value_text = nutrient_elem.find_next().get_text()
                        value = re.search(r'(\d+\.?\d*)', value_text)
                        if value:
                            if nutrient == 'Protein':
                                nutrition_data['proteins'] = float(value.group(1))
                            elif nutrient == 'Carbohydrate':
                                nutrition_data['carbs'] = float(value.group(1))
                            elif nutrient == 'Fat':
                                nutrition_data['fats'] = float(value.group(1))
            
            if nutrition_data:
                nutrition_data['name'] = food_name
                nutrition_data['source'] = 'FatSecret'
                return nutrition_data
                
        except Exception as e:
            print(f"FatSecret scraping error: {e}")
        
        return None
    
    def search_myfitnesspal(self, food_name: str) -> Optional[Dict]:
        """
        Search MyFitnessPal for nutritional information
        
        Args:
            food_name (str): Name of the food to search
            
        Returns:
            Dict: Nutritional information or None if not found
        """
        try:
            # Search MyFitnessPal
            search_url = f"https://www.myfitnesspal.com/food/search?search={food_name.replace(' ', '+')}"
            response = self.session.get(search_url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for nutrition information in search results
            nutrition_data = {}
            
            # Try to find nutrition facts in the page
            calories_elem = soup.find(text=re.compile(r'calories', re.IGNORECASE))
            if calories_elem:
                calories_text = calories_elem.get_text()
                calories = re.search(r'(\d+)', calories_text)
                if calories:
                    nutrition_data['calories'] = int(calories.group(1))
            
            # Look for macronutrients
            for nutrient, key in [('protein', 'proteins'), ('carb', 'carbs'), ('fat', 'fats')]:
                nutrient_elem = soup.find(text=re.compile(nutrient, re.IGNORECASE))
                if nutrient_elem:
                    value_text = nutrient_elem.get_text()
                    value = re.search(r'(\d+\.?\d*)', value_text)
                    if value:
                        nutrition_data[key] = float(value.group(1))
            
            if nutrition_data:
                nutrition_data['name'] = food_name
                nutrition_data['source'] = 'MyFitnessPal'
                return nutrition_data
                
        except Exception as e:
            print(f"MyFitnessPal scraping error: {e}")
        
        return None
    
    def search_generic_nutrition(self, food_name: str) -> Optional[Dict]:
        """
        Generic nutrition search using multiple sources
        
        Args:
            food_name (str): Name of the food to search
            
        Returns:
            Dict: Nutritional information or None if not found
        """
        # Try multiple sources
        sources = [
            self.search_fatsecret,
            self.search_myfitnesspal
        ]
        
        for source_func in sources:
            try:
                result = source_func(food_name)
                if result:
                    return result
                time.sleep(1)  # Be respectful to websites
            except Exception as e:
                print(f"Error with {source_func.__name__}: {e}")
                continue
        
        return None
    
    def get_estimated_nutrition(self, food_name: str) -> Optional[Dict]:
        """
        Get estimated nutrition based on food type
        
        Args:
            food_name (str): Name of the food
            
        Returns:
            Dict: Estimated nutritional information
        """
        # Common food estimates (per 100g)
        food_estimates = {
            'rice': {'calories': 130, 'carbs': 28, 'proteins': 2.7, 'fats': 0.3},
            'chicken': {'calories': 165, 'carbs': 0, 'proteins': 31, 'fats': 3.6},
            'dal': {'calories': 116, 'carbs': 20, 'proteins': 9, 'fats': 0.4},
            'roti': {'calories': 264, 'carbs': 46, 'proteins': 8, 'fats': 4.2},
            'subzi': {'calories': 50, 'carbs': 10, 'proteins': 2, 'fats': 0.5},
            'bread': {'calories': 265, 'carbs': 49, 'proteins': 9, 'fats': 3.2},
            'milk': {'calories': 42, 'carbs': 5, 'proteins': 3.4, 'fats': 1},
            'egg': {'calories': 155, 'carbs': 1.1, 'proteins': 13, 'fats': 11},
            'banana': {'calories': 89, 'carbs': 23, 'proteins': 1.1, 'fats': 0.3},
            'apple': {'calories': 52, 'carbs': 14, 'proteins': 0.3, 'fats': 0.2},
            'potato': {'calories': 77, 'carbs': 17, 'proteins': 2, 'fats': 0.1},
            'tomato': {'calories': 18, 'carbs': 3.9, 'proteins': 0.9, 'fats': 0.2},
            'onion': {'calories': 40, 'carbs': 9.3, 'proteins': 1.1, 'fats': 0.1},
            'carrot': {'calories': 41, 'carbs': 10, 'proteins': 0.9, 'fats': 0.2},
            'spinach': {'calories': 23, 'carbs': 3.6, 'proteins': 2.9, 'fats': 0.4},
            'yogurt': {'calories': 59, 'carbs': 3.6, 'proteins': 10, 'fats': 0.4},
            'cheese': {'calories': 113, 'carbs': 0.4, 'proteins': 7, 'fats': 9},
            'fish': {'calories': 84, 'carbs': 0, 'proteins': 20, 'fats': 0.5},
            'beef': {'calories': 250, 'carbs': 0, 'proteins': 26, 'fats': 15},
            'pork': {'calories': 242, 'carbs': 0, 'proteins': 27, 'fats': 14},
        }
        
        # Try to match food name with estimates
        food_lower = food_name.lower()
        for food_key, nutrition in food_estimates.items():
            if food_key in food_lower:
                return {
                    'name': food_name,
                    'calories': nutrition['calories'],
                    'carbs': nutrition['carbs'],
                    'proteins': nutrition['proteins'],
                    'fats': nutrition['fats'],
                    'source': 'Estimated',
                    'note': 'Based on general food estimates'
                }
        
        return None 