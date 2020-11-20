from PIL import Image
import numpy as np



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

	bgColor = np.array([140,140,140])
	w, h = image.size
	average = np.array([0,0,0,0])

	for i in range(w):
		for j in range(h):
			average += np.array(getPixel([i,j],image)) 
			
	average = average // (w*h)
	add = np.array([*((bgColor * (1 - average[-1]/255)).astype(int)),0])
	average = (average*( average[-1]/255)).astype(int) + add
	
	return np.array([*average[:-1],255])
	
	
	
def getColor(c,palette):
	if(len(c) != 4): c.append(255)	
	return(palette[ min([ [np.sqrt(sum([v*v for v in (palette[i][0][:-1] - c[:-1])])), i] for i in range(len(palette)) ])[1] ])



def getClosestColor(c,palette):
	if(len(c) != 4): c.append(255)	
	return(palette[ min([ [np.sqrt(sum([v*v for v in (palette[i][0][:-1] - c[:-1])])), i] for i in range(len(palette)) ])[1] ][0])



def detectExtension(name):
    dPos = name.find('.')
    if(dPos>1): return name[dPos:]
    return ""
