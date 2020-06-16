# Introduction

**NeuroDecode** provides a real-time brain signal decoding framework. The decoding performance was recognised at [Microsoft Brain Signal Decoding competition](https://github.com/dbdq/microsoft_decoding) with the <i>First Prize Award</i> (2016) considering high decoding accuracy. It has been applied on a couple of online decoding projects based on EEG and ECoG and on various acquisition systems including AntNeuro eego, g.tec gUSBamp, BioSemi ActiveTwo, BrainProducts actiCHamp and Wearable Sensing. The decoding runs at approximately 15 classifications per second(cps) on a 4th-gen i7 laptop with 64-channel setup at 512 Hz sampling rate. High-speed decoding up to 200 cps was achieved using process-interleaving technique on 8 cores. It has been tested on both Linux and Windows using Python 3.8.

The underlying data communication is based on Lab Streaming Layer (LSL) which provides sub-millisecond time synchronization accuracy. Any signal acquisition system supported by native LSL or OpenVibe is also supported by NeuroDecode. Since the data communication is based on TCP, signals can be also transmitted wirelessly. For more information about LSL, please visit:
[https://github.com/sccn/labstreaminglayer](https://github.com/sccn/labstreaminglayer)

# Setup
## Prerequisites

Anaconda is recommended for easy installation of Python environment.

NeuroDecode depends on following packages:
  - scipy
  - numpy
  - PyQt5
  - scikit-learn
  - pylsl
  - mne 0.14 or later
  - matplotlib 2.1.0 or later
  - pyqtgraph
  - opencv-python
  - pyserial
  - future
  - configparser
  - xgboost
  - psutil

Optional but strongly recommended:
  - [OpenVibe](http://openvibe.inria.fr/downloads)

OpenVibe supports a wide range of acquisition servers and all acquisition systems supported by OpenVibe are supported by Neurodecode through LSL. Make sure you tick the checkbox "LSL_EnableLSLOutput" in Preferences when you run acquisition server. This will stream the data through the LSL network from which NeuroDecode receives data.

## Installation

Clone the repository:
```
git clone https://github.com/samuelsmal/NeuroDecode.git
```

**Note**: This project requires Python 3.8.

### Pip version / system version

Run setup script:
```
python setup.py develop
```

### Conda version

Run

```
conda env create --file environment.yml
```

## Configurations

Check the `env` file for all the global configurations that have to be set. Then check
also the configuration parameters required in the protocol-configs.

Notice that there are two different config files. The `structure_files` are for the GUI
and can be ignored, depending on how you run the software. The `template_files` are for
the protocols themselves and have to be adapted.

# Running

In general this system is a producer-consumer application. You need to start a
data-streamer (either through  driver and a EEG measurements, or by streaming old data
(see `cli.sh -s`)), followed by starting a consumer (e.g. `cli.sh -f` or `cli.sh -r`).

Given that the whole application is a multi-process application it's highly advised to
start these processes in a different shell, otherwise debugging is difficult.
A one-click setup does not work right now.

## Running steps

1. Start the plugin and connect the EEG device to the computer.
   On windows the port should be something along `com7` (check with the device manager).
   On Linux the port should be something along `/dev/ttyUSB0` (check with `dmesg`)
2. Check the signal by running `./cli.sh -v`
3. Start the recording / feedback (either `./cli.sh -r` or `./cli.sh -f`).

## Debugging and troubleshooting help

- If the protocols can't make a connection, reset the connection using the driver
- If connection problems persist, restart the device
- If the program crashes or if you have to abort it, make sure that you have no
    zombie-processes.
  On Linux run: `ps aux | grep neurodecode` to check for such processes and then execute 
  `pkill -f neurodecode` to kill them.

## Platform specific instructions
### Windows

**IMPORTANT:** Create environment variables:
> NEUROD_ROOT = NeuroDecode path

> NEUROD_DATA = path to the desired data folder (data will be saved there if using the GUI)

> NEUROD_SCRIPTS = path to the desired scripts folder (subject specific scripts will be saved there if using the GUI)


Add *%NEUROD_ROOT%/scripts* directory to PATH environment variable for convenient access to commonly used scripts.


**Launch GUI**, Go to *%NEUROD_ROOT%/scripts* directory and launch:
```
nd_gui.cmd
```

### Linux

Checkout out `cli.sh` and `env`. All environment variables (and some simple helper
variables) and the conda environment will be loaded if you execute `source env`. This has
to be run before using the CLI. In order to use all provided options you'll have to adapt
paths in certain files. For example in the config files (e.g. `neurodecode/config_files/Neurofeedback/template_files/config_online.py`)
and the protocols themselves (e.g. `neurodecode/protocols/NeuroFeedback/online_NeuroFeedback.py`).

# Important modules

### StreamReceiver
The base module for acquiring signals used by other modules such as Decoder, StreamViewer and StreamRecorder.

### StreamViewer
Visualize signals in real time with spectral filtering, common average filtering options and real-time FFT.

### StreamRecorder
Record signals into fif format, a standard format mainly used in [MNE EEG analysis library](http://martinos.org/mne/).

### StreamPlayer
Replay the recorded signals in real time as if it was transmitted from a real acquisition server.

### Decoder
This folder contains decoder and trainer modules. Currently, LDA, regularized LDA, Random Forests, and Gradient Boosting Machines are supported as the classifier type. Neural Network-based decoders are currently under experiment.

### Protocols
Contains some basic protocols for training and testing. Google Glass visual feedback is supported through USB communication.

### Triggers
Triggers are used to mark event (stimulus) timings during the recording. This folder contains common trigger event definition files.

### Utils
Contains various utilities.




## For Windows users, increase timer resolution
The default timer resolution in some Windows versions is 16 ms, which can limit the precision of timings. It is recommended to run the following tool and set the resolution to 1 ms or lower:
[https://vvvv.org/contribution/windows-system-timer-tool](https://vvvv.org/contribution/windows-system-timer-tool)


## Hardware triggering without legacy parallel port
We have also developed an Arduino-based triggering system as we wanted to send triggers to a parallel port using standard USB ports. We achieved sub-millisecond extra latency compared to physical parallel port (150 +- 25 us). Experimental results using oscilloscope can be found in "doc" folder. The package can be downloaded by:
```
git clone https://github.com/dbdq/arduino-trigger.git
```
The customized firmware should be installed on Arduino Micro and the circuit design included in the document folder should be printed to a circuit board.


## For g.USBamp users
The following customized acquisition server is needed instead of default LSL app to receive the trigger channel as part of signal streaming channels:
```
git clone https://github.com/dbdq/gUSBamp_pycnbi.git
```
because the default gUSBamp LSL server do not stream event channel as part of the signal stream but as a separate server. The customized version supports simultaneous signal+event channel streaming.


## For AntNeuro eego users
Use the OpenVibe acquisition server and make sure to check "LSL output" in preference.  If you don't see "eego" from the device selection, it's probably because you didn't install the additional drivers when you installed OpenVibe.


# To do
  - Tutorial
  - More cpu-efficient decoder class
  - Numba optimization

There are still plenty of possibilities to optimize the speed in many parts of the code. Any contribution is welcome. Please contact arnaud.desvachez@gmail.com or lee.kyuh@gmail.com for any comment / feedback.


# Copyright and license
The codes are released under [GNU General Public License](https://www.gnu.org/licenses/gpl-3.0.en.html).
