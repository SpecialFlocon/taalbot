"""
Custom-defined exceptions.
"""


class Error(Exception):
    pass

class MissingConfigKeyError(Error):
    """
    Exception raised on incomplete/incorrect configuration file

    Attributes:
      parameter -- name of the missing required parameter
    """

    def __init__(self, parameter):
        self.parameter = parameter

    def __str__(self):
        return "Missing required configuration parameter: {}".format(self.parameter)

class RoleDoesNotExist(Error):
    """
    Exception raised when trying to work with a role that does not exist

    Attributes:
      name -- name of the role that was attempted access
    """

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return "Role does not exist on the server: {}".format(self.parameter)
