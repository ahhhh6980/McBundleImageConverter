from imageProcessing import setPixel, getPixel, getAverageColor, getColor, getClosestColor, detectExtension
from multiprocessClass import NonDaemon, nPool
import multiprocessing.pool
from PIL import Image
from sys import exit
import numpy as np
import glob
import os


try: tAdjust = int(tAdjust)
except:	tAdjust = 1


colors = []


for palette in os.listdir("palettes"):

	print("LOADING "+palette, "\n")
	
	for image in os.listdir("palettes/"+palette):
	
		currentImage = Image.open("palettes/"+palette+"/"+image) 
		print("palettes/"+palette+"/"+image)
		
		colors.append([getAverageColor(currentImage),image[:-4]])
		print(colors[-1],"\n")


print("COLORS: ")
for e in colors:
	print(e)


print("\nColors: ", len(colors),"\n")


def generateCommandItems(inData):
	pieceNum = inData[0]
	segment = inData[1]
	image = inData[2]
	height = inData[3]
	
	command = ""
	
	for i in range(*segment):
		for j in range(height):
			currentColor = getColor(getPixel([i,j], image),colors)
			command+='{Count:1b,id:\\"'+currentColor[1]+'\\"},'
	
	return [pieceNum,command]


def processFile(filename):

	ex = detectExtension(filename)
	print("\nPROCESSING ",filename[:-len(ex)]," ...")
	
	
	workImage = Image.open(("images/"+filename)) 
	width, height = workImage.size
	preview = Image.new('RGB', (width, height), color = 'red')


	if(dithering):
		print(filename+" Started dithering")
		for i in range(width):
			for j in range(height):
				oldPixel = getPixel( [i,j], workImage )
				newPixel = getClosestColor(oldPixel,colors)
			
				setPixel( [i,j], workImage, getClosestColor(newPixel,colors) )
				quant_error = np.array(oldPixel) - np.array(newPixel)
				
				if( i<width-1 ): 
					setPixel([i+1,j], workImage, 
							 ( np.array(getPixel([i+1,j], workImage)) + (quant_error * (7 / 16)) ).astype(int))		
				if( i>0 and j<height-1 ): 
					setPixel([i-1,j+1], workImage, 
							 ( np.array(getPixel([i-1,j+1], workImage)) + (quant_error * (3 / 16)) ).astype(int))
				if( j<height-1 ): 
					setPixel([i,j+1], workImage, 
							 ( np.array(getPixel([i,j+1], workImage)) + (quant_error * (5 / 16)) ).astype(int))
				if( i<width-1 and j<height-1 ): 
					setPixel([i+1,j+1], workImage, 
						 	 ( np.array(getPixel([i+1,j+1], workImage)) + (quant_error * (1 / 16)) ).astype(int))
		print(filename+" Finished dithering")
	
	
	inData = []
	seg = width//6
	for n in range(6):
		inData.append( [n, [seg*(n),seg*(n+1)], workImage, height])
		if(seg*(n+1)<width and n == 5):
			inData.append( [n, [seg*(n+1),width], workImage, height])
	
	
	print(filename+" Started assembling function")
	if __name__ == '__main__':
		pool = nPool(3)
		output = pool.map(generateCommandItems, inData)
		pool.close()
		pool.join()
		
		
	output.sort()
	
	
	if(isGif):
		command = '{"function":"set_nbt","tag":"{\\"Items\\":['
		items = ""
		for e in output:
			print(filename, e[0])
			items += e[1]

		command+= items+'],bundle:\\" '+filename+' \\"}"}'

		file1 = open("item_modifiers/"+filename[:-len(ex)]+".json","w") 
		file1.write(command)
		file1.close()
		
	else:
		items = ""
		for e in output:
			print(filename, e[0])
			items += e[1]
		command = "give @p bundle{Items:["+items[:-1]+"]}"
		file1 = open("functions/giveBundle_"+filename[:-len(ex)]+".mcfunction","w") 
		file1.write(command)
		file1.close()
		
		
	print(filename+" \nCommand generated and saved! Size: "+str(len(command)))
	return 1


