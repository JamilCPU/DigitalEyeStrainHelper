def validateIsIntegerAndBelow60Minutes(input):
    if input == "":
        return True
    if input.isdigit():
        if int(input) <= 60:
            return True
        else:
            return False
    else:
        return False
