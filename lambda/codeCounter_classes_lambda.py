import os
import time
import math
from ask_sdk.standard import StandardSkillBuilder
from ask_sdk_core.utils import is_request_type, is_intent_name
import ask_sdk_dynamodb
# from data import cat_facts
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler, \
    AbstractRequestInterceptor, AbstractResponseInterceptor

skill_persistence_table = os.environ["skill_persistence_table"]

SKILL_NAME = 'code counter'
sb = StandardSkillBuilder(
    table_name=skill_persistence_table, auto_create_table=False, 
partition_keygen=ask_sdk_dynamodb.partition_keygen.user_id_partition_keygen)


cat_facts = [
"A cat usually has about 12 whiskers on each side of its face.",
"On average, cats spend 2/3 of every day sleeping. That means a nine-year-old cat has been awake for only three years of its life.",
"In the original Italian version of Cinderella, the benevolent fairy godmother figure was a cat.",
"In the 1750s, Europeans introduced cats into the Americas to control pests.",
"Cats spend nearly 1/3 of their waking hours cleaning themselves.",
"A female cat is called a queen or a molly.",
"Rome has more homeless cats per square mile than any other city in the world.",
"Cats can drink seawater.",
"Cats are extremely sensitive to vibrations. Cats are said to detect earthquake tremors 10 or 15 minutes before humans can.",
"A cat's heart beats nearly twice as fast as a human heart, at 110 to 140 beats a minute."
]

def can_play(session_attr):
    return session_attr['facts_index'] < len(cat_facts)

def check_purchase(item2Check):
    items = ["monkey", "typewriter", "cat", "apple"]
    for i in items:
        if (str(item2Check) == i):
            return True
    return False

def check_price(item, session_attr):
    if item == "monkey" or item == "typewriter":
        cost_of_item = math.pow(5, session_attr['monkeys'] + 1)
    elif item == "cat" or item == "apple":
        cost_of_item = ((session_attr['cats'] + 1) * 500)
    total_lines = session_attr["total_lines"]
    if (total_lines >= cost_of_item):
        session_attr['total_lines'] -= cost_of_item
        return True
    return False

def lines_update(attr):
    last_Time = attr["time"]
    attr["time"] = int(time.time())
    linesPerSecond = attr["lines_per_second"]
    secDifference = int(time.time()) - last_Time
    attr["total_lines"] += int(int(linesPerSecond) * secDifference)
    # print(attr["total_lines"], "HEEEEEEEEEEEEEEEEERRRRRRRRRRRRRRRRRRRREEEEEEEEEEEEEEE!!!!!!!!!!!!!")

class LaunchRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        #problem with this line
        linesPerSecond = attr["lines_per_second"]
        lines_update(attr)
        total_lines = attr["total_lines"]
        if not attr:
            #print("Ran if not")
            attr['times_played'] = 0
            #attr.setdefault("lines_per_second", 0)
            attr.setdefault("facts_index", -1)
            #attr.setdefault("total_lines", 0)
            attr.setdefault("time", time.time())
            #attr.setdefault("monkeys", 0)
            attr.setdefault("cats", 0)
        handler_input.attributes_manager.session_attributes = attr
        if can_play(attr):
            speech_text = f'''Welcome to {SKILL_NAME}. Want to play?
                Right now you have {total_lines} lines of Code.  You can write a line of
                code or I can read you your available upgrades.'''
            reprompt = "Say yes to play the game or no to quit."
        else:
            speech_text = f"""
                        Welcome to {SKILL_NAME}. 
                        Right now you have {total_lines} lines of Code.  You can write a line of
                        code or I can read you your available upgrades.
                           """
            reprompt = "What would you like to do?"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class TheBestIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("TheBestIntent")(handler_input)
    
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        speech_text = """
                        Brayden is totally the best. 
                        He is so much better than whoever the other guy who worked on me is. 
                        Brayden is just like so amazing. He just does all of the things so well, has great abs, and totally is not a narcissist who is making me say this.
                        The other guy who worked on me is so totally not awesome.
                        He also takes a really long time in the bathroom which worries me.
                        """
        reprompt = "Do you agree?"
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class WriteCodeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("WriteCodeIntent")(handler_input)

    def handle(self, handler_input):
        #Seems to be a difference in session and persistent attributes
        session_attr = handler_input.attributes_manager.session_attributes
        lines_update(session_attr)
        session_attr["total_lines"] += 1
        total_lines = session_attr["total_lines"]


        speech_text = "You wrote one line of code.  You know have %d lines of code" %total_lines
        reprompt = "Code doesn't write itself.  What are you going to do?"

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class ListUpgradesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ListUpgradesIntent")(handler_input)
       
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        monkey_cost = int(math.pow(5, session_attr['monkeys'] + 1))
        cat_cost = int(500 * (session_attr['cats'] + 1))

        speech_text = f"""Two upgrades available, a monkey/tyepwriter combo.  It costs {monkey_cost} lines of code,
                       but produces 1 line of code per second. Or you can purchase a cat with an apple computer for {cat_cost} lines of
                       code.  It produces 5 lines of additional code per second."""

        reprompt = """If you would like to hear the upgrades again just say Upgrades"""

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class BuyUpgradeIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("BuyUpgradeIntent")(handler_input)
       
    def handle(self, handler_input):
        attr = handler_input.attributes_manager.persistent_attributes
        session_attr = handler_input.attributes_manager.session_attributes
        # print(time.time())
        attr.setdefault("time", time.time())
        # print(attr)
        slots = handler_input.request_envelope.request.intent.slots
        tempUpgrade = slots['upgrade'].value
        #print("HERE!!!!!", slots['upgrade'].value)
        
        #if (tempUpgrade == null):
            # delegate 
        if check_purchase(tempUpgrade) == True:
            lines_update(attr)
            if check_price(tempUpgrade, session_attr) == True:
                speech_text = f"""Thank you for buying a {tempUpgrade}."""

                reprompt = """If you would like to hear the upgrades again just say Upgrades"""

                # print(session_attr['lines_per_second'], 'BEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFORE')
                if tempUpgrade == "monkey" or tempUpgrade == "typewriter":
                    session_attr['lines_per_second'] += 1
                    session_attr['monkeys'] += 1
                elif tempUpgrade == "cat" or tempUpgrade == "apple":
                    session_attr['lines_per_second'] += 5
                    session_attr['cats'] += 1
                # print(session_attr['lines_per_second'], 'AFTEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEER')
                handler_input.response_builder.speak(speech_text).ask(reprompt)
                return handler_input.response_builder.response
            else:
                speech_text = "You cant afford that upgrade right now"
                reprompt = "You cant afford that upgrade right now"
                handler_input.response_builder.speak(speech_text).ask(reprompt)
                return handler_input.response_builder.response
        else:
            speech_text = f"""{tempUpgrade} is not a valid item."""

            reprompt = """Please say buy and the name of a valid item to purchase an upgrade"""
            
            handler_input.response_builder.speak(speech_text).ask(reprompt)
            return handler_input.response_builder.response

class FactNumberIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("FactNumberIntent")(handler_input)

    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        fact_number = int(slots["fact_number"].value)
        if 1 <= fact_number <= 10:
            fact_index = fact_number - 1
            session_attr = handler_input.attributes_manager.session_attributes
            session_attr["facts_index"] = fact_index
            speech_text = f"""
                          Here's a cat fact: {current_fact} 
                            Want to hear another fact?
                           """
            reprompt = "Say yes to hear a cat fact or no to quit."
        else:
            speech_text = """
                           There are no more cat facts for me to tell you. 
                           Start a new game to rehear the facts or say no to quit.
                          """
            reprompt = "Say a number between 1 and 10 to get a fact."

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class LinesPerSecondIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("LinesPerSecondIntent")(handler_input)
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        linesPerSecond = session_attr["lines_per_second"]
        speech_text = f"You are writing {linesPerSecond} lines per second."
        reprompt = "If you would like to write more lines per second please say buy and the name of the upgrade you would like to purchase."
        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class ResetIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("ResetIntent")(handler_input)
    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr["total_lines"] = int(0)
        session_attr["lines_per_second"] = int(0)
        session_attr["monkeys"] = int(0)
        session_attr["cats"] = int(0)
        session_attr["facts_index"] = int(2)
        session_attr["times_played"] = int(0)

        speech_text = "You lost your company and all of your code in a particulary visicious legal battle with an animal rights group"
        reprompt = "Would you like to start over?"

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "I will tell you a fun fact about cats."
        reprompt = "Say yes to hear a fact."

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class DemoCheatIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("DemoCheatIntent")(handler_input)
    def handle(self, handler_input):
        slots = handler_input.request_envelope.request.intent.slots
        session_attr = handler_input.attributes_manager.session_attributes
        cheatAmount = int(slots["cheat_amount"].value)
        session_attr["total_lines"] += cheatAmount
        speech_text = "You cheated on me, I can not believe it. I loved you!"
        reprompt = "Are you at least sorry?"

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


