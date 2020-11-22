from imageProcessing import setPixel, getPixel, getAverageColor, getColor, getClosestColor, detectExtension
from multiprocessClass import NonDaemon, nPool
import multiprocessing.pool
from PIL import Image
from sys import exit
import numpy as np
import shutil 
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
		
		colors.append([getAverageColor(currentImage, image),image[:-4]])
		print(colors[-1],"\n")
		
paletteFile = open("paletteFile.txt","w") 
paletteFile.write("")
paletteFile.close()

paletteFile = open("paletteFile.txt","a") 
print("COLORS: ")
for e in colors:
	paletteFile.write(str(e)+"\n")
	print(e)
paletteFile.close()

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
	print("\nStarted processing ", filename[:-len(ex)]," ...")
	
	
	workImage = Image.open(("images/"+filename)) 
	width, height = workImage.size
	preview = Image.new('RGB', (width, height), color = 'red')


	if(dithering):
		print("Started dithering for "+filename)
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
		print("Finished dithering for "+filename)
	
	
	inData = []
	seg = width//6
	for n in range(6):
		inData.append( [n, [seg*(n),seg*(n+1)], workImage, height])
		if(seg*(n+1)<width and n == 5):
			inData.append( [n, [seg*(n+1),width], workImage, height])
	
	
	print("Started assembling function for "+ filename)
	if __name__ == '__main__':
		pool = nPool(processThreads)
		output = pool.map(generateCommandItems, inData)
		pool.close()
		pool.join()
		
		
	output.sort()
	
	if(isGif):
		command = '{"function":"set_nbt","tag":"{\\"Items\\":['
		items = ""
		for e in output: items += e[1]

		command+= items+'],gbundle:\\"start\\"}"}'

		file1 = open("item_modifiers/"+(''.join([char for char in filename[:-len(ex)] if char != '\\'])).lower()+".json","w") 
		file1.write(command)
		file1.close()
		
	else:
		items = ""
		for e in output: items += e[1]
		command = "give @p bundle{Items:["+(''.join([char for char in items[:-1] if char != '\\']))+"]}"
		file1 = open("functions/"+(''.join([char for char in filename[:-len(ex)] if char != '\\'])).lower()+".mcfunction","w") 
		file1.write(command)
		file1.close()
		
	print(filename+" command has been generated and saved! Size: "+str(len(command)))
	return 1

notOkayWithThreads = True
while(notOkayWithThreads):
	processThreads = int(input("\nHow many processes would you like to use for processing the commands?\n(each image will open this many processes)\n[default: 3 ]:") or 3)
	imageThreads = int(input("\nHow many images would you like to process at the same time?\n(will open this many processes times the amount per image!!!)\n[default: 2]:") or 2)
	notOkayWithThreads = (input("\n!!!This program is set to use "+str(processThreads*imageThreads)+" threads of your CPU, are you sure?!!!\n[y/N]:").lower() or "n")=="n"


datapackName = input("\nPlease enter a name for the data pack\n[untitled_pack]:") or "untitled_pack"
everything = ((input("\nDo you wish to process every image in images/?\n(!!LARGE FILES MAY TAKE A WHILE!!)\n[Y/n]:") or "y").lower()=="y")
dithering = ((input("\nDo you want dithering?\n(This is best for images with a wide range of colors)\n[y/N]:") or "n").lower()=="y")
isGif = ((input("\nDo you wish to process a gif?\n(!!LARGE FILES MAY TAKE A WHILE!!)\n[y/N]:") or "n").lower()=="y")


files = []
if(isGif): 
	directory = 'item_modifiers'
	for f in os.listdir(directory):
		os.remove(os.path.join(directory, f))
		
	everything = False
	gName = input("\nType the file name of the image (including extension) that you wish to process\n[imageName]: ")
	im = Image.open("gifs/"+gName)
	
	ext = detectExtension(gName)
	gName = gName[:-1*len(ext)]
	
	print("\nStarted splitting GIF...\n")
	
	for frame in range(0,im.n_frames):
		im.seek(frame)
		name = gName+"_"+str(frame)+".png"
		im.save("images/"+name)
		files.append(name)
		
	print("\nGIF is split...\n")
	
else:
	directory = 'functions'
	for f in os.listdir(directory):
		os.remove(os.path.join(directory, f))
		
		
if(everything==True and isGif==False):

	files = []
	for fileN in os.listdir("images"):
	
		if(detectExtension(fileN)!=".gif" and
		   detectExtension(fileN)!=".blank"):
		   
			files.append(fileN)
	
	
