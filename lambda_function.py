# -*- coding: utf-8 -*-



#-------------------------------------------------------------------------
#
# Importing Modules Used
#
#-------------------------------------------------------------------------

#import logging
import json
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import CustomSkillBuilder
from ask_sdk_core.api_client import DefaultApiClient
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractResponseInterceptor, AbstractRequestInterceptor,
    AbstractExceptionHandler)
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response
from ask_sdk_model.ui import SimpleCard
from ask_sdk_model.interfaces.alexa.presentation.apl import (
    RenderDocumentDirective, ExecuteCommandsDirective, SpeakItemCommand,
    AutoPageCommand, HighlightMode)

from ask_sdk_model.services.monetization import (
    EntitledState, PurchasableState, InSkillProductsResponse, Error,
    InSkillProduct)
from ask_sdk_model.interfaces.monetization.v1 import PurchaseResult
from ask_sdk_model.interfaces.connections import SendRequestDirective

from dialogue import alexa_responses, lumpia_recipe
from utils import create_presigned_url # to use with intent: image_url = create_presigned_url("Media/image.png")
from utils import get_all_entitled_products, is_product, is_entitled, in_skill_product_response, get_speakable_list_of_products

# Set logging -----
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
skill_name = "Faraway Food Planner"

#-------------------------------------------------------------------------
#
# Helper Functions
#
#-------------------------------------------------------------------------
def _load_apl_document(file_path):
    # type: (str) -> Dict[str, Any]
    """Load the apl json document at the path into a dict object."""
    with open(file_path) as f:
        return json.load(f)


#-------------------------------------------------------------------------
#
# Intent Handlers
#
#-------------------------------------------------------------------------

# Launch Request Handler
class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool

        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["intent_history"] = ["Launch"]

        intro_prompt = alexa_responses.INTRO_PROMPT
        in_skill_response = in_skill_product_response(handler_input)

        if isinstance(in_skill_response, InSkillProductsResponse):
            entitled_prods = get_all_entitled_products(in_skill_response.in_skill_products)
            if entitled_prods:
                logger.info("Entitled Products: {}".format(entitled_prods))
                speak_output = ("Welcome to {}, premium member. ").format(skill_name) + intro_prompt
            else:
                logger.info("No entitled products")
                speak_output = ("Welcome to {}. ").format(skill_name) + intro_prompt
        else:
            logger.info("Error calling InSkillProducts API: {}".format(in_skill_response.message))
            speak_output = "Something went wrong in loading your purchase history."

        card_title = "Faraway Food Planner"
        card_text = speak_output
        apl_document = _load_apl_document("./apl/welcome.json")
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(alexa_responses.INTRO_REPROMPT)
                # .set_card(SimpleCard(card_title, card_text))
                .add_directive(
                    RenderDocumentDirective(
                        token = "launchToken",
                        document = apl_document["document"],
                        datasources = apl_document["datasources"]
                    )
                )
                .response
        )

