# OpenFOAM Course Docker Environment

This repository provides a pre-built Docker environment for running OpenFOAM assignments.

Students do **not** need to install OpenFOAM manually.  
They only need to install Docker and use the provided course image.

---

## Docker Image

```bash
ghcr.io/jianxunz/openfoam-course-2026:openfoam13
```

This image contains:

```text
OpenFOAM Foundation v13
Python with numpy, matplotlib, scipy and PyVista
```

---

# 1. Install Docker

Recommended setup:

- **Windows:** Docker Desktop with WSL2 backend
- **macOS:** Docker Desktop
- **Linux:** Docker Engine or Docker Desktop

---

# 2. Pull the Course Image

```bash
docker pull ghcr.io/jianxunz/openfoam-course-2026:openfoam13
```

If Docker requires administrator permission:

```bash
sudo docker pull ghcr.io/jianxunz/openfoam-course-2026:openfoam13
```

---

# 3. Create a Working Folder

```bash
mkdir OpenFOAM_assignment
cd OpenFOAM_assignment
```

---

# 4. Enter the Docker Environment

## Linux / macOS / Git Bash

```bash
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && export PATH=/opt/pyenv/bin:$PATH && exec bash'
```

If Docker requires administrator permission:

```bash
sudo docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && export PATH=/opt/pyenv/bin:$PATH && exec bash'
```

## Windows PowerShell

```powershell
docker run --rm -it `
  --user 1000:1000 `
  -e HOME=/work `
  --mount "type=bind,src=${PWD},target=/work" `
  -w /work `
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 `
  bash -lc "source /opt/openfoam13/etc/bashrc && export PATH=/opt/pyenv/bin:`$PATH && exec bash"
```

---

# 5. Run the Cylinder Flow Simulation

# Run the Cylinder Flow Assignment

After entering the Docker container, copy the prepared cylinder case to your working directory:

```bash
cd /work
cp -r /course/assignments/cylinder .
cd cylinder
```

The cylinder case contains the following main scripts:

- `GenMesh.sh`: a shell script used to generate the mesh, check the mesh quality, convert the initial mesh/field data to VTK format, and run `plot_mesh.py` to create mesh-related plots.

- `runSimulations`: a shell script used to run the main CFD simulation workflow.

- `Allclean`: a shell script used to clean the case directory before rerunning the mesh generation or simulation.

- `plot_mesh.py`: a Python post-processing script used to visualize the generated mesh, including the full computational domain and the near-cylinder mesh resolution.

- `plot.py`: a Python post-processing script used to plot the drag and lift coefficients, calculate mean values, estimate the RMS lift coefficient, and compute the Strouhal number from the lift-coefficient signal.

- `plot_vorticity.py`: a Python post-processing script used to plot vorticity contours from the OpenFOAM results. This provides a simple alternative to using ParaView for visualizing the wake structure.

Make sure the scripts are executable:

```bash
chmod +x GenMesh.sh
chmod +x runSimulations
chmod +x Allclean
```

## Step 1: Generate and check the mesh

Run:

```bash
./GenMesh.sh
```

This script performs:

```bash
blockMesh
checkMesh
foamToVTK -time 0
python3 plot_mesh.py
```

After this step, the mesh is generated and the mesh plots are created.

## Step 2: Run the CFD simulation

Run:

```bash
./runSimulations
```

This starts the OpenFOAM simulation.

## Step 3: Post-process force coefficients

After the simulation is finished, run:

```bash
python3 plot.py
```

This generates plots of the drag and lift coefficients and calculates the main statistical quantities.

## Step 4: Plot vorticity contours

To visualize the wake without using ParaView, run:

```bash
python3 plot_vorticity.py
```

This script plots vorticity contours from the simulation results.

## Clean and rerun

To clean the case and start again:

```bash
./Allclean
./GenMesh.sh
./runSimulations
python3 plot.py
python3 plot_vorticity.py
```

The results are saved in:

```bash
/work/cylinder
```

Because `/work` is connected to your local folder, the same files will also appear on your own computer in:

```text
OpenFOAM_assignment/cylinder
```
```
---
---

# Common Problems

## Docker permission denied

Use `sudo`:

```bash
sudo docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && export PATH=/opt/pyenv/bin:$PATH && exec bash'
```

## Results disappear after exiting Docker

This happens if Docker is started without mounting a local folder.

Correct command:

```bash
docker run --rm -it \
  --user "$(id -u):$(id -g)" \
  -e HOME=/work \
  --mount type=bind,src="$(pwd)",target=/work \
  -w /work \
  ghcr.io/jianxunz/openfoam-course-2026:openfoam13 \
  bash -lc 'source /opt/openfoam13/etc/bashrc && export PATH=/opt/pyenv/bin:$PATH && exec bash'
```

## OpenFOAM refuses to run `#calc` or `#codeStream`

If you see:

```text
This code should not be executed by someone with administrator rights due to security reasons.
```

restart Docker using the non-root command shown above. The important option is:

```bash
--user "$(id -u):$(id -g)"
```
# Basic Linux Commands

Inside Docker, you only need a few basic Linux commands.

```bash
pwd
```

Show the current directory.

```bash
ls
```

List files and folders.

```bash
cd folderName
cd ..
```

Enter a folder, or go back to the parent folder.

```bash
cp -r sourceFolder targetFolder
```

Copy a folder. For example:

```bash
cp -r /course/assignments/cylinder .
```

Here, `.` means the current directory.

```bash
rm -rf folderName
```

Remove a folder and everything inside it. Be careful with this command.

```bash
chmod +x scriptName
```

Make a script executable.

```bash
./scriptName
```

Run a script, for example:

```bash
./Allrun
./Allclean
```

For this assignment, the most useful command sequence is:

```bash
cd /work
cp -r /course/assignments/cylinder .
cd cylinder
./Allrun
python3 plot.py
```

To clean and rerun:

```bash
./Allclean
./Allrun
python3 plot.py
```
