# -*- coding: utf-8 -*-

# This sample demonstrates handling intents from an Alexa skill using the Alexa Skills Kit SDK for Python.
# Please visit https://alexa.design/cookbook for additional examples on implementing slots, dialog management,
# session persistence, api calls, and more.
# This sample is built using the handler classes approach in skill builder.
import logging
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        
        speak_output = "Bienvenido. Di quién quieres que empiece o pregunta las reglas."
        attr = handler_input.attributes_manager.session_attributes
        # El usuario debe decir quién empieza para que empiece el juego
        attr["en_juego"] = False

        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class EmpezarIntentHandler(AbstractRequestHandler):
    """Handler para el inicio del juego."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("EmpezarIntent")(handler_input)

    def handle(self, handler_input):
        # Se resetean las variables del juego en session_attributes
        attr = handler_input.attributes_manager.session_attributes
        attr["opcion_actual"]= 0
        attr["opciones_alexa"] = ["haz te un polo", "un qué", "un polo"]
        attr["ronda"] = 1
        attr["repeticiones"] = 0
        attr["en_juego"] = True
        
        id = handler_input.request_envelope.request.intent.slots["usuario"].resolutions.resolutions_per_authority[0].values[0].value.id

        speak_output = "Recibido. Comienzas Tú "
        if id and id == "0":
            claculate_next(attr)
            speak_output ="Comienzo yo. Hazte un polo"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
        

    
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "El juego se basa en repetir tres frases en orden: hazte un polo, un qué y un polo. En cada turno, uno dice una frase. El juego funciona por rondas: en cada ronda se incrementa en uno el número de veces que hay que repetir cada frase antes de pasar a la siguiente."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class JuegoIntentHandler(AbstractRequestHandler):
    """Handler para el desarrollo del juego."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("juegoIntent")(handler_input)

    def handle(self, handler_input):
        # Se busca el id
        id = handler_input.request_envelope.request.intent.slots["opcion"].resolutions.resolutions_per_authority[0].values[0].value.id
        id = int(id)
        attr = handler_input.attributes_manager.session_attributes
        
        speak_output = ""
        
        if attr["en_juego"]:
            speak_output = process_input(attr, id)
            calculate_next2(attr)
        else:
            speak_output = "Debes empezar un nuevo juego. ¿Quién quieres que empiece?"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

def process_input(session_attributes, id_opcion):
    """
    Procesa la opción del jugador y calcula la respuesta de Alexa según el estado del juego
    """
    if session_attributes["opcion_actual"] != id_opcion:
        to_return = "Opción incorrecta. Deberías haber dicho: " + session_attributes["opciones_alexa"][session_attributes["opcion_actual"]] + ". Has acabado en la ronda " + str(session_attributes["ronda"]) + ". ¿Quién empieza ahora?"
        # El usuario debe empezar un nuevo juego
        session_attributes["en_juego"] = False
        return to_return

    claculate_next(session_attributes)
    to_return = session_attributes["opciones_alexa"][session_attributes["opcion_actual"]]
    return to_return


def claculate_next(session_attributes):
    """
    Actualiza el estado del juego para que se pueda recibir la siguiente frase
    """
    session_attributes["repeticiones"] += 1
    if session_attributes["repeticiones"] == session_attributes["ronda"]:
        session_attributes["repeticiones"] = 0
        session_attributes["opcion_actual"] += 1
        if session_attributes["opcion_actual"] > 2:
            session_attributes["opcion_actual"] = 0
            session_attributes["ronda"] += 1

def calculate_next2(session_attributes):
    """
    Hace lo mismo que calculate_next. Daba error llamar dos veces a la misma función en un mismo intent handle
    """
    session_attributes["repeticiones"] += 1
    if session_attributes["repeticiones"] == session_attributes["ronda"]:
        session_attributes["repeticiones"] = 0
        session_attributes["opcion_actual"] += 1
        if session_attributes["opcion_actual"] > 2:
            session_attributes["opcion_actual"] = 0
            session_attributes["ronda"] += 1
            
class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        speak_output = "¡Hasta nunqui!"

        return (
            handler_input.response_builder
                .speak(speak_output)
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
        speak_output = "Lo siento, no entendí eso. Dí quién quieres que empice otra vez"
        attr = handler_input.attributes_manager.session_attributes
        attr["en_juego"] = False
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class FallbackHandler(AbstractRequestHandler):
    """The intent reflector is used for interaction model testing and debugging.
    It will simply repeat the intent the user said. You can create custom handlers
    for your intents by defining them above, then also adding them to the request
    handler chain below.
    """
    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return ask_utils.is_request_type("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):

        
        
        speak_output = "Lo siento, no entendí eso. Prueba otra vez por favor."
        

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
# The SkillBuilder object acts as the entry point for your skill, routing all request and response
# payloads to the handlers above. Make sure any new handlers or interceptors you've
# defined are included below. The order matters - they're processed top to bottom.


sb = SkillBuilder()
sb.add_request_handler(FallbackHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(JuegoIntentHandler())
sb.add_request_handler(EmpezarIntentHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
sb.add_request_handler(IntentReflectorHandler()) # make sure IntentReflectorHandler is last so it doesn't override your custom intent handlers



lambda_handler = sb.lambda_handler()