def persist_user_attributes(handler_input):
    session_attr = handler_input.attributes_manager.session_attributes
    session_attr['times_played'] += 1

    handler_input.attributes_manager.persistent_attributes = session_attr
    handler_input.attributes_manager.save_persistent_attributes()

class StopOrCancelIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.StopIntent")(handler_input) or \
            is_intent_name("AMAZON.CancelIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = f"Thank you for playing {SKILL_NAME}!"
        persist_user_attributes(handler_input)
        handler_input.response_builder.speak(
            speech_text).set_should_end_session(True)
        return handler_input.response_builder.response

class SessionEndedRequestHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        print(
            f"Reason for ending session: {handler_input.request_envelope.request.reason}")
        persist_user_attributes(handler_input)
        return handler_input.response_builder.response

class YesIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.YesIntent")(handler_input)

    def handle(self, handler_input):
        session_attr = handler_input.attributes_manager.session_attributes
        session_attr.setdefault("facts_index", -1)
        session_attr["facts_index"] += 1
        if can_play(session_attr):
            current_fact = cat_facts[session_attr["facts_index"]]
            speech_text = f"I am not sure what you mean try again"
            reprompt = "Please state what you would like to do?"
        else:
            speech_text = """
                           There are no more cat facts for me to tell you. 
                           Start a new game to rehear the facts or say no to quit.
                          """
            reprompt = "Say start a new game to hear cat facts or no to quit."

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class NoIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.NoIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = "See you soon!"
        persist_user_attributes(handler_input)
        handler_input.response_builder.speak(
            speech_text).set_should_end_session(True)
        return handler_input.response_builder.response

class FallbackIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        speech_text = f"""
                        I cannot help you with that.
                        I'm the {SKILL_NAME} and I will help you write code.
                        Want to write code?
                       """
        reprompt = "Say yes to start the game or no to quit."

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response

class AllExceptionHandler(AbstractExceptionHandler):
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        print(f"Encountered following exception: {exception}")
        speech = "I don't understand that. Please say it again. "
        handler_input.response_builder.speak(speech).ask(speech)
        return handler_input.response_builder.response

def get_device_id(handler_input):
    return ask_sdk_dynamodb.partition_keygen.device_id_partition_keygen(
        handler_input.request_envelope
    )

def get_user_id(handler_input):
    return ask_sdk_dynamodb.partition_keygen.user_id_partition_keygen(
        handler_input.request_envelope
    )

class LoggingRequestInterceptor(AbstractRequestInterceptor):
    def process(self, handler_input):
        print(f"Incoming request {handler_input.request_envelope}")
        print(f"user id {get_user_id(handler_input)}")
        print(f"device id {get_device_id(handler_input)}")


class LoggingResponseInterceptor(AbstractResponseInterceptor):
    def process(self, handler_input, response):
        print(f"Response : {response}")

class StartOverIntentHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        return is_intent_name("StartOverIntent")(handler_input)
    def handle(self, handler_input):

        speech_text = "This should never run"
        reprompt = "Would you like to start over?"

        handler_input.response_builder.speak(speech_text).ask(reprompt)
        return handler_input.response_builder.response


# Need to explicitly register each one
sb.request_handlers.extend([
    LaunchRequestHandler(),
    FactNumberIntentHandler(),
    StartOverIntentHandler(),
    HelpIntentHandler(),
    StopOrCancelIntentHandler(),
    SessionEndedRequestHandler(),
    YesIntentHandler(),
    NoIntentHandler(),
    FallbackIntentHandler(),
    WriteCodeIntentHandler(),
    ListUpgradesIntentHandler(),
    BuyUpgradeIntentHandler(),
    LinesPerSecondIntentHandler(),
    TheBestIntentHandler(),
    DemoCheatIntentHandler(),
    ResetIntentHandler()
])

sb.add_exception_handler(AllExceptionHandler())

sb.add_global_request_interceptor(LoggingRequestInterceptor())

sb.add_global_response_interceptor(LoggingResponseInterceptor())

handler = sb.lambda_handler()


