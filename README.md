# OpenFOAM Course Docker Environment

This repository provides a pre-built Docker environment for running OpenFOAM assignments.

Students do **not** need to install OpenFOAM manually.  
They only need to install Docker and use the provided course image.

---

## Docker Image

The course image is:

```bash
ghcr.io/jianxunz/openfoam-course-2026:openfoam13
```

OpenFOAM version:

```text
OpenFOAM Foundation v13
```

This is the OpenFOAM version from:

```text
https://openfoam.org/version/13/
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

Students do **not** need to install Ubuntu or OpenFOAM directly.  
The Docker container provides an Ubuntu-based OpenFOAM environment internally.

---

# 2. Pull the Course Image

Run:

```bash
docker pull ghcr.io/jianxunz/openfoam-course-2026:openfoam13
```

On some Linux systems, Docker may require administrator permission:

```bash
sudo docker pull ghcr.io/jianxunz/openfoam-course-2026:openfoam13
```

---

# 3. Create a Working Folder

Create a folder where your OpenFOAM assignment files and results will be saved:

```bash
mkdir OpenFOAM_assignment
cd OpenFOAM_assignment
```

---

# 4. Start the OpenFOAM Environment

For this course, the Docker container should be started as a **non-root user**.

This is important because some OpenFOAM cases, such as `blockMeshDict` files using `#calc` or `#codeStream`, compile temporary dynamic code. OpenFOAM refuses to do this when running as root for security reasons.

## Linux / macOS / Git Bash

```bash
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && exec bash'
```

If Docker requires administrator permission:

```bash
sudo docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && exec bash'
```

## Windows PowerShell

```powershell
docker run --rm -it `
  --user 1000:1000 `
  -e HOME=/work `
  --mount "type=bind,src=${PWD},target=/work" `
  -w /work `
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 `
  bash -lc "source /opt/openfoam13/etc/bashrc && exec bash"
```

After running this command, you are inside a Linux Docker container where OpenFOAM Foundation v13 is already available.

You can check that you are not running as root:

```bash
id
```

You should **not** see:

```text
uid=0(root)
```

It is okay if you see something like:

```text
I have no name!
uid=1001 gid=1001 groups=1001
```

This only means the container does not know the username for your host user ID. It is harmless.

---

# 5. Check the OpenFOAM Environment

Inside the Docker container, run:

```bash
/course/scripts/check_openfoam.sh
```

Expected output should include:

```text
WM_PROJECT_VERSION=13
blockMesh
checkMesh
foamRun
```

You can also check manually:

```bash
echo $WM_PROJECT_VERSION
which blockMesh
which foamRun
```

Expected version:

```text
13
```

---

# 6. Run the Test Case

For OpenFOAM Foundation v13, the test case uses the `pitzDailySteady` tutorial.

Inside the Docker container, run:

```bash
/course/scripts/run_test_pitzDailySteady.sh
```

This script will:

1. Copy the OpenFOAM v13 `pitzDailySteady` tutorial.
2. Run `blockMesh`.
3. Run `foamRun`.
4. Save the results in:

```bash
/work/pitzDailySteady_test
```

Because `/work` is connected to your local folder, the results are also saved on your own computer.

---

# 7. Run a Cylinder Case

If your assignment contains a cylinder case, for example:

```text
OpenFOAM_assignment/cylinder
```

then inside the Docker container:

```bash
cd /work/cylinder
blockMesh
checkMesh
```

If the `blockMeshDict` uses `#calc` or `#codeStream`, make sure you started Docker with the non-root command shown above.

---

# 8. Exit the Docker Container

To leave the OpenFOAM environment, run:

```bash
exit
```

After exiting, check your local folder:

```bash
ls
```

You should see the generated case folders, for example:

```text
pitzDailySteady_test
```

or:

```text
cylinder
```

The files are saved on your local computer.

---

# Important Explanation

When you run:

```bash
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && exec bash'
```

your local folder is connected to the Docker container:

```text
Local computer folder    <-->    Docker container folder

OpenFOAM_assignment      <-->    /work
```

Therefore:

```text
Inside Docker: /work/pitzDailySteady_test
On your computer: OpenFOAM_assignment/pitzDailySteady_test
```

