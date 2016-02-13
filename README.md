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

###URL

`[ipadress]/[image_mode]?[property=value]&[property=value]`

| Part          | Options                 | Use   |
| ------------- |:-----------------------:| -----:|
| [ipadress]    | localhost, ip or domain | adress of the scanner |
| [image_mode]  | line,full               | line returns only the current scanline so you have to set it up |
| [properties] | mode=(color, gray, lineart),preview=(0,1), resolution=(50,75,100,150,200)      | Properties directly in SANE can be set |

 e.g `http://localhost/full?mode=color&brightness=1&resolution=100&preview=0`

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
