import enum


class Event:

    class Initialization:

        PostLoadEvent = 0x1948C

class EventHolder:

    def __init__(self):
        self.events = {}

    def add_event_listener(self, event):
        def decorator(func):

            if event not in self.events:
                self.events[event] = []
            self.events[event].append(func)

            return func



        return decorator

    def call_event_listener(self, event, *args, **kwargs):

        if event in self.events:
            for listener in self.events[event]:
                listener(*args, **kwargs)
        else:
            print(f"No listeners registered for event: {event}")