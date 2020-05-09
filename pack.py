from shared import readAssets
from shared import swapNibbles
from classes import assetCompressed

from compress.rle import *
from compress.huffman import *
from compress.hilbert import *

import math

def compressAsset(asset, args):

	global totalSize
	global totalSizeWithoutHilbert
	global totalSizeWithoutRLE
	global totalSizeWithoutHuffman	
	global currentAssetIndex
	global amountOfAssets	
	global commandStringData	
	global usesHilbert
	global usesRLE
	global usesHuffman
	
	if asset.bitmap != None:
		type = "bitmap"
		scanlineWidth = len(asset.bitmap[0])
		dataLinearRaw = ""
		for line in asset.bitmap:
			dataLinearRaw += line
		dataLinearRaw = swapNibbles(dataLinearRaw)
	else:
		type = "generic"
		scanlineWidth = len(asset.data)
		dataLinearRaw = asset.data
		
	winnerMethodID = 0
	winnerData = dataLinearRaw
	winnerSize = len(dataLinearRaw)
	bestWithoutRLE = winnerSize
	bestWithoutHuffman = winnerSize
	bestWithoutHilbert = winnerSize
	
	print("Compressing asset " + str(currentAssetIndex) + " out of " + str(amountOfAssets) + " (name: " + asset.name + ", type: " + type + ", size: " + str(len(dataLinearRaw))+")")
	
	verificationFailures = []
	
	if type == "bitmap" and args.no_hilbert == False:
	   
		dataHilbertRaw = swapNibbles(hilbertMap(asset.bitmap))
		
		rleFailed = False
		
		if args.no_rle == False:
			dataHilbertRLE = rleCompress(dataHilbertRaw)
			if rleDecompress(dataHilbertRLE) != dataHilbertRaw:
				verificationFailures.append(" - Hilbert mapping, RLE")
				rleFailed == True
			else:
				bestWithoutHuffman = min(len(dataHilbertRLE), bestWithoutHuffman)
				if len(dataHilbertRLE) < winnerSize:
					winnerSize = len(dataHilbertRLE)
					winnerMethodID = 6
					winnerData = dataHilbertRLE
					
		if args.no_huffman == False:
			dataHilbertHuffman = huffmanCompress(dataHilbertRaw)
			if huffmanDecompress(dataHilbertHuffman) != dataHilbertRaw:
				verificationFailures.append(" - Hilbert mapping, Huffman coding")
			else:
				bestWithoutRLE = min(len(dataHilbertHuffman), bestWithoutRLE)
				if len(dataHilbertHuffman) < winnerSize:
					winnerSize = len(dataHilbertHuffman)
					winnerMethodID = 5
					winnerData = dataHilbertHuffman
					
		if args.no_rle == False and args.no_huffman == False and rleFailed == False:
			dataHilbertBoth = huffmanCompress(dataHilbertRLE)
			if huffmanDecompress(dataHilbertBoth) != dataHilbertRLE:
				verificationFailures.append(" - Hilbert mapping, RLE to Huffman coding")
			elif len(dataHilbertBoth) < winnerSize:
				winnerSize = len(dataHilbertBoth)
				winnerMethodID = 7
				winnerData = dataHilbertBoth
				
	rleFailed = False
	
	errorMessageStart = ""
	if type == "bitmap" and args.no_hilbert == False:
		errorMessageStart = "Linear mapping, "
	
	if args.no_rle == False:
		dataLinearRLE = rleCompress(dataLinearRaw)
		if rleDecompress(dataLinearRLE) != dataLinearRaw:
			verificationFailures.append(" - " + errorMessageStart + "RLE")
			rleFailed = True
		else:
			bestWithoutHuffman = min(len(dataLinearRLE), bestWithoutHuffman)
			bestWithoutHilbert = min(len(dataLinearRLE), bestWithoutHilbert)        
			if len(dataLinearRLE) < winnerSize:
				winnerSize = len(dataLinearRLE)
				winnerMethodID = 2
				winnerData = dataLinearRLE
					
	if args.no_huffman == False:
		dataLinearHuffman = huffmanCompress(dataLinearRaw)
		if huffmanDecompress(dataLinearHuffman) != dataLinearRaw:
			verificationFailures.append(" - " + errorMessageStart + "Huffman coding")
		else:
			bestWithoutRLE = min(len(dataLinearHuffman), bestWithoutRLE)
			bestWithoutHilbert = min(len(dataLinearHuffman), bestWithoutHilbert)
			if len(dataLinearHuffman) < winnerSize:
				winnerSize = len(dataLinearHuffman)
				winnerMethodID = 1
				winnerData = dataLinearHuffman
					
	if args.no_rle == False and args.no_huffman == False:
		dataLinearBoth = huffmanCompress(dataLinearRLE)
		if huffmanDecompress(dataLinearBoth) != dataLinearRLE:
			verificationFailures.append(" - " + errorMessageStart + "RLE to Huffman coding")
		else:
			bestWithoutHilbert = min(len(dataLinearBoth), bestWithoutHilbert)
			if len(dataLinearBoth) < winnerSize:
				winnerSize = len(dataLinearBoth)
				winnerMethodID = 3
				winnerData = dataLinearBoth    
	
	if winnerMethodID % 4 == 0:
		winnerMethod = "Raw"
	if winnerMethodID % 4 == 1:
		winnerMethod = "Huffman coding"
		usesHuffman = True
	if winnerMethodID % 4 == 2:
		winnerMethod = "RLE"
		usesRLE = True
	if winnerMethodID % 4 == 3:
		winnerMethod = "RLE to Huffman coding"
		usesRLE = True
		usesHuffman = True
	
	if type == "bitmap" and args.no_hilbert == False:
		if winnerMethodID <= 4:
			winnerMethod = "Linear mapping, " + winnerMethod
		else:
			winnerMethod = "Hilbert mapping, " + winnerMethod
			usesHilbert = True
			
	print("Compressed size: " + str(winnerSize) + " (" + winnerMethod + ")")
	
	if len(verificationFailures) > 0:
		print("Verification failures detected:")
		for line in verificationFailures:
			print(line)
			
	newAssetCompressed = assetCompressed(asset.name, type, winnerData, scanlineWidth, winnerSize, totalSize, winnerMethodID)
	
	totalSize += winnerSize
	totalSizeWithoutHilbert += bestWithoutHilbert
	totalSizeWithoutRLE += bestWithoutRLE
	totalSizeWithoutHuffman += bestWithoutHuffman
	
	currentAssetIndex += 1
	
	print("")
	
	commandStringData += str(winnerSize) + "_"
	
	if type == "bitmap":
		commandStringData += str(scanlineWidth) + "_" + str(len(asset.bitmap) - 1)
	else:
		commandStringData += str(scanlineWidth) + "_0"
		
	for i in range(0, 3):
		commandStringData += "_" + str(winnerMethodID >> i & 1)
		
	commandStringData += "|"

	return newAssetCompressed
	
