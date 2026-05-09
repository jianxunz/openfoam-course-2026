#!/bin/bash

if ! command -v blockMesh >/dev/null 2>&1; then
    . /opt/openfoam13/etc/bashrc
fi

set -e

echo "======================================"
echo "Running OpenFOAM 13 pitzDailySteady test"
echo "======================================"

cd /work

if [ -d "pitzDailySteady_test" ]; then
    echo "Removing old pitzDailySteady_test folder..."
    rm -rf pitzDailySteady_test
fi

echo "Copying pitzDailySteady tutorial..."
cp -r "$FOAM_TUTORIALS/incompressibleFluid/pitzDailySteady" pitzDailySteady_test

cd pitzDailySteady_test

echo
echo "Running blockMesh..."
blockMesh

echo
echo "Running foamRun..."
foamRun

echo
echo "Simulation finished."
echo "Results are saved in:"
pwd
