#!/bin/bash

set -e

echo "======================================"
echo "Running OpenFOAM cavity tutorial test"
echo "======================================"

cd /work

if [ -d "cavity_test" ]; then
    echo "Removing old cavity_test folder..."
    rm -rf cavity_test
fi

echo "Copying cavity tutorial..."
cp -r "$FOAM_TUTORIALS/incompressible/icoFoam/cavity/cavity" cavity_test

cd cavity_test

echo
echo "Running blockMesh..."
blockMesh

echo
echo "Running icoFoam..."
icoFoam

echo
echo "Simulation finished."
echo "Results are saved in:"
pwd
