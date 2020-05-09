from classes import assetRaw

def swapNibbles(input):

    output = ""
    for i in range(0, len(input), 2):
        output += input[i + 1] + input[i]
    return output
    
def readAssets(path, terminateIfNotFound):

    assetList = []

    try:
        file = open(path, "r")
    except FileNotFoundError:
        if terminateIfNotFound == True:
            print(path + " not found!")
            quit()
        return assetList
    assetData = file.readlines()
    file.close()
    
    name = ""
    data = ""
    bitmap = []
    
    for line in assetData:
    
        if line.startswith("name"):
            name = line.strip("\n")[5:]
            
        if line.startswith("data"):
            data = line.strip("\n")[5:]
            
        if line.startswith("bitmap"):
            bitmap.append(line.strip("\n")[7:])
            
        if line.startswith("-"):
            if name != "":                
                if len(bitmap) > 0:
                    size = len(bitmap) * len(bitmap[0])
                    assetList.append(assetRaw(name, bitmap, None, size))
                elif data != "":
                    size = len(data)
                    assetList.append(assetRaw(name, None, data, size))
            name = ""
            data = ""
            bitmap = []
    
    return assetList
    