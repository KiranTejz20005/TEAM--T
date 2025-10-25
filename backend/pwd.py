"""
Mock pwd module for Windows compatibility.
This module provides stubs for Unix-only pwd module.
"""

class struct_passwd:
    """Mock struct_passwd class."""
    def __init__(self):
        self.pw_name = "user"
        self.pw_passwd = "x"
        self.pw_uid = 1000
        self.pw_gid = 1000
        self.pw_gecos = ""
        self.pw_dir = "/home/user"
        self.pw_shell = "/bin/sh"

def getpwuid(uid):
    """Mock getpwuid function."""
    return struct_passwd()

def getpwnam(name):
    """Mock getpwnam function."""
    return struct_passwd()

def getpwall():
    """Mock getpwall function."""
    return [struct_passwd()]
