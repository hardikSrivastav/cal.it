import boto3
import json
import requests
from typing import Dict, List, Optional, Tuple
import config
from bs4 import BeautifulSoup
import re

class AIFoodParser:
    def __init__(self):
        self.bedrock_client = None
        self.setup_bedrock()
        self.web_search_api = WebSearchAPI()
    
    def setup_bedrock(self):
        """Initialize AWS Bedrock client"""
        try:
            if config.AWS_ACCESS_KEY_ID and config.AWS_SECRET_ACCESS_KEY:
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY,
                    region_name=config.AWS_REGION
                )
                print("✅ AWS Bedrock client initialized successfully")
            else:
                print("⚠️ AWS credentials not found. Using fallback parsing.")
        except Exception as e:
            print(f"❌ Failed to initialize Bedrock: {e}")
    
    def parse_food_with_ai(self, message: str) -> Dict:
        """
        Use AI to intelligently parse food messages and extract nutritional information
        
        Args:
            message (str): User's food message
            
        Returns:
            Dict: Parsed food information with nutrition data
        """
        if not self.bedrock_client:
            return self._fallback_parse(message)
        
        try:
            # Create AI prompt for food parsing
            prompt = self._create_food_parsing_prompt(message)
            
            # Get AI response
            ai_response = self._get_bedrock_response(prompt)
            
            # Parse AI response
            parsed_data = self._parse_ai_response(ai_response, message)
            
            # If AI couldn't find nutrition data, search the web
            if not parsed_data.get("nutrition_data"):
                web_nutrition = self._search_web_for_nutrition(parsed_data["food_name"])
                if web_nutrition:
                    parsed_data["nutrition_data"] = web_nutrition
                    parsed_data["source"] = "Web Search"
            
            return parsed_data
            
        except Exception as e:
            print(f"AI parsing failed: {e}")
            return self._fallback_parse(message)
    
    def _create_food_parsing_prompt(self, message: str) -> str:
        """Create a comprehensive prompt for AI food parsing"""
        return f"""You are an expert nutritionist and food analyst. Your task is to parse the following food message and extract detailed nutritional information.

User message: "{message}"

Please analyze this message and provide a JSON response with the following structure:
{{
    "food_name": "Standardized food name",
    "quantity": number,
    "unit": "serving unit (piece, cup, gram, etc.)",
    "calories": number,
    "proteins": number (in grams),
    "carbs": number (in grams), 
    "fats": number (in grams),
    "confidence": "high/medium/low",
    "notes": "Any relevant notes about the food or estimation",
    "search_terms": ["list", "of", "search", "terms", "for", "web", "lookup"]
}}

Guidelines:
1. If the message contains calorie information (e.g., "400 cals"), use those exact calories
2. For multiple items, combine them into a single entry with total nutrition
3. If you're not confident about nutrition values, set confidence to "low" and provide search_terms
4. Standardize food names (e.g., "double choco chip muffin" → "chocolate chip muffin")
5. Estimate reasonable portion sizes if not specified
6. For drinks, include caffeine content if mentioned

Examples:
- "a double choco chip muffin (400 cals) and an iced cappuccino (173 cals)" should return combined nutrition
- "chicken wing 6-piece" should estimate nutrition for 6 chicken wings
- "dal roti and subzi" should provide typical Indian meal nutrition

Respond only with valid JSON:"""

    def _get_bedrock_response(self, prompt: str) -> str:
        """Get response from AWS Bedrock"""
        try:
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_client.invoke_model(
                modelId=config.BEDROCK_MODEL_ID,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response.get('body').read())
            return response_body['content'][0]['text']
            
        except Exception as e:
            print(f"Bedrock API error: {e}")
            raise
    
    def _parse_ai_response(self, ai_response: str, original_message: str) -> Dict:
        """Parse the AI response and extract structured data"""
        try:
            # Extract JSON from AI response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if not json_match:
                raise ValueError("No JSON found in AI response")
            
            ai_data = json.loads(json_match.group())
            
            # Create nutrition data structure
            nutrition_data = {
                "name": ai_data.get("food_name", "Unknown Food"),
                "calories": ai_data.get("calories", 0),
                "carbs": ai_data.get("carbs", 0),
                "proteins": ai_data.get("proteins", 0),
                "fats": ai_data.get("fats", 0),
                "source": "AI Analysis",
                "confidence": ai_data.get("confidence", "low"),
                "notes": ai_data.get("notes", "")
            }
            
            return {
                "food_name": ai_data.get("food_name", "Unknown Food"),
                "quantity": ai_data.get("quantity", 1),
                "unit": ai_data.get("unit", "serving"),
                "original_message": original_message,
                "nutrition_data": nutrition_data,
                "search_terms": ai_data.get("search_terms", []),
                "confidence": ai_data.get("confidence", "low")
            }
            
        except Exception as e:
            print(f"Failed to parse AI response: {e}")
            return self._fallback_parse(original_message)
    
    def _search_web_for_nutrition(self, food_name: str, search_terms: List[str] = None) -> Optional[Dict]:
        """Search the web for nutritional information"""
        try:
            # Use search terms if provided, otherwise use food name
            search_query = " ".join(search_terms) if search_terms else food_name
            search_query += " nutrition facts calories protein carbs fat"
            
            # Search the web using Exa
            search_results = self.web_search_api.search(search_query)
            
            if not search_results:
                return None
            
            # Extract nutrition data from search results
            nutrition_data = self._extract_nutrition_from_web(search_results, food_name)
            
            return nutrition_data
            
        except Exception as e:
            print(f"Web search failed: {e}")
            return None
    
    def _extract_nutrition_from_web(self, search_results: List[Dict], food_name: str) -> Optional[Dict]:
        """Extract nutrition data from web search results using AI"""
        if not self.bedrock_client:
            return None
        
        try:
            # Create a summary of search results
            results_summary = "\n".join([
                f"Title: {result.get('title', '')}\nContent: {result.get('text', '')}\n"
                for result in search_results[:5]
            ])
            
            prompt = f"""Based on the following web search results, extract nutritional information for "{food_name}".

Search Results:
{results_summary}

Please provide a JSON response with:
{{
    "calories": number,
    "proteins": number (grams),
    "carbs": number (grams),
    "fats": number (grams),
    "serving_size": "description",
    "confidence": "high/medium/low"
}}

If you can't find reliable information, respond with null. Only respond with valid JSON:"""

            ai_response = self._get_bedrock_response(prompt)
            
            # Parse the response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                nutrition = json.loads(json_match.group())
                if nutrition.get("calories"):
                    return {
                        "name": food_name,
                        "calories": nutrition.get("calories", 0),
                        "carbs": nutrition.get("carbs", 0),
                        "proteins": nutrition.get("proteins", 0),
                        "fats": nutrition.get("fats", 0),
                        "source": "Web Search (Exa)",
                        "serving_size": nutrition.get("serving_size", "1 serving"),
                        "confidence": nutrition.get("confidence", "medium")
                    }
            
            return None
            
        except Exception as e:
            print(f"Failed to extract nutrition from web: {e}")
            return None
    
    def _fallback_parse(self, message: str) -> Dict:
        """Fallback parsing when AI is not available"""
        # Basic parsing logic
        message = message.lower()
        
        # Extract calories if provided
        calorie_match = re.search(r'(\d+)\s*cals?', message)
        calories = int(calorie_match.group(1)) if calorie_match else 0
        
        # Extract quantity
        quantity_match = re.search(r'(\d+)-piece|(\d+)\s+piece', message)
        quantity = int(quantity_match.group(1) or quantity_match.group(2)) if quantity_match else 1
        
        # Clean food name
        food_name = re.sub(r'(\d+)\s*cals?|(\d+)-piece|(\d+)\s+piece', '', message).strip()
        food_name = re.sub(r'^(i just ate|i ate|ate|just ate)\s+', '', food_name)
        
        return {
            "food_name": food_name,
            "quantity": quantity,
            "original_message": message,
            "nutrition_data": {
                "name": food_name,
                "calories": calories,
                "carbs": 0,
                "proteins": 0,
                "fats": 0,
                "source": "Fallback",
                "confidence": "low"
            },
            "confidence": "low"
        }


