
def apl_Text(key, text):
    apl = {key: {"type": "PlainText", "text": text}}
    return apl

def apl_Image(image_url):
    apl = {"image": {"sources": [
            {"url": image_url,
                "size": "small"
                },
                {
                "url": image_url,
                "size": "large"
                }
            ]}
        }
    return apl

apl_Image("https://alexa-skill-faraway-food-planner.s3.amazonaws.com/images/lacausa.jpeg")

text_types = ['primaryText','secondaryText','tertiaryText']

guatemala_text = ['Guatemala','Featured Dish: Pepían','3 Recipes']
peru_text = ['Peru','Featured Dish: La Causa','3 Recipes']
philippines_text = ['Philippines','Featured Dish: Chicken Adobo','3 Recipes']

country_texts = [
    guatemala_text,
    peru_text,
    philippines_text
]
country_images = [
"https://alexa-skill-faraway-food-planner.s3.amazonaws.com/images/pepian.jpeg",
"https://alexa-skill-faraway-food-planner.s3.amazonaws.com/images/lacausa.jpeg",
"https://alexa-skill-faraway-food-planner.s3.amazonaws.com/images/adobo.jpeg"
]

n_countries = 3
full_apl = []
for country in range(n_countries):
    apl={}
    for i in range(len(text_types)):
        apl.update(apl_Text(text_types[i], country_texts[country][i]))
    country_apl = {"listItemIdentifier": country_texts[country][0],
                    "ordinalNumber": country+1,
                    "textContent": apl}
    country_apl.update(apl_Image(country_images[country]))

    print(country_apl)
    full_apl.append(country_apl)
print(', '.join(country) for country in full_apl)

full_apl
