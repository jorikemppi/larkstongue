def rleCompress(input):

    output = ""
    length = 0
    char = input[0]
    
    for input_char in input[1:]:
        if input_char == char:
            length += 1
            if length == 16:
                output = output + "f" + char
                length = 0
        else:
            output = output + format(length, "x") + char
            char = input_char
            length = 0
    
    output = output + format(length, "x") + char
    
    return output
    
def rleDecompress(input):

    output = ""
    
    for sliceLocation in range(0, len(input), 2):
        length = int(input[sliceLocation], 16) + 1
        char = input[sliceLocation + 1]
        for i in range(0, length):
            output = output + char
            
    return output