def encodeOutputCartData(args):

    # encode compressed data into the .p8 format

	global compressedAssets
	global outputGfxArea
	global outputMapArea
	global outputGffArea
	global outputMusicArea
	global outputSfxArea
	
	global writeGfxArea
	global writeMapArea
	global writeGffArea
	global writeMusicArea
	global writeSfxArea
	
	global overflowData
	
	cartDataString = ""
	
	for asset in compressedAssets:
		cartDataString += asset.data
		
	# encode __gfx__
	
	gfxDataString = cartDataString[:16384]
	while len(gfxDataString) % 2 != 0:
		gfxDataString += "0"
		
	outputGfxArea.append("__gfx__\n")
	
	outputLine = ""

	for i in range(0, len(gfxDataString), 2):
		outputByte = gfxDataString[i + 1] + gfxDataString[i]
		outputLine += outputByte
		if len(outputLine) == 128 or i == len(gfxDataString) - 2:
			while len(outputLine) < 128:
				outputLine += "0"
			outputGfxArea.append(outputLine + "\n")
			outputLine = ""
	
	if not args.gfx_only:
	
		# encode __map__
		
		if len(cartDataString) > 16384:
		
			writeMapArea = True
		
			mapDataString = cartDataString[16384 : 24576]
		
			outputMapArea.append("__map__\n")

			for i in range(0, len(mapDataString), 256):
				outputLine = mapDataString[i : i + 256]
				while len(outputLine) < 256:
					outputLine = outputLine + "0"
				outputMapArea.append(outputLine + "\n")
			
		# encode __gff__
		
		if len(cartDataString) > 24576:
		
			writeGffArea = True
		
			gffDataString = cartDataString[24576 : 25088]
			while len(gffDataString) < 512:
				gffDataString += "0"
		
			outputGffArea.append("__gff__\n")
		
			for i in range(0, 512, 256):
				outputGffArea.append(gffDataString[i : i+256] + "\n")
				
		if not args.spare_music:
		
			# encode __music__
		
			if len(cartDataString) > 25088:
			
				writeMusicArea = True
		
				musicDataString = cartDataString[25088 : 25600]

				outputMusicArea.append("__music__\n")
	
				for i in range(0, len(musicDataString), 8):
					inputPattern = musicDataString[i : i + 8]
					while len(inputPattern) < 8:
						inputPattern = inputPattern + "0"
					flagNibble = 0
					flagBitValue = 1
					strChannels = ""
					for j in range(0, 8, 2):
						inputHex = inputPattern[j : j + 2]
						inputDec = int(inputHex, 16)
						if inputDec > 127: #checks if flag bit if set
							flagNibble += flagBitValue
						flagBitValue *= 2            
						channelDec = inputDec & 127 #bitwise and, gets the channel bits
						channelHex = format(channelDec, "02x")
						strChannels = strChannels + channelHex
					flagNibbleInHex = format(int(flagNibble), "02x")
					outputMusicArea.append(flagNibbleInHex + " " + strChannels + "\n")
			
			# encode __sfx__
		
			if len(cartDataString) > 25600:
			
				writeSfxArea = True
		
				sfxDataString = cartDataString[25600 : 34304]
				outputSfxArea.append("__sfx__\n")
		
				for i in range(0, len(sfxDataString), 136):
					inputSound = sfxDataString[i : i + 136]
					while len(inputSound) < 136:
						inputSound = inputSound + "0"
					outputNotes = ""
					for j in range(0, 128, 4):
						noteHex = inputSound[j + 2 : j + 4] + inputSound[j : j + 2]
						noteDec = int(noteHex, 16)
						noteBinary = format(noteDec, "016b")
						instrumentFlag = int(noteBinary[0], 2)
						effectDec = int(noteBinary[1 : 4], 2)
						volumeDec = int(noteBinary[4 : 7], 2)
						waveformDec = int(noteBinary[7 : 10], 2) + 8 * instrumentFlag
						pitchDec = int(noteBinary[10 : 16], 2)
						pitchHex = format(pitchDec, "02x")
						waveformHex = format(waveformDec, "x")
						volumeHex = format(volumeDec, "x")
						effectHex = format(effectDec, "x")
						outputNotes = outputNotes + pitchHex + waveformHex + volumeHex + effectHex
					outputHeader = inputSound[128 : 136]
					outputSfxArea.append(outputHeader + outputNotes + "\n")
					
	if len(cartDataString) > usableCartData:
		overflowData = cartDataString[usableCartData :]
 
