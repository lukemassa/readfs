#!/bin/bash



if [[ ! -f libexec/run.py ]]
then
    echo "Must be run from top of readfs"
    exit 1
fi

export PYTHONPATH=$PYTHONPATH:$(pwd)/lib
exec python -m unittest discover ci -v