if(everything==False and isGif==False): 
	files = [input("\nType the file name of the image (including extension) that you wish to process\n[imageName]: ")]


if __name__ == '__main__':
	print("\nFiles that will be processed:\n",files)
	print("\n\nStarting to MultiProcess images...\n")
	if(len(files)==1):
		processFile(files[0])
	else:
		p = nPool(imageThreads)
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
	
	print("\nClearing images if gif frames, and clearing out gif frames from functions")
	
	
	directory = 'images'
	for f in os.listdir(directory):
		if f in files:
			os.remove(os.path.join(directory, f))
		else: continue
	
	
	directory = 'functions'
	for f in os.listdir(directory):
		os.remove(os.path.join(directory, f))


	print("\ngenerating gif commands...")
	

	tag = ''.join([char for char in (datapackName.lower()+"score") if char !='\\'])
	start = 'scoreboard objectives add '+tag+' dummy\nscoreboard players set @a '+tag+' 1\ngive @a minecraft:bundle{gbundle:"run"}'
	run = """scoreboard players add @a[ scores={"""+tag+"""=1..} ] """+tag+""" 1
scoreboard players set @a[ scores={"""+tag+"""=..1}, nbt={Inventory: [ {Slot: 0b, id: "minecraft:bundle", Count: 1b, tag: {gbundle: "run"}} ]} ] """+tag+""" 1
scoreboard players set @a[ scores={"""+tag+"""=1..}, nbt=!{Inventory: [ {Slot: 0b, id: "minecraft:bundle", Count: 1b, tag: {gbundle: "run"}} ]} ] """+tag+""" 0\n"""


	fileList = []
	for modifier in os.listdir("item_modifiers"):
		fileList.append([getLastNumber(modifier),modifier[:-5]])
	fileList.sort()

	print(fileList)

	for e in fileList:
		run+="""item entity @a[ scores={"""+tag+"""="""+str(int(e[0])+2).lower()+"""}, nbt={Inventory: [ {Slot: 0b, id: "minecraft:bundle", Count: 1b, tag: {gbundle: "run"}} ]} ] hotbar.0 modify """+datapackName.lower()+""":"""+e[1].lower()+"""\n"""
	run+="""scoreboard players set @a[ scores={"""+tag+"""="""+str(int(fileList[-1][0])+3).lower()+"""..} ] """+tag+""" 1"""


#nbt={Inventory: [ {Slot: 0b, id: "minecraft:bundle", Count: 1b, tag: {gbundle: "start"}} ]}
	startS = open("functions/start.mcfunction","w") 
	startS.write(start)
	startS.close()


	runS = open("functions/run.mcfunction","w") 
	runS.write(run)
	runS.close()
	print("gif commands finished writing!")


print()	
print("Assembling datapack...")


dirs = [
		"datapacks/"+datapackName,
		"datapacks/"+datapackName+"/data",
		"datapacks/"+datapackName+"/data/"+datapackName.lower()
	   ]

for d in dirs:
	try: os.mkdir(d)  
	except: continue


delDirs = [
			"datapacks/"+datapackName+"/data/"+datapackName.lower()+"/functions",
			"datapacks/"+datapackName+"/data/"+datapackName.lower()+"/item_modifiers"
		  ]
		  
for d in delDirs:
	if(os.path.isdir(d)):
		for f in os.listdir(d):
			try: os.remove(os.path.join(d, f))
			except: break
		os.rmdir(d)


metafile = open("datapacks/"+datapackName+"/pack.mcmeta","w") 
mcmeta = '{\n"pack": {\n"pack_format": 7,\n"description": "'+datapackName.lower()+' Bundle Pack"}}'
metafile.write(mcmeta)
metafile.close()


fSrc = "functions/"
fCopy = "datapacks/"+datapackName+"/data/"+datapackName.lower()+"/functions/"
copy = shutil.copytree(fSrc,fCopy)
print(copy)


if(isGif):
	imSrc = "item_modifiers/"
	imCopy = "datapacks/"+datapackName+"/data/"+datapackName.lower()+"/item_modifiers/"
	copy = shutil.copytree(imSrc,imCopy)
	print(copy)
	
	
delDirs = [ "functions", "item_modifiers" ]


for d in delDirs:
	for f in os.listdir(d):
		try: os.remove(os.path.join(d, f))
		except: break
		
		
print("\nYour data pack has been created at: \ndatapacks/"+datapackName+"\n\n")

