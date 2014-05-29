import zmq
import argparse
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
        "--port", dest="port", help="The port to subscribe to.",
        default=5556, type=int)
    parser.add_argument(
        "--address", dest="address",
        help="The address to connect to.",
        default="127.0.0.1", type=str)
    arguments = parser.parse_args()
    address = arguments.address
    port = arguments.port
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.LINGER, 0)
    socket.setsockopt(zmq.SUBSCRIBE, "")
    url = "tcp://%s:%i" % (address, port)
    print url
    socket.connect(url)
    descriptor = tanks.TankDescriptor(0)

    broadcaster = communications.CombinedDispatcher(socket)
    test_world = world.World(broadcaster, draw_helpers=True)
    robot = tanks.Tank(descriptor)
    robot_event_handler = communications.TankEventHandler(descriptor)
    test_world.add(robot)
    broadcaster.register_event_handler(Quitter())
    broadcaster.register_event_handler(robot_event_handler)
    test_world.camera_giver = robot
    broadcaster.register_listener(robot)
    broadcaster.register_listener(test_world)
    test_world.run()


if ('__main__' == __name__):
    main()