def doPack(args):

	print("Larkstongue v0.0.1-alpha")
    
    # set global variables
	
	global totalSize
	global totalSizeWithoutHilbert
	global totalSizeWithoutRLE
	global totalSizeWithoutHuffman
	
	totalSize = 0
	totalSizeWithoutHilbert = 0
	totalSizeWithoutRLE = 0
	totalSizeWithoutHuffman = 0
	
	global writeGfxArea
	global writeMapArea
	global writeGffArea
	global writeMusicArea
	global writeSfxArea
	
	writeGfxArea = True
	writeMapArea = False
	writeGffArea = False
	writeMusicArea = False
	writeSfxArea = False
	
	global usableCartData
	
	if args.gfx_only:
		usableCartData = 16384
	elif args.spare_music:
		usableCartData = 25088
	else:
		usableCartData = 34304
		
	global overflowData
	overflowData = ""

	global compressedAssets
	compressedAssets = []

	global commandStringData
	commandStringData = ""

	global outputGfxArea
	global outputMapArea
	global outputGffArea
	global outputMusicArea
	global outputSfxArea
	
	outputGfxArea = []
	outputMapArea = []
	outputGffArea = []
	outputMusicArea = []
	outputSfxArea = []    
		
	global usesHilbert
	global usesRLE
	global usesHuffman
	
	usesHilbert = False
	usesRLE = False
	usesHuffman = False
	
	assetList = readAssets(args.input, True)
    
    # check for duplicate names
	
	dupeList = []
	for asset in assetList:
		if asset.name in dupeList:
			print("Error! The name \"" + asset.name + "\" appears in " + args.input + " more than once")
			quit()
		dupeList.append(asset.name)
	
	global amountOfAssets
	global currentAssetIndex
		
	amountOfAssets = len(assetList)
	currentAssetIndex = 1
	
	totalRawSize = 0
	for asset in assetList:
		totalRawSize += asset.size
        
    # compress assets

	print("Compressing " + str(amountOfAssets) + " assets, total size " + str(totalRawSize) + " nibbles")
	
	print("")
	
	startPopping = False
	popToArea = None
	
	for asset in assetList:
		compressedAssets.append(compressAsset(asset, args))
	
	encodeOutputCartData(args)
	
	# generate loader
	
	cartDataSizeInBytes = math.ceil(min(totalSize, usableCartData) / 2)
	
	commandStringDataStart = "data, asset_list = mem_to_str(0, " + str(cartDataSizeInBytes) + ")"
	if len(overflowData) > 0:
		commandStringDataStart += "..\"" + overflowData + "\""
		
	commandStringData = commandStringDataStart + ", parse_table(\"" + commandStringData + "\")"
	
	commandStringLoaderCall = ""
	for asset in assetList:
		commandStringLoaderCall += asset.name + ", "
	
	commandStringLoaderCall = commandStringLoaderCall[:-2] + " = larkstongue_unpack(1)"
	
	loaderFileName = args.output
	if "." in loaderFileName:
		loaderFileName = ".".join(loaderFileName.split(".")[:-1])
	loaderFileName += "_larkstongue.p8l"
	
	file = open(loaderFileName, "w")

	file.write("function larkstongue_unpack(asset_index)\n")
	file.write("\n")
	file.write("\tcls()\n")
	if args.progressbar:
		file.write("\trect(8, 60, 120, 68, 7)\n")
		file.write("\trectfill(10, 62, 11 + " + str(108 / amountOfAssets) + " * (asset_index - 1), 66, 7)\n")
	file.write("\tflip()\n")
	file.write("\tholdframe()\n")
	file.write("\n")
	file.write("\tcurrent_asset = asset_list[asset_index]\n")
	file.write("\n")
	file.write("\tif current_asset==nil then\n")
	file.write("\t\treturn\n")
	file.write("\tend\n")
	file.write("\n")
	file.write("\tasset_string, asset, data = sub(data,1,current_asset[1]), {}, sub(data,current_asset[1]+1)\n")
	file.write("\n")
	if usesHuffman:
		file.write("\tif current_asset[4] == 1 then asset_string = huffman_decomp(asset_string) end\n")
	if usesRLE:
		file.write("\tif current_asset[5] == 1 then asset_string = rle_decomp(asset_string) end\n")
	file.write("\n")		
	file.write("\tfor i = 0, current_asset[3] do\n")
	file.write("\t\tadd(asset, sub(asset_string, i * current_asset[2] + 1, (i + 1) * current_asset[2]))\n")
	file.write("\tend\n")
	if usesHilbert:
		file.write("\n")
		file.write("\tif (current_asset[6] == 1) hilbert_unwrap()\n")
	file.write("\n")
	file.write("\tif asset_index <= #asset_list then\n")
	file.write("\t\treturn asset, larkstongue_unpack(asset_index + 1)\n")
	file.write("\tend\n")
	file.write("\n")
	file.write("end\n")
	file.write("\n")

	file.write(commandStringData + "\n" + commandStringLoaderCall + "\ndata, asset_list = nil, nil\nmemset(0, 0, " + str(usableCartData / 2) + ")\ncls()\npal()")
	file.close()
    
    # write includes and cart data to target cart
	
	try:
		file = open(args.output, "r")
		cartText = file.readlines()
		file.close
	except FileNotFoundError:
		print(args.output + " not found, generating new cart")
		cartText = ["pico-8 cartridge // http://www.pico-8.com\n",
					"version 22\n",
					"__lua__\n",
					"\n",
					"__gfx__\n"]
		file = open(args.output, "w")
		for line in cartText:
			file.write(line)
		file.close
	
	cartLine = 0
	
	def changePopToArea(targetArea, writeToThisArea):
		if writeToThisArea:
			popToArea = None
		else:
			popToArea = targetArea
			
	while cartLine < len(cartText):
	
		if cartText[cartLine].startswith("__label__"):
			break
	
		if cartText[cartLine].startswith("__"):
			startPopping = True            
			if cartText[cartLine].startswith("__gfx__"):
				if writeGfxArea:
					popToArea = None
				else:
					popToArea = outputGfxArea
			elif cartText[cartLine].startswith("__map__"):
				if writeMapArea:
					popToArea = None
				else:
					popToArea = outputMapArea
			elif cartText[cartLine].startswith("__gff__"):
				if writeGffArea:
					popToArea = None
				else:
					popToArea = outputGffArea
			elif cartText[cartLine].startswith("__music__"):
				if writeMusicArea:
					popToArea = None
				else:
					popToArea = outputMusicArea
			elif cartText[cartLine].startswith("__sfx__"):
				if writeSfxArea:
					popToArea = None
				else:
					popToArea = outputSfxArea
			else:
				startPopping = False
			
		if startPopping:
			if popToArea == None:
				cartText.pop(cartLine)
			else:
				popToArea.append(cartText.pop(cartLine))
		else:
			cartLine += 1
			
	def writeArea(outputArea):
		for i in range(len(outputArea) - 1, -1, -1):
			#print(outputArea[i])
			cartText.insert(cartLine, outputArea[i])
			
	writeArea(outputMusicArea)
	writeArea(outputSfxArea)
	writeArea(outputMapArea)
	writeArea(outputGffArea)
	writeArea(outputGfxArea)
	
	filterLines=[
		"hilbert_unwrap.p8l",
		"rle_decomp.p8l",
		"huffman_decomp.p8l",
		"hex_to_dec.p8l",
		"str_to_mem.p8l",
		"mem_to_str.p8l",
		"parse_table.p8l",
		"larkstongue.p8l"]
	
	for filterLine in filterLines:
		cartText = list(filter(lambda line: filterLine not in line, cartText))
	
	lineNumber = 3
	while cartText[lineNumber].startswith("--"):
		lineNumber += 1
		
	cartText.insert(lineNumber, "#include " + loaderFileName + "\n")
	if usesHuffman:
		cartText.insert(lineNumber, "#include include/huffman_decomp.p8l\n")
	if usesRLE:
		cartText.insert(lineNumber, "#include include/rle_decomp.p8l\n")
	if usesHilbert:
		cartText.insert(lineNumber, "#include include/hilbert_unwrap.p8l\n")
	cartText.insert(lineNumber, "#include include/parse_table.p8l\n")
	cartText.insert(lineNumber, "#include include/mem_to_str.p8l\n")
	cartText.insert(lineNumber, "#include include/str_to_mem.p8l\n")
	cartText.insert(lineNumber, "#include include/hex_to_dec.p8l\n")
	 
	file = open(args.output, "w")
	for line in cartText:
		file.write(line)
	file.close()
    
    # output summary
	
	spaceSavings = 100 * (1 - totalSize / totalRawSize)
		
	print("Total size of compressed data: " + str(totalSize) + " (" + "{:.2f}".format(spaceSavings) + " %)")
	
	suggestions = []
	
	if not args.no_hilbert:
		hilbertDifference = totalSizeWithoutHilbert - totalSize
		hilbertPercentage = 100 * hilbertDifference / totalSizeWithoutHilbert	
		suggestions.append([hilbertPercentage, "Hilbert mapping only saves you " + str(hilbertDifference) + " nibbles (" + "{:.2f}".format(hilbertPercentage) + " %) - consider using --no-hilbert to save tokens"])

	if not args.no_rle:
		rleDifference = totalSizeWithoutRLE - totalSize
		rlePercentage = 100 * rleDifference / totalSizeWithoutRLE
		suggestions.append([rlePercentage, "RLE only saves you " + str(rleDifference) + " nibbles (" + "{:.2f}".format(rlePercentage) + " %) - consider using --no-rle to save tokens"]) 

	if not args.no_huffman:
		huffmanDifference = totalSizeWithoutHuffman - totalSize
		huffmanPercentage = 100 * huffmanDifference / totalSizeWithoutHuffman
		suggestions.append([huffmanPercentage, "Huffman coding only saves you " + str(huffmanDifference) + " nibbles (" + "{:.2f}".format(huffmanPercentage) + " %) - consider using --no-hilbert to save tokens"])
	
	if len(suggestions) > 0:
		suggestions = sorted(suggestions, key = lambda line: line[0])
		if suggestions[0][0] < 2:
			print(suggestions[0][1])
		
	print("Warning! Significant amount of data (" + str(len(overflowData)) + " nibbles) encoded in Lua, increasing the compressed size of your cart")
