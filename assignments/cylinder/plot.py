#!/usr/bin/env python3

import numpy as np
import matplotlib
matplotlib.use("Agg")   # Save figures without opening plot windows
import matplotlib.pyplot as plt

from pathlib import Path


# ============================================================
# User settings
# ============================================================

# Folder where OpenFOAM writes force coefficients
postprocessing_folder = Path("postProcessing")

# This matches folders like:
#   postProcessing/forces/0/forceCoeffs.dat
#   postProcessing/forces/200/forceCoeffs.dat
#   postProcessing/forces/400/forceCoeffs.dat
force_folder_pattern = "forces"

# File name
coefficient_file = "forceCoeffs.dat"

# Number of header rows to skip
skiprows = 9

# Start time after lift oscillation becomes stable
stable_start_time = 50.0

# Reference quantities for Strouhal number
# St = f * D / U_inf
D = 1.0
U_inf = 1.0

# ============================================================
# Column definition in your file
#
# File columns:
#   column 1 = Time
#   column 3 = Cd
#   column 4 = Cl
#
# Python indices:
#   0 = Time
#   2 = Cd
#   3 = Cl
# ============================================================

time_col = 0
cd_col = 2
cl_col = 3

# Output folder
out_dir = Path("postResults")
out_dir.mkdir(exist_ok=True)

# Maximum Strouhal number shown in the spectrum plot
St_plot_max = 1.0


# ============================================================
# Helper functions
# ============================================================

def time_average(y, t):
    """
    Time average using trapezoidal integration.
    Better than a simple arithmetic mean if dt is not perfectly constant.
    """
    if len(t) < 2:
        return float(np.mean(y))

    try:
        integral = np.trapezoid(y, t)
    except AttributeError:
        integral = np.trapz(y, t)

    return float(integral / (t[-1] - t[0]))


def folder_time(file_path):
    """
    Get numerical restart time folder.

    Example:
        postProcessing/forces/200/forceCoeffs.dat
        returns 200.0
    """
    try:
        return float(file_path.parent.name)
    except ValueError:
        return -1.0


def read_all_force_coefficients():
    """
    Read all forceCoeffs.dat files from all restart folders.

    Example:
        postProcessing/forces/0/forceCoeffs.dat
        postProcessing/forces/200/forceCoeffs.dat
        postProcessing/forces/400/forceCoeffs.dat

    Then combine, sort by time, and remove duplicate times.
    """

    files = list(
        postprocessing_folder.glob(
            f"{force_folder_pattern}/*/{coefficient_file}"
        )
    )

    if len(files) == 0:
        raise FileNotFoundError(
            f"No {coefficient_file} files found under "
            f"{postprocessing_folder}/{force_folder_pattern}/*/"
        )

    files = sorted(files, key=folder_time)

    all_rows = []
    source_index = []

    print("Reading force coefficient files:")

    for i, file in enumerate(files):
        print(f"  {file}")

        try:
            data_i = np.loadtxt(file, skiprows=skiprows)
        except ValueError:
            print(f"  Warning: skipped empty or incomplete file: {file}")
            continue

        if data_i.size == 0:
            print(f"  Warning: skipped empty file: {file}")
            continue

        if data_i.ndim == 1:
            data_i = data_i.reshape(1, -1)

        all_rows.append(data_i)
        source_index.append(np.full(data_i.shape[0], i))

    if len(all_rows) == 0:
        raise ValueError("No valid force coefficient data was loaded.")

    data = np.vstack(all_rows)
    source_index = np.concatenate(source_index)

    # Sort by physical time first, then by file order
    sort_index = np.lexsort((source_index, data[:, time_col]))
    data = data[sort_index]
    source_index = source_index[sort_index]

    # Remove duplicated time values, keeping the last occurrence.
    # This is useful when restarted simulations overlap in time.
    times = data[:, time_col]
    _, last_indices = np.unique(times[::-1], return_index=True)
    last_indices = len(times) - 1 - last_indices
    last_indices = np.sort(last_indices)

    data = data[last_indices]

    # Final sort by time
    data = data[np.argsort(data[:, time_col])]

    return data


