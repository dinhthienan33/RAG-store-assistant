from samples import product,chitchat
from semantic_router import Route

class Route(object):
    def __init__(self, intent, action):
        self.intent = intent
        self.action = action
    def matches(self, intent):
        return self.intent == intent