# Create Meal Plan Handler: 'View countries'
class CreateMealPlanIntentHandler(AbstractRequestHandler):
    """Handler for CreateMealPlan Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CreateMealPlanIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        session_attr = handler_input.attributes_manager.session_attributes
        if "intent_history" in session_attr.keys():
            session_attr["intent_history"].append("CreateMealPlanIntent")
        else:
            session_attr["intent_history"] = ["Launch", "CreateMealPlanIntent"]

        speak_output = alexa_responses.STARTPLAN
        # card_title = "Select a Country"
        # card_text = alexa_responses.country_text
        apl_document = _load_apl_document("./apl/countries.json")

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask(speak_output)
                # .set_card(SimpleCard(card_title, card_text))
                .add_directive(
                    RenderDocumentDirective(
                        token = "countries",
                        document = apl_document["document"],
                        datasources = apl_document["datasources"]
                    )
                )
                .response
        )

# Recipe Intent Handler: 'How do I make Lumpia?'
class RecipeIntentHandler(AbstractRequestHandler):
    """Handler for RecipeIntent"""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("RecipeIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        session_attr = handler_input.attributes_manager.session_attributes
        if "intent_history" in session_attr.keys():
            session_attr["intent_history"].append("RecipeIntent")
        else:
            session_attr["intent_history"] = ["Launch", "CreateMealPlanIntent", "CountrySelectorIntent", "RecipeIntent"]

        # country attribute
        selected_recipe = ask_utils.get_slot_value(handler_input, "food")
        logger.info("SELECTED RECIPE = {}".format(selected_recipe))

        selected_recipe_lower = selected_recipe.lower()

        session_attr["recipe"] = selected_recipe


        # response to country selection - FREE OR PAID UP CONTENT
        speak_output = "Here is what I found for {}.".format(selected_recipe)
        apl_document = _load_apl_document("./apl/{}.json".format(selected_recipe_lower))

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .add_directive(
                    RenderDocumentDirective(
                        token = "selected_recipe",
                        document = apl_document["document"],
                        datasources = apl_document["datasources"]
                    )
                )
                .response
        )

# Country Selector Handler: 'Show me recipes from Thailand'
class CountrySelectorIntentHandler(AbstractRequestHandler):
    """Handler for CountrySelector Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("CountrySelectorIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        session_attr = handler_input.attributes_manager.session_attributes
        if "intent_history" in session_attr.keys():
            session_attr["intent_history"].append("CreateMealPlanIntent")
        else:
            session_attr["intent_history"] = ["Launch", "CreateMealPlanIntent", "CountrySelectorIntent"]

        # country attribute
        selected_country = ask_utils.get_slot_value(handler_input, "country")
        logger.info("SELECTED COUNTRY = {}".format(selected_country))

        if selected_country.lower()[0:4] == "the ":
            selected_country_lower = selected_country[4:].lower()
        else:
            selected_country_lower = selected_country.lower()

        session_attr["country"] = selected_country_lower
        premium_countries = [text.lower() for text in alexa_responses.premium_countries]

        # response to country selection - PREMIUM CONTENT
        if selected_country_lower in premium_countries:
            in_skill_response = in_skill_product_response(handler_input)

            if in_skill_response:
                product = [
                    l for l in in_skill_response.in_skill_products
                    if l.reference_name == "premium_content_onetime"]
                logger.info("PRODUCT: {}".format(product))
                if is_entitled(product):
                    speak_output = "Here are recipes from {}.".format(selected_country)
                    apl_document = _load_apl_document("./apl/{}.json".format(selected_country_lower))
                    return handler_input.response_builder.speak(speak_output).response
                else:
                    upsell_msg = (
                        "This selection contains premium content. "
                        "You are not a premium member. Would you hear how to unlock premium content?"
                    )

                    return (
                        handler_input.response_builder
                            .add_directive(
                                SendRequestDirective(
                                    name="Upsell",
                                    payload={
                                        "InSkillProduct": {
                                            "productId": product[0].product_id,
                                        },
                                        "upsellMessage": upsell_msg
                                    },
                                    token="correlationToken"
                                )
                            )
                            .response
                    )
        else:
            # response to country selection - FREE OR PAID UP CONTENT
            speak_output = "Here are recipes from {}.".format(selected_country)
            apl_document = _load_apl_document("./apl/{}.json".format(selected_country_lower))

            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .add_directive(
                        RenderDocumentDirective(
                            token = "selected_country",
                            document = apl_document["document"],
                            datasources = apl_document["datasources"]
                        )
                    )
                    .response
            )

# Previous Intent Handler: 'Go Back'
class PreviousIntentHandler(AbstractRequestHandler):
    """Handler for Previous Intent."""
    def can_handle(self, handler_input):
        # type: (handler_input) -> bool
        return ask_utils.is_intent_name("AMAZON.PreviousIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["intent_history"].pop()
        if not session_attr["intent_history"]:
            speak_output = "There is nowhere to go back. You can say things like, 'Start a meal plan,' or 'View recipes'"
            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .ask(speak_output)
                    .response
            )
        elif session_attr["intent_history"][-1] in ["CreateMealPlanIntent", "CountrySelectorIntent"]:
            session_attr["intent_history"].pop()
            return CreateMealPlanIntentHandler.handle(self, handler_input)
        elif session_attr["intent_history"][-1] in ["RecipeIntent","MakeRecipe"]:
            session_attr["intent_history"].pop()
            return CountrySelectorIntentHandler.handle(self, handler_input)
        elif session_attr["intent_history"][-1] == "Launch":
            return LaunchRequestHandler.handle(self, handler_input)