class WebSearchAPI:
    def __init__(self):
        self.exa_api_key = config.EXA_API_KEY
    
    def search(self, query: str) -> List[Dict]:
        """Search the web for nutrition information using Exa"""
        try:
            if not self.exa_api_key:
                print("⚠️ Exa API key not configured")
                return []
            
            return self._search_exa(query)
            
        except Exception as e:
            print(f"Web search failed: {e}")
            return []
    
    def _search_exa(self, query: str) -> List[Dict]:
        """Search using Exa API - optimized for AI applications"""
        try:
            url = "https://api.exa.ai/search"
            headers = {
                "x-api-key": self.exa_api_key,
                "Content-Type": "application/json"
            }
            
            # Exa search parameters optimized for nutrition data
            payload = {
                "query": query,
                "numResults": 10,
                "includeDomains": [
                    "nutrition.gov",
                    "fdc.nal.usda.gov", 
                    "fatsecret.com",
                    "myfitnesspal.com",
                    "calorieking.com",
                    "nutritionix.com",
                    "webmd.com",
                    "healthline.com"
                ],
                "useAutoprompt": True,
                "type": "keyword"
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            # Format results for consistency
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "title": result.get("title", ""),
                    "text": result.get("text", ""),
                    "url": result.get("url", ""),
                    "publishedDate": result.get("publishedDate", ""),
                    "author": result.get("author", "")
                })
            
            return formatted_results
            
        except Exception as e:
            print(f"Exa API error: {e}")
            return []
    
    def get_content(self, url: str) -> Optional[str]:
        """Get full content of a webpage using Exa's content API"""
        try:
            if not self.exa_api_key:
                return None
            
            content_url = "https://api.exa.ai/contents"
            headers = {
                "x-api-key": self.exa_api_key,
                "Content-Type": "application/json"
            }
            
            payload = {
                "url": url,
                "type": "text"
            }
            
            response = requests.post(content_url, headers=headers, json=payload)
            response.raise_for_status()
            
            data = response.json()
            return data.get("text", "")
            
        except Exception as e:
            print(f"Exa content API error: {e}")
            return None 