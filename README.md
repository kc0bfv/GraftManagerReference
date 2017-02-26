# Graft Manager

## Purpose
This software will be used as part of a Python 2 course.

The software enables deployment of shellcode, and the tasking of commands, to listeners created by msfvenom.

## Usage
Deploy listeners (found in Stage0Binaries) to hosts and execute them.  Use the cli or the web-view to task the listeners.

./cli

## Requirements
Python 2.7

## Structure
- Libs
  - files that provide most of the functionality
- Stage0Binaries
  - listeners created with msfvenom, and a Makefile to create more
- UnitTests
  - tests to verify the functionality of the Libs
