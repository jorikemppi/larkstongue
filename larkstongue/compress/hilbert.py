import math
   
def hilbertMap(inputBitmap):

    def hilbertMapSubsquare(offsetX, offsetY, squareSize):

        offsetX = int(offsetX)
        offsetY = int(offsetY)
        
        if squareSize == 1:
            outputBitmap[offsetY][offsetX] = inputBitmap[offsetY][offsetX]
            return    
        
        hilbertCurve = [[0, 0]]
    
        while True:
    
            sideLength = math.sqrt(len(hilbertCurve))
    
            for i in range(0, len(hilbertCurve)):
                hilbertCurve.append([hilbertCurve[i][1], hilbertCurve[i][0] + sideLength])
                
            for i in range(len(hilbertCurve) - 1, -1, -1):
                hilbertCurve.append([2 * sideLength - hilbertCurve[i][0] - 1, hilbertCurve[i][1]])
                
            writeX = 0
            writeY = 0
            for co in hilbertCurve:
                readX = int(co[0])
                readY = int(co[1])
                outputBitmap[writeY + offsetY][writeX + offsetX] = inputBitmap[readY + offsetY][readX + offsetX]
                co[0], co[1] = co[1], co[0]
                writeX += 1
                if writeX == squareSize:
                    writeX = 0
                    writeY += 1
                    
            if sideLength == squareSize / 2:
                break
    
    def hilbertSubdivide(x, y, width, height):

        boundingSize = min(width, height)
        
        squareSize = 128
        while squareSize > boundingSize:
            squareSize /= 2
            
        hilbertMapSubsquare(x, y, squareSize)
        
        if squareSize < width:
            hilbertSubdivide(x + squareSize, y, width - squareSize, height)
            
        if squareSize < height:
            hilbertSubdivide(x, y + squareSize, squareSize, height - squareSize)
    
    outputBitmap = []
    for line in inputBitmap:
        newLine = []
        for pixel in line:
            newLine.append("")
        outputBitmap.append(newLine)
        
    width = len(inputBitmap[0])
    height = len(inputBitmap)
        
    hilbertSubdivide(0, 0, width, height)
    
    outputString = ""
    for line in outputBitmap:
        outputString += "".join(line)
        
    return outputString