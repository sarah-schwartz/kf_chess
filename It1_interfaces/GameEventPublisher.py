from Command import Command
from MessageBroker import MessageBroker
from EventQueue import EventQueue
from EventType import EventType
class GameEventPublisher:
        def __init__(self, broker: MessageBroker):
                self.broker = broker

        def send(self, event_type: EventType, command: Command):
                self.broker.publish(event_type, command)
