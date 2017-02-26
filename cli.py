#!/usr/bin/env python

from __future__ import print_function

from Libs.ManageAllGrafts import ManageAllGrafts

def display_menu(header, menu_list):
    """
    Display a menu and return the selection
    :param str header: The header to print at top
    :param list menu_list:
        A list of tuples of format
            (thing to display, thing to return when selected)
    :returns: One of the selected things :-)
    """
    while True:
        print()
        print(header)
        for ind, menu_item in enumerate(menu_list):
            print("{}: {}".format(ind, menu_item[0]))
        
        user_input = raw_input("Enter a selection index: ")
        # Handle the case where the user input something non-integer
        try:
            user_input_int = int(user_input)
        except:
            print("ERROR: input an integer")
            continue
        
        # Handle the case where the user input something out of range
        if user_input_int not in range(len(menu_list)):
            print("ERROR: select something on the menu")
            continue

        # Handle the case where the user did something else invalid
        try:
            selected_entry = menu_list[user_input_int]
        except:
            print("ERROR: bad selection, you bad mother")
            continue

        # This might break if the programmer doesn't provide proper input
        # Let it break - how else would you handle programmer stupidity?
        return selected_entry[1]

def add_graft(manager):
    print()
    addr = raw_input("Address (blank to cancel): ")
    if addr == "":
        print("CANCELLED")
        return

    port = raw_input("Port (blank to cancel): ")
    if port == "":
        print("CANCELLED")
        return
    try:
        port = int(port)
    except:
        print("ERROR: invalid port - cancelling - only integers accepted")
        return

    if port < 0 or port > 65535:
        print("ERROR: invalid port - cancelling")
        return

    """ TODO: Maybe later
    architecture = raw_input("Architecture of graft to add (default: X64): ")
    if architecture == "":
        architecture = "X64"
    """

    new_ind = manager.add_graft(addr, port)

    print("Added graft index: {}".format(new_ind))

def list_grafts(manager):
    print()
    print("Available grafts:")
    for index, addr, port in manager.list_grafts():
        print("{}: {} port {}".format(index, addr, port))

def select_graft(manager, menu_title):
    """
    Display a list of grafts, and return the integer selected
    :return int or None: None if the user selected "back"
    """
    graft_list = manager.list_grafts()

    graft_menu = [("{}: {} port {}".format(index, addr, port), index) 
            for index, addr, port in graft_list]
    graft_menu.append(("Back", None))

    return display_menu(menu_title, graft_menu)

def command_graft(manager):
    selected = select_graft(manager, "Send Command to Graft: ")
    if selected is None:
        print("CANCELLED")
        return

    command = raw_input("Command (blank to cancel): ")
    if command == "":
        print("CANCELLED")
        return

    manager.command_graft(selected, command)
    print("Command sent - response will be received in background")


def show_command_responses(manager):
    selected = select_graft(manager, "Show Response From Graft: ")
    if selected is None:
        print("CANCELLED")
        return

    print()
    for c_and_r in manager.list_graft_responses(selected):
        print("{}: {}".format(c_and_r.command, c_and_r.response))

def shutdown(manager):
    quit(0)

def mainloop():
    main_menu = [
            ("Add graft", add_graft),
            ("List grafts", list_grafts),
            ("Command graft", command_graft),
            ("Show command responses", show_command_responses),
            ("Quit", shutdown),
            ]

    manager = ManageAllGrafts()

    while True:
        selected_action = display_menu("Main Menu", main_menu)
        selected_action(manager)

if __name__ == "__main__":
    mainloop()
