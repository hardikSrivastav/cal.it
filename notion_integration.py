import requests
from datetime import datetime
import config

class NotionIntegration:
    def __init__(self):
        self.token = config.NOTION_TOKEN
        self.database_id = config.NOTION_DATABASE_ID
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
    
    def test_connection(self):
        """Test the connection to Notion database"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return True
        except Exception as e:
            raise Exception(f"Notion connection failed: {str(e)}")
    
    def create_food_entry(self, food_name: str, calories: float, proteins: float, carbs: float, fats: float, meal_type: str) -> bool:
        """
        Create a new food entry in Notion database
        
        Args:
            food_name (str): Name of the food
            calories (float): Calories
            proteins (float): Protein in grams
            carbs (float): Carbs in grams
            fats (float): Fats in grams
            meal_type (str): Type of meal (Breakfast, Lunch, Dinner, Snack)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            url = "https://api.notion.com/v1/pages"
            
            # Prepare the data for Notion
            data = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    config.NOTION_FIELDS["food_name"]: {
                        "title": [
                            {
                                "text": {
                                    "content": food_name
                                }
                            }
                        ]
                    },
                    config.NOTION_FIELDS["calories"]: {
                        "number": round(calories)
                    },
                    config.NOTION_FIELDS["proteins"]: {
                        "number": round(proteins, 1)
                    },
                    config.NOTION_FIELDS["carbs"]: {
                        "number": round(carbs, 1)
                    },
                    config.NOTION_FIELDS["fats"]: {
                        "number": round(fats, 1)
                    },
                    config.NOTION_FIELDS["meal_type"]: {
                        "select": {
                            "name": meal_type
                        }
                    },
                    config.NOTION_FIELDS["date"]: {
                        "date": {
                            "start": datetime.now().isoformat()
                        }
                    }
                }
            }
            
            response = requests.post(url, headers=self.headers, json=data)
            response.raise_for_status()
            
            return True
            
        except Exception as e:
            print(f"Error creating Notion entry: {e}")
            return False
    
    def get_database_info(self):
        """Get information about the Notion database"""
        try:
            url = f"https://api.notion.com/v1/databases/{self.database_id}"
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            
            db_info = response.json()
            return {
                "success": True,
                "title": db_info.get("title", [{}])[0].get("text", {}).get("content", "Unknown"),
                "url": db_info.get("url", ""),
                "properties": list(db_info.get("properties", {}).keys())
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            } 