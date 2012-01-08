AirPlayer
=======
This program lets you send YouTube videos and other files from you Mac to your Airplay Device. 

Install & Usage
===========
AirPlayer uses some third-party modules.

* [pyboujour](http://code.google.com/p/pybonjour/)
* [requests](https://github.com/kennethreitz/requests)

So you need to install them first if you want this to work.

Usage
--------
If you don't know how to install a module do this:

1. Open you terminal and `cd` into the folder you want to install.

2. `python setup.py install` _(You might need to run it as `sudo`)_
3. We're done!



To Play
----------
`cd` into your AirPlayer folder and run this command.

	# To play a video from YouTube
	# It will automatically pick the highest possible quality and send it to you AirPlay Device.
    python airplayer.py http://www.youtube.com/watch?v=8To-6VIJZRE
or

	# To play a local mp3 file (must be on your own server at the moment)
	python airplayer.py http://192.168.0.10/10%20Not%20Exactly.mp3
or

	# To play a video from blip.tv
	python airplayer.py http://blip.tv/wptuts/getting-loopy-ajax-powered-loops-with-jquery-and-wordpress-5805465

	# To play a hosted video
	python airplayer.py http://movies.apple.com/media/us/iphone/2011/ads/apple-iphone4s-siri-snow-today-us-20111030_r848-9cie.mov

Licence
----------
Do what ever you want. Public Domain or something. 
If you like it, drop me a line and tell so. It makes me all warm en fuzzy inside.