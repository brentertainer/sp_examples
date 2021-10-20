#!/bin/bash

mpiexec -n 4 python -m mpi4py farmer_ph.py\
    --default-rho 1.0\
    --max-iterations 50\
    --rel-gap 0.0\
    --abs-gap 0.0
