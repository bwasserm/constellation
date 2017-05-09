# constellation
LED baloons in the desert

## System architecture
Each balloon will have a wireless controlled node with an RGB LED. Each node will light up per values in a command packet set to the node network from the ground control station.

The ground control software will be multiple software modules passing "frame buffers" from one to another. Each module will transmit JSON packets to the next module in a chain, until the frames are converted into packets fit to send over the air to the nodes.

### Modules:
* Sources
** Conway's game of life
** Video player
** Image viewer
** Finger painting
** Pong
** Tetris
** Music visualizer
** Autopatcher
* Utils (may be merged together)
** Gamma correction
** Node control
** Frame rate control

### Packet formats
Frame buffer: JSON packet containing a 2D array of RGB pixel values (each int), and a source name field
Sky buffer: A list of uint8s, every 3 bytes is a pixel. Each node reads its values by indexing to 3*<node address>.
