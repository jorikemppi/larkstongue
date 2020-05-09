class assetRaw:
    def __init__(self, name, bitmap, data, size):
        self.name = name
        self.bitmap = bitmap
        self.data = data
        self.size = size
        
class assetCompressed:
    def __init__(self, name, type, data, scanlineWidth, size, offset, method):
        self.name = name
        self.type = type
        self.data = data
        self.scanlineWidth = scanlineWidth
        self.size = size
        self.offset = offset
        self.method = method

class node:
    def __init__(self, freq, word, left, right):
        self.freq = freq
        self.word = word
        self.left = left        
        self.right = right