# constellation
LED baloons in the desert

## Codebase

Ground code is written in Python 2.7 (but there are some leftover pieces of me trying to experiment with 3, sorry about that).

## System architecture
Each balloon will have a wireless controlled node with an RGB LED. Each node will light up per values in a command packet set to the node network from the ground control station.

Each ground module will import ground_base.py. The GroundBase class will provide the tools necessary to write to the nodes, via the methods set_nodes() and set_nodes_frame(). set_nodes() takes a dictionary of tuples of (red, green, blue, alpha). All four values must be one (unsigned) byte each. Alpha is a "special" channel, and nodes will ignore color values set to them if it is 0. 255 will set the color. Other values in between 0 and 255 may be defined later.

### Modules:
* Sources
** Conway's game of life (TBD)
** Video player (TBD)
** Image viewer (image.py)
** Gif viewer (gif.py)
** Finger painting (TBD)
** Pong (TBD)
** Tetris (TBD)
** Music visualizer (TBD)
** Autopatcher (TBD)

### Packet formats
Control of the nodes is via a protocol called E1.31, or Streaming Architecture for Control Networks, or sACN. This is a standard protocol in the theatrical industry for contrlling lighting instruments over Ethernet and wifi. It also allows using free lighting console software to control the nodes (with nice GUIs and faders and built-in effects engines and canned effects).


### Running ground control software
Run any of the python scripts in ground/ (other than ground_base.py) and they should control the nodes.

### Off the shelf lighting consoles
* MagicQ: https://secure.chamsys.co.uk/magicq
** show stored in ground/constellation.shw
** Tries to emulate actual desk, difficult to use on screen
* Q Light Controller+: http://www.qlcplus.org/features.html
** show stored in ground/qlcp_constellation.qxw
** Easy to use, console of choice so far