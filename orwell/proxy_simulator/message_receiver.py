import zmq
import argparse
import socket
import pygame
import orwell.proxy_simulator.tanks as tanks
import orwell.proxy_simulator.world as world
import orwell.proxy_simulator.communications as communications


class Quitter(communications.BaseEventHandler):
    def _key_down(self, key):
        if (key == pygame.K_ESCAPE):
            import sys
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port", dest="port",
        help="The port to connect to to receive messages from the server.",
        default=9000, type=int)
    parser.add_argument(
        "--address", dest="address",
        help="The address to connect to to receive messages from the server.",
        default="127.0.0.1", type=str)
    parser.add_argument(
        "--push-port",
        help="The port to connect to to send messages to the server.",
        default=9001, type=int)
    parser.add_argument(
        "--push-address",
        help="The address to connect to to send messages to the server.",
        default="127.0.0.1", type=str)
    arguments = parser.parse_args()
    address = arguments.address
    port = arguments.port
    context = zmq.Context()
    pull_socket = context.socket(zmq.SUB)
    pull_socket.setsockopt(zmq.LINGER, 0)
    pull_socket.setsockopt(zmq.SUBSCRIBE, "")
    url = "tcp://%s:%i" % (address, port)
    print "subscribe to", url
    pull_socket.connect(url)
    temporary_robot_id = socket.gethostbyname(socket.gethostname())
    descriptor = tanks.TankDescriptor(temporary_robot_id)

    push_socket = context.socket(zmq.PUSH)
    push_socket.setsockopt(zmq.LINGER, 0)
    #push_socket.setsockopt(zmq.SUBSCRIBE, "")
    push_url = "tcp://%s:%i" % (arguments.push_address, arguments.push_port)
    print "push to", push_url
    push_socket.connect(push_url)

    broadcaster = communications.CombinedDispatcher(pull_socket)
    test_world = world.World(broadcaster, draw_helpers=True)
    robot = tanks.Tank(descriptor)
    #robot_event_handler = communications.TankEventHandler(descriptor)
    test_world.add(robot)
    broadcaster.register_event_handler(Quitter())
    #broadcaster.register_event_handler(robot_event_handler)
    test_world.camera_giver = robot
    broadcaster.register_listener(robot)
    broadcaster.register_listener(test_world)
    # send request to register the robot
    # // maybe this could be done in test_world.run()
    register_message = descriptor.get_register_message()
    print "regiter_message =", repr(register_message)
    push_socket.send(register_message)
    test_world.run()


if ('__main__' == __name__):
    main()
