import datetime
from Queue import Queue
import threading

import Architectures
from ManageSysgraft import ManageSysgraft

class CommandAndResponse(object):
    """
    A class to associate graft commands with responses

    Instances map commands to their responses, with datetimes for each
    """
    def __init__(self):
        self._command = None
        self._response = None
        self.command_time = None
        self.response_time = None

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value
        self.command_time = datetime.datetime.now()

    @property
    def response(self):
        return self._response

    @response.setter
    def response(self, value):
        self._response = value
        self.response_time = datetime.datetime.now()


class ManageAllGrafts(object):
    """
    A class that manages a set of grafts
    """
    def __init__(self):
        self.cur_graft_index = 0
        """
        self.graft_list will be a dictionary of format
        {
            graft_index_number: [ManageSysgraft Object,
                                    [CommandAndResponse, CommandAndResponse...]
                                    ]
            graft_index_number...
        }
        """
        self.graft_list = dict()
        self.graft_list_lock = threading.Lock()

    def add_graft(self, addr, port, architecture=Architectures.X64):
        """
        Add and create a new graft, return its index
        :param str addr: The address of the new graft
        :param int port: The port of the new graft
        :param Architecture architecture: The architecture of the target
        :returns int: The new graft's index
        """
        new_graft = ManageSysgraft(addr, port, architecture)
        with self.graft_list_lock:
            self.graft_list[self.cur_graft_index] = [new_graft, list()]
            self.cur_graft_index += 1
            return self.cur_graft_index - 1

    def del_graft(self, index):
        """
        Remove and close a graft by index
        """
        with self.graft_list_lock:
            graft, _ = self.graft_list.pop(index)
        graft.close_graft()

    def list_grafts(self):
        """
        :returns list: A list of (index, addr, port) tuples
        """
        with self.graft_list_lock:
            return [
                    (index,
                        self.graft_list[index][0].addr,
                        self.graft_list[index][0].port)
                    for index in sorted(self.graft_list.keys())
                    ]

    def command_graft(self, index, command):
        """
        Send a command to a graft, don't wait for the response
        """
        with self.graft_list_lock:
            graft, _ = self.graft_list[index]

        def __run_cmd():
            c_and_r = CommandAndResponse()
            c_and_r.command = command
            c_and_r.response = graft.send_command(command)
            with self.graft_list_lock:
                if index in self.graft_list:
                    self.graft_list[index][1].append(c_and_r)
                else:
                    # The index got deleted while we were waiting for response
                    pass

        command_thread = threading.Thread(target=__run_cmd)
        command_thread.start()

    def list_graft_responses(self, index):
        """
        Return the list of CommandAndResponse objects for a graft (by index)
        """
        with self.graft_list_lock:
            return list(self.graft_list[index][1])

