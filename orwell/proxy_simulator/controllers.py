import orwell.messages.controller_pb2 as pb_messages


class ControllerDescriptor(object):
    """
    """
    def __init__(self, port, ip):
        self._recipient = "SERVER"
        self._port = port
        self._ip = ip

    @property
    def recipient(self):
        return self._recipient

    def get_hello_message(self, name, ready=True):
        message = pb_messages.Hello()
        message.name = name
        message.ready = ready
        message.port = self._port
        message.ip = self._ip
        payload = message.SerializeToString()
        return self.recipient + " Hello " + payload

    def get_hello(self, payload):
        message = pb_messages.Hello()
        message.ParseFromString(payload)
        return (message.name, message.ready, message.port, message.ip)
