#!/bin/bash

# dumb script to get around ipython/docker see: https://github.com/ipython/ipython/issues/7062

ipython notebook --no-browser --ip=* --port 8888