# Touch Screen Button Handler: Touch Response on Echo Show
class confirmTouchIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return (
            handler_input.request_envelope.request.object_type == 'Alexa.Presentation.APL.UserEvent' and
            handler_input.request_envelope.request.arguments[0]
        )

    def handle(self, handler_input):

        session_attr = handler_input.attributes_manager.session_attributes
        button_argument = handler_input.request_envelope.request.arguments[0]
        countries_available = [text.lower() for text in alexa_responses.countries_available]
        recipes_available = [text.lower() for text in alexa_responses.recipes_available]


        if button_argument.lower() in countries_available:
            '''Button Action for Country Selection'''

            # country attribute
            selected_country = handler_input.request_envelope.request.arguments[0]
            session_attr["intent_history"].append("CountrySelectorIntent")

            if selected_country.lower()[0:4] == "the ":
                selected_country_lower = selected_country[4:].lower()
            else:
                selected_country_lower = selected_country.lower()
            session_attr["country"] = selected_country_lower

            # response to country selection
            speak_output = "Here are recipes from {}.".format(selected_country)
            apl_document = _load_apl_document("./apl/{}.json".format(selected_country_lower))

            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .add_directive(
                        RenderDocumentDirective(
                            token = "selected_country",
                            document = apl_document["document"],
                            datasources = apl_document["datasources"]
                        )
                    )
                    .response
            )
        elif button_argument.lower() in recipes_available:
            '''Button Action for recipe Selection'''

            # recipe attribute
            selected_recipe = handler_input.request_envelope.request.arguments[0]
            session_attr["intent_history"].append("RecipeIntent")

            selected_recipe_lower = selected_recipe.lower()
            session_attr["recipe"] = selected_recipe_lower

            # response to country selection
            speak_output = "I found a recipe for {}.".format(selected_recipe)
            apl_document = _load_apl_document("./apl/{}.json".format(selected_recipe_lower))

            return (
                handler_input.response_builder
                    .speak(speak_output)
                    .add_directive(
                        RenderDocumentDirective(
                            token = "selected_recipe",
                            document = apl_document["document"],
                            datasources = apl_document["datasources"]
                        )
                    )
                    .response
            )

        elif button_argument.lower() == "make_recipe":
            '''Button Action for recipe ingredients'''

            # recipe attribute
            selected_recipe = session_attr["recipe"]
            session_attr["intent_history"].append("MakeRecipe")

            # response to make recipe selection
            recipe_items = ', '.join([item for (item,qty) in lumpia_recipe.recipe_ingredients])

            speak_output = "To make {}, you need {}.".format(selected_recipe, recipe_items)

            return (
                handler_input.response_builder
                    .speak(speak_output)
                    # .add_directive(
                    #     RenderDocumentDirective(
                    #         token = "selected_recipe",
                    #         document = apl_document["document"],
                    #         datasources = apl_document["datasources"]
                    #     )
                    # )
                    .response
            )

        else:
            '''Button Action for default response'''
            return(
                handler_input.response_builder
                    .speak("A button was pressed, but no action is set yet.")
                    .response
            )


#-------------------------------------------------------------------------
#
# ISP Intent Handlers
#
#-------------------------------------------------------------------------
class ShoppingHandler(AbstractRequestHandler):
    """
    Following handler demonstrates how skills can handle user requests to
    discover what products are available for purchase in-skill.
    User says: Alexa, ask Premium facts what can I buy.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("ShoppingIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In ShoppingHandler")

        # Inform the user about what products are available for purchase
        in_skill_response = in_skill_product_response(handler_input)
        if in_skill_response:
            purchasable = [l for l in in_skill_response.in_skill_products
                          if l.entitled == EntitledState.NOT_ENTITLED and
                          l.purchasable == PurchasableState.PURCHASABLE]

            if purchasable:
                speech = ("Products available for purchase at this time are {}.  "
                          "To learn more about a product, say 'Tell me more "
                          "about' followed by the product name.  If you are ready "
                          "to buy say 'Buy' followed by the product name. So what "
                          "can I help you with?").format(
                    get_speakable_list_of_products(purchasable))
            else:
                speech = ("There are no more products to buy. To hear a "
                          "random fact, you could say, 'Tell me a fact', or "
                          "you can ask for a specific category you have "
                          "purchased, for example, say 'Tell me a science "
                          "fact'. So what can I help you with?")
            reprompt = "I didn't catch that. What can I help you with?"
            return handler_input.response_builder.speak(speech).ask(
                reprompt).response

class UpsellResponseHandler(AbstractRequestHandler):
    """This handles the Connections.Response event after an upsell occurs."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_request_type("Connections.Response")(handler_input) and
                handler_input.request_envelope.request.name == "Upsell")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In UpsellResponseHandler")
        session_attr = handler_input.attributes_manager.session_attributes
        if "intent_history" in session_attr.keys():
            session_attr["intent_history"].append("CreateMealPlanIntent")
        else:
            session_attr["intent_history"] = ["Launch", "CreateMealPlanIntent", "CountrySelectorIntent"]

        if handler_input.request_envelope.request.status.code == "200":
            if handler_input.request_envelope.request.payload.get(
                    "purchaseResult") == PurchaseResult.DECLINED.value:
                speak_output = (
                    "Remember, you can always unlock premium content by asking, "
                    "What can I purchase? "
                    "To return to what you were doing, say, 'Go Back'"
                )
                reprompt = "To return to what you were doing, say, 'Go Back'"

                return (
                    handler_input.response_builder
                        .speak(speak_output)
                        .ask(reprompt)
                        .response
                )

        else:
            logger.log("Connections.Response indicated failure. "
                      "Error: {}".format(
                handler_input.request_envelope.request.status.message))
            return handler_input.response_builder.speak(
                "There was an error handling your Upsell request. "
                "Please try again or contact us for help.").response

