#!/bin/bash

NRT_SITE="http://nrt-status.gina.alaska.edu/products.txt?"
QUERY=""

usage() {
cat << EOF
usage: $0 options

This script mirrors data from the NRT Status available products

OPTIONS:
 -h   Show this message
 -s   Fetch data for SATELLITE
 -i   Fetch data for SENSOR
 -f   Fetch data for FACILITY
 -p   Fetch data for PROCESSING_LEVEL
 -n   Namespace the data (Place in sub-directorys for each pass)
 -o   Path to write data to (Default: .)
 -z   Create done files. 
EOF
}


while getopts "h:s:i:f:p:o:d:n:z" OPTION; do
case $OPTION in
  h)
    usage
    exit 1
    ;;
  s)
    QUERY="${QUERY}satellites\[\]=${OPTARG}&"
    # SATELLITES=$OPTARG
    ;;
  i)
    QUERY="${QUERY}sensors\[\]=${OPTARG}&"
    # SENSORS=$OPTARG
    ;;
  f)
    QUERY="${QUERY}facilities\[\]=${OPTARG}&"
    # FACILITY=$OPTARG
    ;;
  p)
    QUERY="${QUERY}processing_levels\[\]=${OPTARG}&"
    # PROCESSING_LEVELS=$OPTARG
    PLEVEL=${OPTARG}
    ;;
  d)
    DURATION=$OPTARG
    ;;
  o)
    OUTPUT_PATH=$OPTARG
    ;;
  n)
    NRT_NAMESPACE="yes"
    ;;
  z)
    DONE_FILE="yes"
    ;;
  ?)
    usage
    exit
    ;;
esac
done

OUTPUT_PATH="${OUTPUT_PATH:-.}"
DURATION="${DURATION:-1}"

case $(uname -s) in
  Linux)
  START_DATE=$(date +"%Y-%m-%d" -d "${DURATION} days ago")
  END_DATE=$(date +"%Y-%m-%d" -d "tomorrow")
  ;;
  Darwin)
  START_DATE=$(date -j -v-"${DURATION}"d +"%Y-%m-%d")
  END_DATE=$(date -j -v+1d +"%Y-%m-%d")
  ;;
  ?)
  echo "UNKNOWN Platform"
  exit 1
  ;;
esac

TMPFILE="/tmp/nrt-mirror-$(whoami)-$(date +%Y%m%d%H%M%S%N)-$RANDOM"

#Get the products list
curl -s "${NRT_SITE}start_date=${START_DATE}&end_date=${END_DATE}&${QUERY}" -o "$TMPFILE"

for file in $(cat "$TMPFILE"); do
  filename=$(basename "$file")
  passId=$(basename $(dirname "$file"))

  if [ "${filename}" == "leapsec.dat" ]; then
    continue
  fi
  #Get the file if it doesn't exist
  _OUTPUT_PATH=$OUTPUT_PATH
  if [ ! -z ${NRT_NAMESPACE+x} ]; then
    OUTPUT_PATH="${OUTPUT_PATH}/${passId}"
  fi

  wget -nc -q -P "$OUTPUT_PATH" "$file"

  OUTPUT_PATH=$_OUTPUT_PATH
done


 if [ -z ${DONE_FILE+x} ]; then
	 for file in $(cat "$TMPFILE"); do
                filename=$(basename "$file")
                passId=$(basename $(dirname "$file"))

                if [ "${filename}" == "leapsec.dat" ]; then
                        continue
                fi
                #Get the file if it doesn't exist
                _OUTPUT_PATH=$OUTPUT_PATH
                if [ ! -z ${NRT_NAMESPACE+x} ]; then
                        OUTPUT_PATH="${OUTPUT_PATH}/${passId}"
                fi

                if [ ! -e "$OUTPUT_PATH"/done_"$PLEVEL" ]; then
                        echo "Making done file $OUTPUT_PATH/done_$PLEVEL"
                        touch  "$OUTPUT_PATH/done_$PLEVEL"
                fi

                OUTPUT_PATH=$_OUTPUT_PATH
        done

 fi 


rm "$TMPFILE"
