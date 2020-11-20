# McBundleImageConverter
Allows you to batch process images into Bundles! (Gif support too!)

In order to use this, you should get a folder together of the textures you want to use named with their item ID in the game.
Why? Well you can make this work with ANY resource pack!
So you can get a resource pack together for full colors and get this running. :P

How do you set this up?

Just go into datapacks/
drag the folder you created when running the script into your worlds datapack folder!

if you chose to only process images, you'll be able to run functions that just give you the bundles.

If you chose to process a gif, you will have to run /function bundles:start
This will give you a bundle, keep it in the first slot of your hotbar!

Next you need to set up a way to call /function bundles:run
This function is what updates the NBT data in your bundle to the next frame!
