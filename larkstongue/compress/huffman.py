from classes import node

def huffmanCompress(input):

    output = ""
    freqTable = []
    
    for i in range(0, 256):
        freqTable.append([i, 0])
    
    for i in range(0, len(input), 2):
        byteInHex = input[i:i+2]
        byteInDec = int(byteInHex, 16)
        freqTable[byteInDec][1] += 1
        
    freqTable = sorted(freqTable, key=lambda l: l[1], reverse=True)

    nodeTable = []
    
    for charFrequency in freqTable:
        if charFrequency[1] > 0:
            nodeTable.append(node(charFrequency[1], charFrequency[0], None, None))
    
    while len(nodeTable) > 1:
        
        left = nodeTable.pop()
        right = nodeTable.pop()
        
        nodeTable.append(node(left.freq + right.freq, None, left, right))
        
        nodeTable = sorted(nodeTable, key=lambda node: node.freq, reverse=True)
        
    codeTable = []
    for i in range(0,256):
        codeTable.append(None)
    
    global outputBinary
    outputBinary = ""
    
    def huffmanCompressRecursion(node, bits):
        global outputBinary

        if node.word == None:
            outputBinary = outputBinary + "0"
            huffmanCompressRecursion(node.left, bits+"0")
            huffmanCompressRecursion(node.right, bits+"1")
        else:
            outputBinary = outputBinary + "1" + format(node.word, "08b")
            codeTable[node.word] = bits
            
    huffmanCompressRecursion(nodeTable[0], "")    
    
    messageBinary = ""
    
    for i in range(0, len(input), 2):
        byteInHex = input[i:i+2]
        byteInDec = int(byteInHex, 16)
        messageBinary = messageBinary + codeTable[byteInDec]
    
    outputBinary = outputBinary + messageBinary
    
    padLength = 4 - (len(outputBinary) + 2) % 4
    if padLength == 4:
        padLength = 0
    
    padString = format(padLength, "02b")
    outputBinary = padString + outputBinary
    
    while len(outputBinary) % 4 != 0:
        outputBinary = outputBinary + "0"

    for i in range(0, len(outputBinary), 4):
        binarySlice = outputBinary[i:i+4]
        nibbleValue = int(binarySlice, 2)
        nibbleHex = format(nibbleValue, "x")
        output = output + nibbleHex
    
    return output

def huffmanDecompress(input):

    global output
    output = ""
    
    inputBinary = ""
    
    for char in input:
        inputBinary = inputBinary + format(int(char, 16), "04b")
        
    global nodeTree
    nodeTree = node(None, None, None, None)
    
    global bitIndex
    bitIndex = 1
    
    def huffmanRebuildTree(nod):
        global nodeTree
        global bitIndex
        
        bitIndex += 1
        
        if inputBinary[bitIndex] == "0":
            nod.left = node(None, None, None, None)
            huffmanRebuildTree(nod.left)
            nod.right = node(None, None, None, None)
            huffmanRebuildTree(nod.right)
        else:
            wordBinary = inputBinary[bitIndex+1:bitIndex+9]
            wordDec = int(wordBinary, 2)
            wordHex = format(wordDec, "02x")
            nod.word = wordHex
            bitIndex += 8
            
    huffmanRebuildTree(nodeTree)
    
    def huffmanDecompressRecursion(nod):
        global nodeTree
        global bitIndex
        global output
        if nod.word != None:
            output = output + nod.word
        else:
            bitIndex += 1
            if inputBinary[bitIndex] == "0":
                huffmanDecompressRecursion(nod.left)
            else:
                huffmanDecompressRecursion(nod.right)
                
    padLengthBinary = inputBinary[:2]
    padLength = int(padLengthBinary, 2)
    
    while bitIndex < len(inputBinary) - padLength - 1:
        huffmanDecompressRecursion(nodeTree)
    
    return output