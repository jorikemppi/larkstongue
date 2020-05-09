from shared import readAssets

def doExtract(args):

    print("Larkstongue v0.0.1-alpha")

    def readGfx():
        readLine = line.strip("\n")
        if len(readLine) > 0:
            areaGfx.append(readLine)
        
    def readGff():
        readLine = line.strip("\n")        
        if len(readLine) > 0:
            areaGff.append(readLine)
        
    def readMap():
        readLine = line.strip("\n")        
        if len(readLine) > 0:
            areaMap.append(readLine)
        
    def readSfx():
        readLine = line.strip("\n")
        
        if len(readLine) > 0:
            encodedLine = ""
            header = readLine[:8]
        
            for i in range(8, len(readLine), 5):
                pitchHex = readLine[i : i + 2]            
                waveformHex = readLine[i + 2]            
                volumeHex = readLine[i + 3]            
                effectHex = readLine[i + 4]
            
                pitchDec = int(pitchHex, 16)
                pitchBinary = format(pitchDec, "06b")
            
                waveformDec = int(waveformHex, 16)
                waveformBinary = format(waveformDec, "04b")
                instrumentBit = waveformBinary[0]
                waveformBinary = waveformBinary[1:]
            
                volumeDec = int(volumeHex, 16)
                volumeBinary = format(volumeDec, "03b")
            
                effectDec = int(effectHex, 16)
                effectBinary = format(effectDec, "03b")
            
                noteBinary = waveformBinary[1:] + pitchBinary + instrumentBit + effectBinary + volumeBinary + waveformBinary[0]
                noteDec = int(noteBinary, 2)
                noteHex = format(noteDec, "04x")
            
                encodedLine = encodedLine + noteHex
            
            encodedLine = encodedLine + header
        
            areaSfx.append(encodedLine)
        
    def readMusic():
        readLine = line.strip("\n")
        
        if len(readLine) > 0:
        
            flagHex = readLine[1]
            flagDec = int(flagHex, 16)
            flagBinary = format(flagDec, "04b")
        
            channelsHex = []
        
            for i in range(3, len(readLine), 2):
                channelsHex.append(readLine[i : i+2])
        
            encodedBinary = []
            for i in range(3, -1, -1):
                encodedBinary.append(flagBinary[i])
            
            encodedLine = ""
            
            for i in range(0, 4):
                channelDec = int(channelsHex[i], 16)
                channelBinary = format(channelDec, "07b")
                encodedBinary[i] = encodedBinary[i] + channelBinary
                encodedDec = int(encodedBinary[i], 2)
                encodedHex = format(encodedDec, "02x")
                encodedLine = encodedLine + encodedHex
            
            areaMusic.append(encodedLine)
        
    def cropBitmap():
    
        if len(areaGfx) == 0:
            print("Bitmap not found on cart!")
            quit()
    
        cropScanline = ""
        while len(cropScanline) < 128:
            cropScanline += args.bgcolor
        
        while areaGfx[0] == cropScanline:
            areaGfx.pop(0)
            
        while areaGfx[-1] == cropScanline:
            areaGfx.pop(-1)
        
        marginFound = False
        for leftMargin in range(0, 127):
            for y in range(0, len(areaGfx)):
                if areaGfx[y][leftMargin] != args.bgcolor:
                    marginFound = True
                    break
            if marginFound == True:
                break
                
        marginFound = False
        for rightMargin in range(128, 0, -1):
            for y in range(0, len(areaGfx)):
                if areaGfx[y][rightMargin - 1] != args.bgcolor:
                    marginFound = True
                    break
            if marginFound == True:
                break
        
        cropWidth = rightMargin - leftMargin
        if cropWidth % 2 != 0:
            if rightMargin < 128:
                rightMargin += 1
            else:
                leftMargin -= 1

        for i in range(0, len(areaGfx)):
            areaGfx[i] = areaGfx[i][leftMargin : rightMargin]
            
    def swapGfxNibbles():
    
        for i in range(0, len(areaGfx)):
            line = areaGfx[i]
            swappedLine = ""
            for j in range(0, len(line), 2):
                swappedLine += line[j + 1] + line[j]
            areaGfx[i] = swappedLine
            
    def writeBitmap():
    
        for line in areaGfx:
            outputFile.write("bitmap=" + line + "\n")
            
    def areaToString(areaID):
    
        if areaID == "gfx":
            readArea = areaGfx
            areaLength = 16384
        elif areaID == "gff":
            readArea = areaGff
            areaLength = 512
        elif areaID == "map":
            readArea = areaMap
            areaLength = 8192
        elif areaID == "sfx":
            readArea = areaSfx
            areaLength = 8704
        elif areaID == "music":
            readArea = areaMusic
            areaLength = 512
        
        outputString = ""
        for line in readArea:
            outputString += line
        
        while len(outputString) < areaLength:
            if readArea == areaMusic:
                outputString += "40"
            else:
                outputString += "0"
            
        return outputString
        
    def writeSoundtrack():
    
        fullString = ""
        fullString += areaToString("music")
        fullString += areaToString("sfx")
        
        outputFile.write("data=" + fullString + "\n")
        
    def writeAllData():
    
        fullString = ""
        fullString += areaToString("gfx")
        fullString += areaToString("map")
        fullString += areaToString("gff")
        fullString += areaToString("music")
        fullString += areaToString("sfx")
        
        outputFile.write("data=" + fullString + "\n")        
    
    areaGfx = []
    areaGff = []
    areaMap = []
    areaSfx = []
    areaMusic = []

    try:
        file = open(args.input, "r")
    except FileNotFoundError:
        print(args.input + " not found!")
        quit()
    cartContent = file.readlines()
    file.close()
    
    if args.source == "bitmap":
        acceptedBgColorInputs = "0123456789abcdef"
        if len(args.bgcolor) != 1 or args.bgcolor not in acceptedBgColorInputs:
            print("Error: Background color input must be a single hexadecimal digit in lowercase!")
            quit()

    readMode = 0    
    readModes = {   1: readGfx,
                    2: readGff,
                    3: readMap,
                    4: readSfx,
                    5: readMusic
    }
    
    for line in cartContent:
        if len(line) > 1:
            if line.startswith("__gfx__") and args.source in ["bitmap", "gfx", "all"]:
                readMode = 1
            elif line.startswith("__gff__") and args.source in ["gff", "all"]:
                readMode = 2
            elif line.startswith("__map__") and args.source in ["map", "all"]:
                readMode = 3
            elif line.startswith("__sfx__") and args.source in ["soundtrack", "sfx", "all"]:
                readMode = 4
            elif line.startswith("__music__") and args.source in ["soundtrack", "music", "all"]:
                readMode = 5
            elif line.startswith("__label__"):
                readMode = 0
            elif readMode != 0:
                readModes[readMode]()
                
    if args.source == "bitmap":
        cropBitmap()
    elif len(areaGfx) > 0:
        swapGfxNibbles()
    
    assetList = readAssets(args.output, False)

    dupeFound = False
    for asset in assetList:
        if asset.name == args.assetname:
            dupeFound = True
    if dupeFound:
        print("An asset named \"" + args.assetname + "\" already found in " + args.output + ", overwrite?")
        while True:
            userInput = input("(y/n): ")
            if userInput == "y":
                break
            if userInput == "n":
                print("Extract cancelled!")
                quit()
    
    assetList = list(filter(lambda a: a.name != args.assetname, assetList))
    
    try:
        outputFile = open(args.output, "w")
    except PermissionError:
        print("Error! Cannot write to " + args.output + " due to a permission error")
        
    for a in assetList:
        outputFile.write("name=" + a.name + "\n")
        if a.bitmap != None:
            for line in a.bitmap:
                outputFile.write("bitmap=" + line + "\n")
        if a.data != None:
            outputFile.write("data=" + a.data + "\n")
        outputFile.write("-\n")
        
    outputFile.write("name=" + args.assetname + "\n")
    if args.source == "bitmap":
        writeBitmap()
    elif args.source == "soundtrack":
        writeSoundtrack()
    elif args.source == "all":
        writeAllData()
    else:
        outputString = areaToString(args.source)
        outputFile.write("data=" + outputString + "\n")
    outputFile.write("-\n")
    
    outputFile.close
    print("Asset extracted successfully!")