import multiprocessing.pool
from PIL import Image
from sys import exit
import numpy as np
import os

class NonDaemon(multiprocessing.Process):
    def _get_daemon(self):
        return False
    def _set_daemon(self, value):
        pass
    daemon = property(_get_daemon, _set_daemon)

class nPool(multiprocessing.pool.Pool):
    Process = NonDaemon

dithering = (input("\nDo you want dithering?\n(This is best for images with a wide range of colors)\n[Y/n]:")=="Y")
bgRange = input("\nEnter the lightness value of the bg in range 0-255\n(if you dont know what this is, just hit enter)\n>:")

try: 
	bgRange = int(bgRange)
	if(bgRange<0 and bgRange > 255):
		bgRange = 140
except:	bgRange = 140

try: tAdjust = int(tAdjust)
except:	tAdjust = 1

def setPixel(p, image, color):
	image.putpixel( (p[1],p[0]), (color[0], color[1], color[2]) )
	
def getPixel(p, image):
	try:
		c = [*image.getpixel((p[1],p[0]))]
		if(len(c)==3): c.append(255)
	except: 
		try:
			r,g,b,a = image.getpixel((p[1],p[0]))
			c = [r,g,b,a]
		except:
			try:
				r,g,b = image.getpixel((p[1],p[0]))
				c = [r,g,b, 255]
			except:
				c = [0,0,0,0]
	return c
	
def getAverageColor(image):
	bgColor = np.array([bgRange,bgRange,bgRange])
	w, h = image.size
	average = np.array([0,0,0,0])

	for i in range(w):
		for j in range(h):
			average += np.array(getPixel([i,j],image)) 
			
	average = average // (w*h)
	add = np.array([*((bgColor * (1 - average[-1]/255)).astype(int)),0])
	average = (average*( average[-1]/255)).astype(int) + add
	return np.array([*average[:-1],255])

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

print()
print("Colors: ", len(colors))
print()

def getColor(c):
	if(len(c) != 4): c.append(255)	
	return(colors[ min([ [np.sqrt(sum([v*v for v in (colors[i][0][:-1] - c[:-1])])), i] for i in range(len(colors)) ])[1] ])

def getClosestColor(c):
	if(len(c) != 4): c.append(255)	
	return(colors[ min([ [np.sqrt(sum([v*v for v in (colors[i][0][:-1] - c[:-1])])), i] for i in range(len(colors)) ])[1] ][0])

def detectExtension(name):
	for i,e in enumerate(name):
		if(e=="."):
			return name[i:]
	return ""

def generateCommand(inData):
	pieceNum = inData[0]
	segment = inData[1]
	image = inData[2]
	height = inData[3]
	
	command = ""
	
	for i in range(*segment):
		for j in range(height):
			currentColor = getColor(getPixel([i,j], image))
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
				newPixel = getClosestColor(oldPixel)
			
				setPixel( [i,j], workImage, getClosestColor(newPixel) )
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
			
		print(filename+" Finished dithering, saved preview")
	
	command = '{"function":"set_nbt","tag":"{\\"Items\\":['

	inData = []
	seg = width//6
	for n in range(6):
		inData.append( [n, [seg*(n),seg*(n+1)], workImage, height])
		if(seg*(n+1)<width and n == 5):
			inData.append( [n, [seg*(n+1),width], workImage, height])
	
	print(filename+" Started assembling function")
	if __name__ == '__main__':
		pool = nPool(3)
		output = pool.map(generateCommand, inData)
		pool.close()
		pool.join()
    
	output.sort()
	items = ""
	for e in output:
		print(filename, e[0])
		items += e[1]

	command+= items+'],bundle:\\" '+filename+' \\"}"}'

	file1 = open("item_modifiers/"+filename[:-len(ex)]+".json","w") 
	file1.write(command)
	file1.close()

	print(filename+" \nCommand generated and saved! Size: "+str(len(command)))
	
	return 1

count = (input("Do you wish to process every image in images/?\n(!!LARGE FILES MAY TAKE A WHILE!!)\n[Y/n]:")=="n")

files = []
for fileN in os.listdir('images'):
	files.append(fileN)
	
if(count): 
	files = [input("\nType the file name of the image (including extension) that you wish to process\n[imageName]: ")]

if __name__ == '__main__':
	p = nPool(4)
	output = p.map(processFile, files)
	p.close()
	p.join()

import glob

directory = glob.glob('functions/')
for f in directory: os.remove(f)

directory = glob.glob('item_modifiers/')
for f in directory: os.remove(f)
    
tag = "start"
start = 'scoreboard objectives add '+tag+' dummy\ngive @a minecraft:bundle{bundles:"'+tag+'"}'

run = """scoreboard players add @a[scores={"""+tag+"""=1..}] """+tag+""" 1\n

scoreboard players set @a[scores={"""+tag+"""=..1}, nbt={Inventory:[{id:"minecraft:bundle",tag:{bundles:\""""+tag+"""\"}}]}] """+tag+""" 1\n
scoreboard players set @a[scores={"""+tag+"""=1..}, nbt=!{Inventory:[{id:"minecraft:bundle",tag:{bundles:\""""+tag+"""\"}}]}] """+tag+""" 0\n
"""

print()
print("generating gif commands...")
fileList = []
for modifier in os.listdir("item_modifiers"):
	fileList.append([int(modifier[-9:-5]),modifier[:-5]])
fileList.sort()

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

