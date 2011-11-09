AirPlayer
=======
This program lets you send YouTube videos from you Mac to your Airplay Device, it will soon be able to send other media as well. 

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
`cd` into your AirPlayer folder like this: `cd ~/AirPlayer` and run this command.

    python airplayer.py http://www.youtube.com/watch?v=8To-6VIJZRE

It will automatically pick the highest possible quality and send it to you AirPlay Device.

Licence
----------
Do what ever you want. Public Domain or something. 
If you like it, drop me a line and tell so. It makes me all warm en fuzzy inside.