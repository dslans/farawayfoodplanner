""" Events for Launch Screen """

# Welcome Message
WELCOME = "Welcome to the Faraway Food Planner. "
INTRO_PROMPT = "You can ask for recipes from a country, or for a list of available countries. What would you like to do?"
welcome_options = []

# Meal Planner Prompt
STARTPLAN = "Select a country for some recipes:"

# Meal Planner
COUNTRY_REQUEST = "Select a country to start your meal planning"
meal_bundles_dict = {
    'England': ['Meat Pie', 'Fish and Chips', 'Chicken Tikka Masala', ' Full English Breakfast for Dinner'],
    'France': ['Coq Au Vin', 'Ratatouille', 'Croque Madame', 'Quiche Lorraine'],
    'Thailand': ['Red or Green Curry', 'Pad Thai', ' Chicken Cashew', 'Larb'],
    'Philippines': ['Valenciana', 'Chicken Adobo', 'Adobado', 'Pancit'],
    'Peru': ['Aji de Gallina', 'Lomo Saltado', 'Ceviche', 'Quinoa'],
    'Guatemala': ['Pepian']
}
countries = [key for key, value in meal_bundles_dict.items()]
country_text = " \r\n ".join(countries)

countries_available = [
    'England',
    'France',
    'Guatemala',
    'Peru',
    'Philippines',
    'Thailand'
    ]

recipes_available = [
    'Lumpia'
    ]

premium_countries = [
    'Peru',
    'Philippines'
    ]

country_error = "Sorry, we don't have any recipes from that country yet. \
\r\n Please select a valid country. \
\r\n To hear a list of valid countries, say, \
\r\n What countries are available?"