def calculate_strouhal_spectrum_from_cl(t, cl, D, U_inf):
    """
    Calculate dominant frequency from Cl using FFT.

    Returns:
        dominant_frequency
        dominant_St
        St_axis
        amplitude
    """

    if len(t) < 10:
        return np.nan, np.nan, np.array([]), np.array([])

    # Sort by time
    order = np.argsort(t)
    t = t[order]
    cl = cl[order]

    # Remove duplicated time values
    t_unique, unique_indices = np.unique(t, return_index=True)
    t = t_unique
    cl = cl[unique_indices]

    if len(t) < 10:
        return np.nan, np.nan, np.array([]), np.array([])

    # Remove mean value
    cl_mean = time_average(cl, t)
    cl_fluc = cl - cl_mean

    # Uniform time step for FFT
    dt_values = np.diff(t)
    dt = np.median(dt_values)

    if dt <= 0:
        return np.nan, np.nan, np.array([]), np.array([])

    t_uniform = np.arange(t[0], t[-1], dt)

    if len(t_uniform) < 10:
        return np.nan, np.nan, np.array([]), np.array([])

    cl_uniform = np.interp(t_uniform, t, cl_fluc)

    # Apply window to reduce spectral leakage
    window = np.hanning(len(cl_uniform))
    signal = cl_uniform * window

    freq = np.fft.rfftfreq(len(signal), d=dt)
    amplitude = np.abs(np.fft.rfft(signal))

    # Ignore zero-frequency component
    if len(amplitude) > 0:
        amplitude[0] = 0.0

    # Convert frequency axis to Strouhal-number axis
    St_axis = freq * D / U_inf

    dominant_index = np.argmax(amplitude)
    dominant_frequency = freq[dominant_index]
    dominant_St = St_axis[dominant_index]

    return (
        float(dominant_frequency),
        float(dominant_St),
        St_axis,
        amplitude
    )


# ============================================================
# Read force coefficient data
# ============================================================

data = read_all_force_coefficients()

t = data[:, time_col]
Cd = data[:, cd_col]
Cl = data[:, cl_col]


# ============================================================
# Select stable region
# ============================================================

stable_mask = t >= stable_start_time

if np.sum(stable_mask) < 10:
    raise ValueError(
        "Not enough data after stable_start_time. "
        "Please reduce stable_start_time."
    )

t_stable = t[stable_mask]
Cd_stable = Cd[stable_mask]
Cl_stable = Cl[stable_mask]


# ============================================================
# Calculate statistics
# ============================================================

mean_Cd = time_average(Cd_stable, t_stable)
mean_Cl = time_average(Cl_stable, t_stable)

Cl_fluctuation = Cl_stable - mean_Cl
rms_Cl = np.sqrt(time_average(Cl_fluctuation**2, t_stable))

dominant_frequency, St, St_axis, St_amplitude = calculate_strouhal_spectrum_from_cl(
    t_stable,
    Cl_stable,
    D,
    U_inf
)


# ============================================================
# Save combined data
# ============================================================

combined_file = out_dir / "combined_force_coefficients.dat"

np.savetxt(
    combined_file,
    np.column_stack((t, Cd, Cl)),
    header="Time Cd Cl",
    comments=""
)


# ============================================================
# Save Strouhal spectrum data
# ============================================================

St_spectrum_file = out_dir / "St_spectrum_from_Cl.dat"

if len(St_axis) > 0 and len(St_amplitude) > 0:
    np.savetxt(
        St_spectrum_file,
        np.column_stack((St_axis, St_amplitude)),
        header="St FFT_amplitude_of_Cl",
        comments=""
    )


# ============================================================
# Plot Cd
# ============================================================

plt.figure(figsize=(8, 4.5))
plt.plot(t, Cd, linewidth=1.5)
plt.axvline(
    stable_start_time,
    linestyle="--",
    linewidth=1.2,
    label="Stable start"
)
plt.xlabel("Time")
plt.ylabel("Cd")
plt.title("Drag coefficient Cd")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(out_dir / "Cd_time_history.png", dpi=300)
plt.close()


# ============================================================
# Plot Cl
# ============================================================

plt.figure(figsize=(8, 4.5))
plt.plot(t, Cl, linewidth=1.5)
plt.axvline(
    stable_start_time,
    linestyle="--",
    linewidth=1.2,
    label="Stable start"
)
plt.xlabel("Time")
plt.ylabel("Cl")
plt.title("Lift coefficient Cl")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig(out_dir / "Cl_time_history.png", dpi=300)
plt.close()


# ============================================================
# Plot Strouhal spectrum based on Cl
# ============================================================