class BuyResponseHandler(AbstractRequestHandler):
    """This handles the Connections.Response event after a buy occurs."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_request_type("Connections.Response")(handler_input) and
                handler_input.request_envelope.request.name == "Buy")

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In BuyResponseHandler")
        in_skill_response = in_skill_product_response(handler_input)
        product_id = handler_input.request_envelope.request.payload.get(
            "productId")

        if in_skill_response:
            product = [l for l in in_skill_response.in_skill_products
                       if l.product_id == product_id]
            logger.info("Product = {}".format(str(product)))
            if handler_input.request_envelope.request.status.code == "200":
                speech = None
                reprompt = None
                purchase_result = handler_input.request_envelope.request.payload.get(
                    "purchaseResult")
                if purchase_result == PurchaseResult.ACCEPTED.value:
                    category_facts = all_facts
                    speech = "You have unlocked the premium content!"
                    reprompt = None
                elif purchase_result in (
                        PurchaseResult.DECLINED.value,
                        PurchaseResult.ERROR.value,
                        PurchaseResult.NOT_ENTITLED.value):
                    speech = ("Thanks for your interest in our premium membership.  "
                              "Would you like to select another country?")
                    reprompt = "Would you like to select another country?"
                elif purchase_result == PurchaseResult.ALREADY_PURCHASED.value:
                    logger.info("Already purchased product")
                    speech = " Already Purchased"
                    reprompt = None
                else:
                    # Invalid purchase result value
                    logger.info("Purchase result: {}".format(purchase_result))
                    return CatchAllExceptionHandler().handle(handler_input)

                return handler_input.response_builder.speak(speech).ask(
                    reprompt).response
            else:
                logger.log("Connections.Response indicated failure. "
                           "Error: {}".format(
                    handler_input.request_envelope.request.status.message))

                return handler_input.response_builder.speak(
                    "There was an error handling your purchase request. "
                    "Please try again or contact us for help").response


#-------------------------------------------------------------------------
#
# Default Handlers
#
#-------------------------------------------------------------------------
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Select a country to start a meal plan"
        card_title = "Help"
        card_text = speak_output

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .set_card(SimpleCard(card_title, card_text))
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .set_should_end_session(True)
                .response
        )


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response

        # Any cleanup logic goes here.

        return handler_input.response_builder.response


class IntentReflectorHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("IntentRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        intent_name = ask_utils.get_intent_name(handler_input)
        speak_output = "You just triggered " + intent_name + "."

        return (
            handler_input.response_builder
                .speak(speak_output)
                # .ask("add a reprompt if you want to keep the session open for the user to respond")
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors. If you receive an error
    stating the request handler chain is not found, you have not implemented a handler for
    the intent being invoked or included it in the skill builder below.
    """
    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# Request and Response Loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the request envelope."""
    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.info("Request Envelope: {}".format(
            handler_input.request_envelope))

class ResponseLogger(AbstractResponseInterceptor):
    """Log the response envelope."""
    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.info("Response: {}".format(response))

# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = CustomSkillBuilder(api_client=DefaultApiClient())


sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CreateMealPlanIntentHandler())
sb.add_request_handler(CountrySelectorIntentHandler())
sb.add_request_handler(RecipeIntentHandler())
sb.add_request_handler(PreviousIntentHandler())

sb.add_request_handler(ShoppingHandler())
sb.add_request_handler(UpsellResponseHandler())
sb.add_request_handler(BuyResponseHandler())

sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

sb.add_request_handler(confirmTouchIntentHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers

sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

lambda_handler = sb.lambda_handler()
