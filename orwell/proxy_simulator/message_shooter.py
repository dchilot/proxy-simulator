import zmq
import argparse
import pygame
import socket
import orwell.proxy_simulator.tanks as tanks
import orwell.proxy_simulator.communications as communications
import orwell.messages.controller_pb2 as pb_controller
import orwell.messages.server_game_pb2 as pb_server_game


class Quitter(communications.BaseEventHandler):
    def _key_down(self, key):
        if (key == pygame.K_ESCAPE):
            import sys
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port", dest="port", help="The port to publish to.",
        default=5556, type=int)
    parser.add_argument(
        "--address", dest="address",
        help="The address used to bind.",
        default="*", type=str)
    parser.add_argument(
        "--skip-hello",
        action="store_true",
        default=False)
    parser.add_argument(
        "--subscriber-port",
        help="The port to subscribe to.",
        default=9000,
        type=int)
    parser.add_argument(
        "--subscriber-address", dest="subscriber_address",
        help="The address used to connect.",
        default="127.0.0.1", type=str)
    arguments = parser.parse_args()
    port = arguments.port
    address = arguments.address
    context = zmq.Context()
    pub_socket = context.socket(zmq.PUB)
    pub_socket.setsockopt(zmq.LINGER, 10)
    pub_socket.bind("tcp://%s:%i" % (address, port))
    messengers = []
    temporary_robot_id = socket.gethostbyname(socket.gethostname())
    if (arguments.skip_hello):
        robot_id = temporary_robot_id
    else:
        message = pb_controller.Hello()
        message.name = "Nono"
        message.ready = True
        payload = message.SerializeToString()
        pub_socket.send(temporary_robot_id + " Hello " + payload)
        subscribe_socket = context.socket(zmq.SUB)
        subscribe_socket.setsockopt(zmq.LINGER, 0)
        subscribe_socket.setsockopt(zmq.SUBSCRIBE, temporary_robot_id)
        full_address = "tcp://%s:%i" % (
            arguments.subscriber_address, arguments.subscriber_port)
        print "full_address =", full_address
        subscribe_socket.connect(full_address)
        reply = subscribe_socket.recv()
        dest, message_type, payload = reply.split(" ", 2)
        if ("Welcome" == message_type):
            message = pb_server_game.Welcome()
            message.ParseFromString(payload)
            print "We are controlling robot", message.robot
            robot_id = str(message.id)
            print "ID =", robot_id
        else:
            import sys
            sys.stderr.write("We are not welcome, quit.\n")
            sys.exit(0)
    descriptor = tanks.TankDescriptor(robot_id)
    #robot = tanks.Tank(descriptor)
    robot_event_handler = communications.TankEventHandler(descriptor)
    messengers.append(robot_event_handler)
    messengers.append(Quitter())
    pygame.init()
    pygame.display.set_mode((640, 480))
    pygame.display.set_caption('Message shooter')
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()
    previous_str = ""
    while (True):
        events = pygame.event.get()
        for messenger in messengers:
            messenger.handle_events(events)
            for message in messenger.get_messages():
                new_str = str(message)
                if (previous_str != new_str):
                    print "send message:", repr(new_str)
                    previous_str = new_str
                pub_socket.send(message)
        #clock.tick(1 / 0.05)
        clock.tick(40)
        #time.sleep(0.5)


if ('__main__' == __name__):
    main()