OpenFOAM is not installed directly on your computer.  
It is running inside Docker.

The `--rm` option removes the temporary container after you exit, but your simulation files remain in your local mounted folder.

---

# Useful OpenFOAM Commands

Inside the container, you can use standard OpenFOAM commands, for example:

```bash
blockMesh
checkMesh
foamRun
postProcess
foamToVTK
```

For OpenFOAM Foundation v13, many tutorials use:

```bash
blockMesh
foamRun
```

rather than older solver-specific commands such as `icoFoam` or `simpleFoam`.

---

# Visualization

The Docker image is mainly for running OpenFOAM simulations. ParaView is not installed inside the container.

If you run:

```bash
paraFoam
```

you may see:

```text
FATAL ERROR: A ParaView executable was not found on your system.
```

This is expected.

Recommended workflow:

1. Run OpenFOAM inside Docker.
2. Save results to the local mounted folder.
3. Open the results with ParaView installed on your own computer.

For example, after running a case:

```bash
exit
cd OpenFOAM_assignment/pitzDailySteady_test
touch pitzDailySteady_test.foam
```

Then open the `.foam` file in ParaView on your local computer.

Alternatively, inside Docker, you can convert the case to VTK:

```bash
cd /work/pitzDailySteady_test
foamToVTK
```

Then open the generated `VTK/` folder with ParaView on your local computer.

---

# macOS Notes

The container works on macOS through Docker Desktop.

For Apple Silicon Macs, such as M1, M2, M3, or M4, the following command may be needed if there is a platform compatibility issue:

```bash
docker run --platform linux/amd64 --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && exec bash'
```

This may be slower because it can use emulation, but it should be acceptable for small assignment cases.

---

# Common Problems

## Problem 1: `manifest unknown`

If you see:

```text
manifest unknown
```

check that the image tag is correct.

Wrong:

```bash
ghcr.io/jianxunz/openfoam-course-2026:1.
```

Correct:

```bash
ghcr.io/jianxunz/openfoam-course-2026:openfoam13
```

---

## Problem 2: Docker permission denied

If you see:

```text
permission denied while trying to connect to the docker API
```

use `sudo`:

```bash
sudo docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && exec bash'
```

Alternatively, on Linux, the user can be added to the Docker group:

```bash
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

After this, log out and log in again if needed.

---

## Problem 3: Results disappear after exiting Docker

This usually happens if Docker is started without mounting a local folder.

Wrong:

```bash
docker run --rm -it ghcr.io/jianxunz/openfoam-course-2026:openfoam13
```

Correct:

```bash
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && exec bash'
```

The `--mount` option is important because it saves `/work` to your local folder.

---

## Problem 4: OpenFOAM command not found

Inside the container, run:

```bash
/course/scripts/check_openfoam.sh
```

or manually source OpenFOAM:

```bash
source /opt/openfoam13/etc/bashrc
```

Then check:

```bash
echo $WM_PROJECT_VERSION
which blockMesh
```

---

## Problem 5: OpenFOAM refuses to run `#calc` or `#codeStream`

If you see:

```text
This code should not be executed by someone with administrator rights due to security reasons.
```

you are running inside Docker as root.

Exit the container:

```bash
exit
```

Then restart it with the non-root command:

```bash
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && exec bash'
```

If using `sudo`:

```bash
sudo docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && exec bash'
```

---

## Problem 6: `I have no name!`

Inside the container, you may see:

```text
I have no name!
```

This is harmless. It happens because Docker uses your host user ID inside the container, but the container does not have a username registered for that ID.

The important point is that you are not root. Check with:

```bash
id
```

If it does not show `uid=0(root)`, it is fine.

---

# Minimal Command Summary

```bash
docker pull ghcr.io/jianxunz/openfoam-course-2026:openfoam13

mkdir OpenFOAM_assignment
cd OpenFOAM_assignment

docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && exec bash'
```

Inside Docker:

```bash
/course/scripts/check_openfoam.sh
/course/scripts/run_test_pitzDailySteady.sh
```

For a cylinder case:

```bash
cd /work/cylinder
blockMesh
checkMesh
```

Exit:

```bash
exit
```

Check local results:

```bash
ls
```
