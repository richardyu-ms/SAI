
import socket
import time
# from ptf.packet import *
# from ptf.testutils import *
import argparse

def parse_arg():
    parser = argparse.ArgumentParser(
        description="""
        Open a socket on local interface
        """
    )

    parser.add_argument(
        "-i", type=str, dest="if_name", 
        help="interface name", required=True)
    return parser.parse_args()


def open_packet_socket(hostif_name):
    """
    Open a linux socket

    Args:
        hostif_name (str): socket interface name

    Return:
        sock: socket ID
    """
    eth_p_all = 3
    sock = socket.socket(socket.AF_PACKET, socket.SOCK_RAW,
                         socket.htons(eth_p_all))
    sock.bind((hostif_name, eth_p_all))
    print("bind to host interface: {}".format(hostif_name))
    sock.setblocking(0)

    return sock


def socket_verify_packet(sock, timeout=5):
    """
    Verify packet was received on a socket

    Args:
        pkt (packet): packet to match with
        sock (int): socket ID
        timeout (int): timeout

    Return:
        bool: True if packet matched
    """
    max_pkt_size = 9100
    timeout = time.time() + timeout
    match = False


    while time.time() < timeout:
        try:
            packet_from_tap_device = sock.recv(max_pkt_size)
            print("packet: {}".format(packet_from_tap_device))

        except BaseException:
            pass

    return match

if __name__ == '__main__':
    args = parse_arg()
    if_name = args.if_name
    if_sock = open_packet_socket(if_name)
    socket_verify_packet(if_sock)