if len(St_axis) > 0 and len(St_amplitude) > 0:

    if np.max(St_amplitude) > 0:
        St_amplitude_plot = St_amplitude / np.max(St_amplitude)
        ylabel_text = "Normalized FFT amplitude of Cl"
    else:
        St_amplitude_plot = St_amplitude
        ylabel_text = "FFT amplitude of Cl"

    plt.figure(figsize=(8, 4.5))
    plt.plot(St_axis, St_amplitude_plot, linewidth=1.5)

    plt.axvline(
        St,
        linestyle="--",
        linewidth=1.2,
        label=f"Dominant St = {St:.4f}"
    )

    plt.xlabel("Strouhal number, St")
    plt.ylabel(ylabel_text)
    plt.title("Strouhal spectrum based on Cl")
    plt.grid(True)
    plt.legend()

    if np.max(St_axis) > 0:
        plt.xlim(0.0, min(St_plot_max, np.max(St_axis)))

    plt.tight_layout()
    plt.savefig(out_dir / "St_spectrum_from_Cl.png", dpi=300)
    plt.close()


# ============================================================
# Save summary
# ============================================================

summary_file = out_dir / "force_coefficient_summary.txt"

with open(summary_file, "w") as f:
    f.write("Force coefficient post-processing summary\n")
    f.write("=========================================\n\n")

    f.write("Input information\n")
    f.write("-----------------\n")
    f.write(f"Post-processing folder: {postprocessing_folder}\n")
    f.write(f"Force folder pattern:   {force_folder_pattern}\n")
    f.write(f"Coefficient file:       {coefficient_file}\n")
    f.write(f"Skipped header rows:    {skiprows}\n\n")

    f.write("Column definition in source file\n")
    f.write("-------------------------------\n")
    f.write("Time = column 1\n")
    f.write("Cd   = column 3\n")
    f.write("Cl   = column 4\n\n")

    f.write("Stable-region setting\n")
    f.write("---------------------\n")
    f.write(f"Stable start time:      {stable_start_time}\n")
    f.write(f"Stable time range:      {t_stable[0]} to {t_stable[-1]}\n")
    f.write(f"Number of data points:  {len(t_stable)}\n\n")

    f.write("Reference quantities\n")
    f.write("--------------------\n")
    f.write(f"D:                      {D}\n")
    f.write(f"U_inf:                  {U_inf}\n\n")

    f.write("Results based on stable region\n")
    f.write("------------------------------\n")
    f.write(f"Mean Cd:                {mean_Cd:.8f}\n")
    f.write(f"Mean Cl:                {mean_Cl:.8f}\n")
    f.write(f"RMS of fluctuating Cl:  {rms_Cl:.8f}\n")
    f.write(f"Dominant frequency f:   {dominant_frequency:.8f}\n")
    f.write(f"Strouhal number St:     {St:.8f}\n\n")

    f.write("Output files\n")
    f.write("------------\n")
    f.write(f"Combined data:          {combined_file}\n")
    f.write(f"Cd figure:              {out_dir / 'Cd_time_history.png'}\n")
    f.write(f"Cl figure:              {out_dir / 'Cl_time_history.png'}\n")

    if len(St_axis) > 0 and len(St_amplitude) > 0:
        f.write(f"St spectrum data:       {St_spectrum_file}\n")
        f.write(f"St spectrum figure:     {out_dir / 'St_spectrum_from_Cl.png'}\n")


# ============================================================
# Print results
# ============================================================

print()
print("Post-processing finished.")
print("--------------------------------")
print(f"Stable start time       = {stable_start_time}")
print(f"Stable time range       = {t_stable[0]} to {t_stable[-1]}")
print()
print(f"Mean Cd                 = {mean_Cd:.8f}")
print(f"Mean Cl                 = {mean_Cl:.8f}")
print(f"RMS of fluctuating Cl   = {rms_Cl:.8f}")
print(f"Dominant frequency f    = {dominant_frequency:.8f}")
print(f"Strouhal number St      = {St:.8f}")
print()
print(f"Saved combined data to: {combined_file}")
print(f"Saved Cd figure to:     {out_dir / 'Cd_time_history.png'}")
print(f"Saved Cl figure to:     {out_dir / 'Cl_time_history.png'}")

if len(St_axis) > 0 and len(St_amplitude) > 0:
    print(f"Saved St spectrum data: {St_spectrum_file}")
    print(f"Saved St spectrum to:   {out_dir / 'St_spectrum_from_Cl.png'}")

print(f"Saved summary to:       {summary_file}")