everything = ((input("Do you wish to process every image in images/?\n(!!LARGE FILES MAY TAKE A WHILE!!)\n[Y/n]:") or "y").lower()=="y")
isGif = ((input("Do you wish to process a gif?\n(!!LARGE FILES MAY TAKE A WHILE!!)\n[y/N]:") or "n").lower()=="y")
dithering = ((input("\nDo you want dithering?\n(This is best for images with a wide range of colors)\n[y/N]:") or "n").lower()=="y")


files = []
if(isGif): 

	directory = 'item_modifiers'
	for f in os.listdir(directory):
		os.remove(os.path.join(directory, f))
		
	everything = False
	im = Image.open("gifs/"+input("\nType the file name of the image (including extension) that you wish to process\n[imageName]: "))
	
	for frame in range(0,im.n_frames):
		im.seek(frame)
		name = "test_gif_frame_"+str(frame)+".png"
		im.save("images/"+name)
		files.append(name)


if(everything==True and isGif==False):

	files = []
	for fileN in os.listdir("images"):
	
		if(detectExtension(fileN)!=".gif" and
		   detectExtension(fileN)!=".blank"):
		   
			files.append(fileN)
	
	
if(everything==False and isGif==False): 
	files = [input("\nType the file name of the image (including extension) that you wish to process\n[imageName]: ")]


if __name__ == '__main__':
	print()
	print(files)
	print()
	p = nPool(4)
	output = p.map(processFile, files)
	p.close()
	p.join()


def getLastNumber(string):
    ints, i = [""], 0
    for e in string[:-1*len(detectExtension(string))]:
        if e.isnumeric(): 
            ints[i] += e
        elif( ints[-1] != "" ):
            ints.append("")
            i += 1
    return int( [e for e in ints if e.isnumeric()][-1] )


if(isGif):
	
	
	directory = 'images'
	for f in os.listdir(directory):
		if f in files:
			os.remove(os.path.join(directory, f))
		else: continue
	
	
	directory = 'functions'
	for f in os.listdir(directory):
		os.remove(os.path.join(directory, f))


	tag = "start"
	start = 'scoreboard objectives add '+tag+' dummy\ngive @a minecraft:bundle{bundles:"'+tag+'"}'
	run = """scoreboard players add @a[scores={"""+tag+"""=1..}] """+tag+""" 1\n
	scoreboard players set @a[scores={"""+tag+"""=..1}, nbt={Inventory:[{id:"minecraft:bundle",tag:{bundles:\""""+tag+"""\"}}]}] """+tag+""" 1\n
	scoreboard players set @a[scores={"""+tag+"""=1..}, nbt=!{Inventory:[{id:"minecraft:bundle",tag:{bundles:\""""+tag+"""\"}}]}] """+tag+""" 0\n
	"""


	print("\ngenerating gif commands...")
	
	
	fileList = []
	for modifier in os.listdir("item_modifiers"):
		fileList.append([getLastNumber(modifier),modifier[:-5]])
	fileList.sort()

	print(fileList)

	for e in fileList:
		print(e)
		run+="""item entity @a[scores={"""+tag+"""="""+str(int(e[0])+1)+"""},nbt={Inventory:[{id:"minecraft:bundle",tag:{bundles:\""""+tag+"""\"},Count: 1b,Slot: 0b}]}] hotbar.0 modify bundles:"""+e[1]+"""\n"""
	run+="""scoreboard players set @a[scores={"""+tag+"""="""+str(int(fileList[-1][0])+2)+"""..}] """+tag+""" 1"""


	startS = open("functions/start.mcfunction","w") 
	startS.write(start)
	startS.close()


	runS = open("functions/run.mcfunction","w") 
	runS.write(run)
	runS.close()
	print("gif commands finished writing!")

