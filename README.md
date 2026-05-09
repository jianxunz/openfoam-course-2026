# OpenFOAM Course Docker Environment

This repository provides a pre-built Docker environment for running OpenFOAM assignments.

Students do **not** need to install OpenFOAM manually.  
They only need to install Docker and use the provided course image.

## Docker Image

```bash
ghcr.io/jianxunz/openfoam-course-2026:1.0
```

OpenFOAM version:

```bash
OpenFOAM v2512
```

---

# 1. Install Docker

Before starting, install Docker.

Recommended setup:

- **Windows:** Docker Desktop with WSL2 backend
- **macOS:** Docker Desktop
- **Linux:** Docker Engine or Docker Desktop

After installation, check Docker with:

```bash
docker --version
```

---

# 2. Pull the Course Image

Run:

```bash
docker pull ghcr.io/jianxunz/openfoam-course-2026:1.0
```

If you are using Linux and Docker requires administrator permission, use:

```bash
sudo docker pull ghcr.io/jianxunz/openfoam-course-2026:1.0
```

---

# 3. Create a Working Folder

Create a folder where your OpenFOAM assignment results will be saved:

```bash
mkdir OpenFOAM_assignment
cd OpenFOAM_assignment
```

---

# 4. Start the OpenFOAM Environment

## Linux / macOS / Git Bash

```bash
docker run --rm -it \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:1.0
```

If Docker requires administrator permission:

```bash
sudo docker run --rm -it \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:1.0
```

## Windows PowerShell

```powershell
docker run --rm -it `
  --mount "type=bind,src=${PWD},target=/work" `
  -w /work `
  ghcr.io/jianxunz/openfoam-course-2026:1.0
```

After running this command, you are inside a Linux Docker container where OpenFOAM is already available.

---

# 5. Check the OpenFOAM Environment

Inside the Docker container, run:

```bash
/course/scripts/check_openfoam.sh
```

You should see output including:

```bash
WM_PROJECT_VERSION=2512
blockMesh
icoFoam
simpleFoam
```

You can also check manually:

```bash
echo $WM_PROJECT_VERSION
which blockMesh
which simpleFoam
```

---

# 6. Run the Test Cavity Case

Inside the Docker container, run:

```bash
/course/scripts/run_test_cavity.sh
```

This script will:

1. Copy the standard OpenFOAM cavity tutorial.
2. Run `blockMesh`.
3. Run `icoFoam`.
4. Save the results in:

```bash
/work/cavity_test
```

Because `/work` is connected to your local folder, the results are also saved on your own computer.

---

# 7. Exit the Docker Container

To leave the OpenFOAM environment, run:

```bash
exit
```

After exiting, check your local folder:

```bash
ls
```

You should see:

```bash
cavity_test
```

This folder contains the OpenFOAM case and simulation results.

---

# Important Explanation

When you run:

```bash
docker run --rm -it \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:1.0
```

your local folder is connected to the Docker container:

```text
Local computer folder    <-->    Docker container folder

OpenFOAM_assignment      <-->    /work
```

Therefore:

```text
Inside Docker: /work/cavity_test
On your computer: OpenFOAM_assignment/cavity_test
```

OpenFOAM is not installed directly on your computer.  
It is running inside Docker.

---

# Useful OpenFOAM Commands

Inside the container, you can use standard OpenFOAM commands, for example:

```bash
blockMesh
checkMesh
icoFoam
simpleFoam
postProcess
```

---

# Common Problems

## Problem 1: `manifest unknown`

If you see:

```bash
manifest unknown
```

check that the image tag is correct.

Wrong:

```bash
ghcr.io/jianxunz/openfoam-course-2026:1.
```

Correct:

```bash
ghcr.io/jianxunz/openfoam-course-2026:1.0
```

---

## Problem 2: Docker permission denied

If you see:

```bash
permission denied while trying to connect to the docker API
```

use `sudo`:

```bash
sudo docker run --rm -it \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:1.0
```

Alternatively, on Linux, the user can be added to the Docker group:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

---

## Problem 3: Results disappear after exiting Docker

This usually happens if Docker is started without mounting a local folder.

Wrong:

```bash
docker run --rm -it ghcr.io/jianxunz/openfoam-course-2026:1.0
```

Correct:

```bash
docker run --rm -it \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:1.0
```

The `--mount` option is important because it saves `/work` to your local folder.

---

# Minimal Command Summary

```bash
docker pull ghcr.io/jianxunz/openfoam-course-2026:1.0

mkdir OpenFOAM_assignment
cd OpenFOAM_assignment

docker run --rm -it \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:1.0
```

Inside Docker:

```bash
/course/scripts/check_openfoam.sh
/course/scripts/run_test_cavity.sh
```

Exit:

```bash
exit
```

Check local results:

```bash
ls
```

You should see:

```bash
cavity_test
```
