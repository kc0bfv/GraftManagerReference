#!/usr/bin/env python

from itertools import izip_longest
import socket
import time
import threading
import unittest

from Libs.Architectures import X64
from Libs.ManageSysgraft import ManageSysgraft
from Libs.ManageAllGrafts import ManageAllGrafts

LOCALHOST = "127.0.0.1"
LOCALPORTLIST = [59122, 59123, 59124]
LOCALPORT = LOCALPORTLIST[0]

TIMEOUT_TIME = 6
SLEEP_TIME = 2

# One command/response entry per localportlist entry
COMMAND_RESPONSE_LIST = [
        ("get yourself something nice\n",
            ["a cartridge and a mare brie", "five golden rings"]),
        ("real nice\n",
            ["null post's fixed!", "newel post, dangit", "clark"]),
        ("calculate meaning of life\n",
            ["CPE 1704 TKS", "42", "Seg fault dummy"]),
        ]

def _setup_listener(host, port):
    """
    Setup and return a listening tcp socket on host, port
    """
    listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind((host, port))
    listener.listen(1)
    return listener

class Test_ManageSysgraft(unittest.TestCase):
    """
    Test the ManageSysgraft module
    """
    def setUp(self):
        """
        Start all tests in this class with an open graft and send/recv at
        self.graft and self.accepted_conn respectively
        """
        self.graft = None
        def __run_graft():
            # This will run as its own thread
            # The next line will block until we get a connection, but we
            # need to start a listener at the same time that will also block,
            # so one needs to block a different thread
            self.graft = ManageSysgraft(LOCALHOST, LOCALPORT)

        self.listener = _setup_listener(LOCALHOST, LOCALPORT)
        
        self.graft_thread = threading.Thread(target=__run_graft)
        self.graft_thread.start()

        self.accepted_conn, accepted_addr = self.listener.accept()
        
        # Wait for the thread to have assigned self.graft before continuing
        self.graft_thread.join()

    def tearDown(self):
        self.listener.close()
        self.accepted_conn.close()


    def test_connect_recv(self):
        """
        Make sure we receive the correct shellcode
        """
        recvd = self.accepted_conn.recv(4096)
        self.assertEqual(recvd, X64.shell)

    def test_cmd_recv(self):
        """
        Try sending a command, and responses, and make sure we get correct
        data both ways
        """
        command, responses = COMMAND_RESPONSE_LIST[0]

        cmd_retval = []
        def __send_graft_cmd():
            cmd_retval.append(self.graft.send_command(command))

        recvd_shellcode = self.accepted_conn.recv(4096)

        graft_cmd_thread = threading.Thread(target=__send_graft_cmd)
        graft_cmd_thread.start()

        recvd_cmd = self.accepted_conn.recv(4096)
        self.assertEqual(recvd_cmd, command)

        for ind_response in responses:
            self.accepted_conn.sendall(ind_response)
            time.sleep(SLEEP_TIME)

        graft_cmd_thread.join()

        self.assertEqual(cmd_retval[0], "".join(responses))

class Test_ManageAllGrafts(unittest.TestCase):
    """
    Test the ManageAllGrafts module
    """
    def test_runthrough(self):
        manager = ManageAllGrafts()
        self.graft_indexes = None

        def __run_graft():
            # run these blocking lines in a separate thread so we can respond
            # to them with blocking accept()'s
            self.graft_indexes = [manager.add_graft(LOCALHOST, port)
                    for port in LOCALPORTLIST]

        # Setup the listeners, so the add_grafts won't just die
        listeners = [_setup_listener(LOCALHOST, port) 
                for port in LOCALPORTLIST]

        # Let the grafts start connecting
        graft_thread = threading.Thread(target=__run_graft)
        graft_thread.start()

        # Accept their connections
        # accepted becomes a list of tuples, like (connection, addr)
        # it'd be nicer if the connections were in a list by themselves...
        accepted = [listener.accept() for listener in listeners]

        # This next line is a slick way of splitting this list up, but
        # slick isn't always very understandable...
        # accepted_conns, accepted_addrs = zip(*accepted)

        # Here's an understandable way of spllitting the lists, but definitely
        # not slick.  Readability counts.
        accepted_conns = [conn for conn, addr in accepted]
        accepted_addrs = [addr for conn, addr in accepted]

        # Wait for the thread to have assigned graft_indexes before continuing
        graft_thread.join()

        # Test that the manager is setup as we would expect
        manager_results = manager.list_grafts()
        # The list we get back isn't guaranteed to be in any specific order...
        # We'll use sets to parse out the results into something we can check
        index_results = {graft[0] for graft in manager_results}
        addr_results = {graft[1] for graft in manager_results}
        port_results = {graft[2] for graft in manager_results}
        # There should be two unique indexes, whatever they are
        self.assertEqual(len(index_results), len(LOCALPORTLIST)) 
        self.assertEqual(index_results, set(self.graft_indexes))
        # The port and hosts should match these sets...
        self.assertEqual(addr_results, {LOCALHOST})
        self.assertEqual(port_results, set(LOCALPORTLIST))

        # Receive the shellcodes, assume they're gtg
        for conn in accepted_conns:
            _ = conn.recv(4096)

        # Separate out the commands and responses for ease of use...
        commands = [command for command, response in COMMAND_RESPONSE_LIST]
        responses = [response for command, response in COMMAND_RESPONSE_LIST]

        # Now, use the grafts to send the commands.  This should not block,
        # if it does, the test will hang - a sign of a failed test :-)
        for graft_ind, command in zip(self.graft_indexes, commands):
            manager.command_graft(graft_ind, command)

        # Make 'em sweat it out for a hot second
        time.sleep(SLEEP_TIME)

        # Receive their commands, check them
        for conn, command in zip(accepted_conns, commands):
            recvd_cmd = conn.recv(4096)
            self.assertEqual(recvd_cmd, command)

        # Send responses slowly, but don't let the grafts timeout
        # Ok, this one isn't too readable - response_round_list becomes
        # a list of the first response, then the second response, then third,
        # etc. ordered by command.  * and zip are crazy, I know.
        for response_round_list in izip_longest(*responses):
            for conn, response in zip(accepted_conns, response_round_list):
                if response is not None:
                    # response will be None if one response list is shorter
                    # than others...
                    conn.sendall(response)
            time.sleep(SLEEP_TIME)

        # Let the grafts timeout waiting for command response
        time.sleep(TIMEOUT_TIME)

        # Now check each graft for having received the proper responses in
        # the proper order
        desired_resps = ["".join(resp_list) for resp_list in responses]
        for graft_ind, desired_resp in zip(self.graft_indexes, desired_resps):
            actual_resps = manager.list_graft_responses(graft_ind)

            # Each graft only got one command, should only have one response
            self.assertEqual(len(actual_resps), 1)
            self.assertEqual(actual_resps[0].response, desired_resp)

        # Delete 'em
        for graft_ind in self.graft_indexes:
            manager.del_graft(graft_ind)


if __name__ == "__main__":
    unittest.main()
