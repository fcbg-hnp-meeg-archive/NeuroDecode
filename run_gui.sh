#!/bin/bash

export NEUROD_SCRIPTS=/home/sam/proj/epfl/eeg-meditation/new_scripts
export NEUROD_ROOT=/home/sam/proj/epfl/eeg-meditation/NeuroDecode
export NEUROD_DATA=/home/sam/proj/epfl/eeg-meditation/data

python -m neurodecode.gui.mainWindow
