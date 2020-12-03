# McBundleImageConverter

# How to get it working?
In order to run this you must have Python 3.7.x installed on your system
You need to have installed "PIL" (Pillow) and "numpy" to python.
You can do this;

https://numpy.org/install/
https://pypi.org/project/Pillow/


# Allows you to batch process images into Bundles! (Gif support too!)

I recommend scaling gifs down to 64x64 or below, and keep frame count low.
Otherwise you're gonna run out of memory loading minecraft lol.

I recommend scalign images down to 128x128 or below, otherwise you'll find it almost impossible to view the whole image.
You can use GPU software to make windows show at a higher resolution, by using superresolution, which can allow MC to scale down its gui even smaller.
Or you can just drag your window size just large enough such that the bundle in your inventory is at the bottom left of your bototm-left-most monitor.
Make sure you're on GUI scale of 1 :P

In order to use this, you should get a folder together of the textures you want to use named with their item ID in the game.
Why? Well you can make this work with ANY resource pack!
So you can get a resource pack together for full colors and get this running. :P

## How do you set this up?

Just go into datapacks/
drag the folder you created when running the script into your worlds datapack folder!

if you chose to only process images, you'll be able to run functions that just give you the bundles.

If you chose to process a gif, you will have to run /function bundles:start
This will give you a bundle, keep it in the first slot of your hotbar!

Next you need to set up a way to call /function bundles:run
This function is what updates the NBT data in your bundle to the next frame!
