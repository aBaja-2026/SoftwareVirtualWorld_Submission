## Usage instructions

The CameraStream sample is a CarMaker integrated TCP client which consists of the two files `CameraStream.cpp` and
`CameraStream.h` and runs in a separate thread relative to the CarMaker main thread. It receives the Camera RSI images
via the TCP stream of the RSDA framework. The image processing is now part of the CarMaker simulation and generates
information which can be immediately used during the simulation to influence the behavior of the vehicle (e.g. for lane
keeping assistants or sensor data fusion). To use this application the user accessible code needs to be recompiled in
order to generate a new CarMaker executable. After copying `CameraStream.cpp` and `CameraStream.h` to the `src`
directory (`src_cm4sl` if Simulink is used) of the local CarMaker project, both the `Makefile` and `User.cpp` have to be
adapted.

### `Makefile:`

```
OBJS = ... CameraStream.o
```

### `User.cpp:`

```
#include "CameraStream.h"
...
int User_Init (void) {
...
CameraStream_Init();
...
}
int User_TestRun_Start_atEnd (void) {
...
CameraStream_Start();
...
}
void User_Cleanup (void) {
...
CameraStream_Exit();
...
}
```

### Optional configuration of SimParameters

To configure the TCP client, the following optional `SimParameters` can be specified.

| SimParameter           | Type   | Description                                                                               |
|------------------------|--------|-------------------------------------------------------------------------------------------|
| CameraStream.MovieHost | string | Optional. Specifies the host running IPGMovie or Movie&nbsp;NX. <br/> Default: localhost. |
| CameraStream.MoviePort | double | Optional. Specifies the TCP port. <br/> Default: 2210.                                    |
| CameraStream.Verbose   | double | Optional. Activates logging output. <br/> Default: 0.                                     |

### Additional UAQs

Starting the new compiled CarMaker executable gives access to three more UAQs.

| Name                  | Unit | Description                                           |
|-----------------------|------|-------------------------------------------------------|
| CameraStream.MinDepth | m    | Minimal depth value computed by implemented algorithm |
| CameraStream.nBytes   | -    | Number of received bytes                              |
| CameraStream.nImages  | -    | Number of received images                             |
