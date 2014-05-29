import zmq
import argparse
import socket
import pygame
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
        "--port",
        help="The port to push to.",
        default=9001,
        type=int)
    parser.add_argument(
        "--address",
        help="The address to connect to.",
        default="127.0.0.1",
        type=str)
    parser.add_argument(
        "--skip-hello",
        action="store_true",
        default=False)
    parser.add_argument(
        "--subscriber-port",
        help="The port to subscribe to.",
        default=9000,
        type=int)
    arguments = parser.parse_args()
    port = arguments.port
    address = arguments.address
    context = zmq.Context()
    push_socket = context.socket(zmq.PUSH)
    push_socket.connect("tcp://%s:%i" % (address, port))
    messengers = []
    temporary_robot_id = socket.gethostbyname(socket.gethostname())
    if (arguments.skip_hello):
        robot_id = temporary_robot_id
    else:
        message = pb_controller.Hello()
        message.name = "Nono"
        message.ready = True
        message.port = 0
        message.ip = temporary_robot_id
        payload = message.SerializeToString()
        push_socket.send(temporary_robot_id + " Hello " + payload)
        subscribe_socket = context.socket(zmq.SUB)
        subscribe_socket.setsockopt(zmq.LINGER, 0)
        subscribe_socket.setsockopt(zmq.SUBSCRIBE, temporary_robot_id)
        subscribe_socket.connect(
            "tcp://%s:%i" % (address, arguments.subscriber_port))
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
    pygame.time.Clock()
    previous_str = ""
    while (True):
    #if (True):
        events = pygame.event.get()
        for messenger in messengers:
            messenger.handle_events(events)
            for message in messenger.get_messages():
                new_str = str(message)
                if (previous_str != new_str):
                    print "send message:", repr(new_str)
                    previous_str = new_str
                #push_socket.send_unicode(message)
                push_socket.send(message)
        #clock.tick(1 / 0.05)
        #clock.tick(40)
        pygame.time.delay(40)


if ('__main__' == __name__):
    main()
