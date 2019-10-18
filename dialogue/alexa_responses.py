""" Events for Launch Screen """

# Welcome Message
WELCOME = "Welcome to the Faraway Food Planner. "
INTRO_PROMPT = ("You can make 3-day meal plans with recipes "
                "from faraway countries. To hear a list of available countries"
                ", you can ask me what countries are available. Let's start "
                "meal planning!")
INTRO_REPROMPT = ("To get started, you can say things like, 'Start a meal plan'")

countries_available = [
    'Guatemala',
    'Peru',
    'Philippines'
    ]

COUNTRIES_PROMPT = ("There are meal plans available from the following "
                    "countries: {}. Please select one to get "
                    "started.").format(', '.join(countries_available))

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
