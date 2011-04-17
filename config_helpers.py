

"""
Helpers for getting user input for configuration
"""


def get_int(message, value=''):
    """
    Prompts a user for an input int. Uses the default value if no
    value is entered by the user. Uses default value of parse error happens
    """
    msg2 = ' '.join([message, ' (', str(value), ') (int): '])
    new_value = raw_input(msg2)
    if(new_value == "" or new_value == "\n"):
        return int(value)

    try:
        return int(new_value)
    except ValueError:
        print "Invalid integer, '%s', using default value" % (str(new_value))
        return int(value)


def get_string(message, default):
    """get a string value from the command line"""
    msg2 = ''.join([message, ' (', str(default), ') (string): '])
    value = raw_input(msg2)

    if not len(value):
        return default

    return value


def get_yes_or_no(message, value=True):
    """Get yes/no value from the command line"""

    msg2 = ''.join([message, ' (', str(value), ') (Y,n): '])
    new_value = raw_input(msg2)

    if(new_value == "" or new_value == "\n"):
        return value

    if(new_value == 'Y' or new_value == 'Yes' or new_value == 'y'):
        return True

    elif(new_value == 'n' or new_value == 'no' or new_value == 'N'):
        return False

    raise InputError("Please choose y/n")
