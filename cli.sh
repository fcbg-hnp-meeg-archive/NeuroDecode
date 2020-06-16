#!/bin/bash

if [ -z ${NEUROD_ROOT+x} ]; then
  # there we set the SAMPLE_RECORDING path as well
  echo "NEUROD_ROOT is not set, run '. ./env.sh' first"
  exit 1
fi

display_help() {
  echo "$(basename "$0") CLI for NeuroDecode"
  echo
  echo "-h | --help    # displays this message"
  echo "-s | --stream  # streams a pre-recorded FIF file"
  echo "-g | --gui     # starts the gui"
  echo "-v | --viewer  # online viewer of recording"
  echo "-r | --record  # records data, this is not synched by default"
  echo
}

# for more information check this
# - https://gist.github.com/magnetikonline/22c1eb412daa350eeceee76c97519da8
# - https://gist.github.com/cosimo/3760587

opts=$(getopt \
  -o sgvrhf \
  --long stream,gui,viewer,record,feedback,help \
  --name "${0##*/}" \
  -- "$@"
)

eval set -- "$opts"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h | --help )
      display_help
      exit
      ;;
    -s | --stream )
      echo "streaming..."
      python -m neurodecode.stream_player.stream_player "$SAMPLE_RECORDING"
      shift
      ;;
    -g | --gui )
      python -m neurodecode.gui.mainWindow
      shift
      ;;
    -v | --viewer )
      python -m neurodecode.stream_viewer.stream_viewer
      shift
      ;;
    -r | --record )
      echo "recording..."
      python -m neurodecode.stream_recorder.stream_recorder "$NEUROD_DATA"
      shift
      ;;
    -f | --feedback )
      echo "playing feedback..."
      python -m neurodecode.protocols.NeuroFeedback.online_NeuroFeedback
      shift
      ;;
    *)
      echo "No option provided. Check help"
      display_help
      exit 1;
      ;;
  esac
done
