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
Python with numpy, matplotlib, and scipy
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

# Run the Cylinder Flow Simulation

After entering the Docker container, copy the prepared cylinder case to your working directory:

```bash
cd /work
cp -r /course/assignments/cylinder .
cd cylinder
```

The cylinder case contains the following main files:

- `Allrun`: a shell script used to run the main workflow automatically, including mesh generation, mesh checking, and solver execution.

- `Allclean`: a shell script used to clean the case directory before rerunning the simulation.

- `plot.py`: a Python post-processing script used to plot the drag and lift coefficients, calculate mean values, estimate the RMS lift coefficient, and compute the Strouhal number from the lift-coefficient signal.

To run the simulation, use:

```bash
./Allrun
```

After the simulation is finished, run the post-processing script:

```bash
python3 plot.py
```

To clean the case and run it again:

```bash
./Allclean
./Allrun
python3 plot.py
```

The results are saved in:

```bash
/work/cylinder
```

Because `/work` is connected to your local folder, the same files will also appear on your own computer in:

```text
OpenFOAM_assignment/cylinder
```
---

# 6. Exit the Docker Container

```bash
exit
```

After exiting, the `cylinder` folder remains on your local computer.

---

# Visualization

ParaView is not installed inside the Docker image.

Recommended workflow:

1. Run OpenFOAM inside Docker.
2. Save results to the local mounted folder.
3. Open the results with ParaView installed on your own computer.

After exiting Docker:

```bash
cd OpenFOAM_assignment/cylinder
touch cylinder.foam
```

Then open `cylinder.foam` in ParaView.

Alternatively, inside Docker you can export VTK files:

```bash
cd /work/cylinder
foamToVTK
```

Then open the generated `VTK/` folder in ParaView.

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
