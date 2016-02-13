###Use

plug in scanner
```
sudo python server.py
```
sudo is needed in linux if you have not added the user to the scan group, seems fine without sudo on OSX

The program will run a server on port 80, to request an image send a URL it will send back live mpjeg stream of scan over HTTP

if another request is put in during scan it just sends back current image state

may find scanner does nothing if program terminates during the scan (this happens a lot with the Lide 100), simply disconnect and reconnect USB

use `scanimage -L` from `sane-utils` to test if SANE can see the image

###Dependencies

python modules
```
Pillow 3.1.0 (other versions of PIL probably work)
Pyinsane
```



other
```
SANE daemon
```
