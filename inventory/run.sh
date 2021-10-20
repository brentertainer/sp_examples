#!/bin/bash

mpiexec -n 3 python -m mpi4py inventory_ph.py\
    --default-rho 1.00\
    --max-iterations 50\
    --rel-gap 0.0\
    --abs-gap 0.0\
    --with-xhatshuffle\
    --no-xhatlooper\
    --with-lagrangian\
    --bundles-per-rank 3
