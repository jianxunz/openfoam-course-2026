#!/bin/bash

echo "======================================"
echo "Checking OpenFOAM environment"
echo "======================================"

echo
echo "OpenFOAM project:"
echo "WM_PROJECT        = ${WM_PROJECT:-Not set}"
echo "WM_PROJECT_VERSION= ${WM_PROJECT_VERSION:-Not set}"
echo "WM_PROJECT_DIR    = ${WM_PROJECT_DIR:-Not set}"

echo
echo "Important OpenFOAM commands:"

for cmd in blockMesh icoFoam simpleFoam paraFoam; do
    if command -v "$cmd" >/dev/null 2>&1; then
        echo "$cmd: $(command -v "$cmd")"
    else
        echo "$cmd: NOT FOUND"
    fi
done

echo
echo "FOAM_TUTORIALS:"
echo "${FOAM_TUTORIALS:-Not set}"

echo
echo "Check completed."
