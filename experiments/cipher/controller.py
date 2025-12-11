
def convertToASCII(string):
    """"""
    output = []
    for letter in string:
        output.append( ord(letter) )

    return " ".join([str(i) for i in output])


def convertToCaesar(string):
    """
    http://www.wikihow.com/Create-Secret-Codes-and-Ciphers
    Shifts the alphabet 3 places such that A becomes X,
    B becomes Y, etc
    """
    caesar_dict = {"a": "x",
                   "b": "y",
                   "c": "z",
                   "d": "a",
                   "e": "b",
                   "f": "c",
                   "g": "d",
                   "h": "e",
                   "i": "f",
                   "j": "g",
                   "k": "h",
                   "l": "i",
                   "m": "j",
                   "n": "k",
                   "o": "l",
                   "p": "m",
                   "q": "n",
                   "r": "o",
                   "s": "p",
                   "t": "q",
                   "u": "r",
                   "v": "s",
                   "w": "t",
                   "x": "u",
                   "y": "v",
                   "z": "w"}
    new_string = ""
    for char in string:
        if char == ' ':
            new_string += ' '
        else:
            new_string += caesar_dict[char.lower()]
    return new_string


def convertToLeet(string):
    """"""
    leet_dict = {"a":"4", "b":"8", "e":"3", "l":"1",
                 "o":"0", "s":"5", "t":"7"}
    new_string = ""
    for letter in string:
        if letter.lower() in leet_dict:
            letter = leet_dict[letter.lower()]
        new_string += letter
    return new_string


def convertToNumbers(string):
    """
    Convert a string to numbers where a=1, b=2, c=3, etc
    """
    keys = "abcdefghijklmnopqrstuvwxyz"
    values = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
              '12', '13', '14', '15', '16', '17', '18', '19', '20',
              '21', '22', '23', '24', '25', '26']
    num_dict = dict(zip(keys,values))
    new_string = ""
    for letter in string:
        if letter.lower() in num_dict:
            new_string += num_dict[letter.lower()] + " "
    return new_string


def convertFromASCII(data):
    """
    Convert from ASCII
    """
    s = ""
    if isinstance(data, str):
        for item in data.split():
            s += chr(int(item))
    else:
        # can also convert a list of integers
        for item in data:
            s += chr(item)
    return s


def convertFromCaesar(string):
    """
    Converts string from Caesar to normal
    """
    uncaesar_dict = {"x": "a",
                     "y": "b",
                     "z": "c",
                     "a": "d",
                     "b": "e",
                     "c": "f",
                     "d": "g",
                     "e": "h",
                     "f": "i",
                     "g": "j",
                     "h": "k",
                     "i": "l",
                     "j": "m",
                     "k": "n",
                     "l": "o",
                     "m": "p",
                     "n": "q",
                     "o": "r",
                     "p": "s",
                     "q": "t",
                     "r": "u",
                     "s": "v",
                     "t": "w",
                     "u": "x",
                     "v": "y",
                     "w": "z"}
    new_string = ""
    for char in string:
        if char == ' ':
            new_string += ' '
        else:
            new_string += uncaesar_dict[char.lower()]
    return new_string


def convertFromNumbers(data):
    """
    Convert a list of numbers to letters where 1=a, 2=b, 3=c, etc
    """
    keys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11',
            '12', '13', '14', '15', '16', '17', '18', '19', '20',
            '21', '22', '23', '24', '25', '26']
    values = "abcdefghijklmnopqrstuvwxyz"
    num_dict = dict(zip(keys,values))

    new_string = ""
    for char in data:
        val = num_dict[char]
        new_string += val
    return new_string


if __name__ == "__main__":
    x = convertToASCII("I love you")
    y = convertToLeet("I love you")
    print(x)
    new_x = [int(i) for i in x.split()]
    print(convertFromASCII(new_x))
    print(convertFromASCII(x))

    x = convertToCaesar("Meeting tomorrow at station")
    print("Meeting tomorrow at station =>", x)
    print("%s =>" % x, convertFromCaesar(x))

    t = convertToNumbers("Python rules")
    print("Python rules => " + t)
    print("%s => " % t, convertFromNumbers(t.split()))