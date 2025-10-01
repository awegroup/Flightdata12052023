#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 26 11 15:00:00 2024

Simple visualization toolchain for experimental data.

@author: Oriol Cayon
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider
import matplotlib.gridspec as gridspec
import os
import zipfile


def plot_kite_data_with_sliders(flight_data, variables, labels, subplot_labels):
    """
    Plot kite flight data with interactive sliders for cycle selection and 3D view control.

    Parameters:
        flight_data (pd.DataFrame): The dataset containing kite flight data.
        selected_vars (list of str): The variables to plot in time-series format.
    """
    # Extract unique cycles
    unique_cycles = flight_data["cycle"].unique()

    # Initial cycle
    current_cycle = unique_cycles[0]

    # Filter data for the initial cycle
    mask = flight_data["cycle"] == current_cycle

    # Extract time and position data
    t = flight_data[mask]["time"].values
    x = flight_data[mask]["kite_pos_east"].values
    y = flight_data[mask]["kite_pos_north"].values
    z = flight_data[mask]["kite_height"].values

    # Setup figure and layout
    n = len(variables)
    fig = plt.figure(figsize=(14, 8))
    gs = gridspec.GridSpec(
        n, 2, width_ratios=[1, 1], height_ratios=[0.5 for _ in range(n)]
    )

    # 3D plot of the trajectory
    ax_3d = fig.add_subplot(gs[0:3, 0], projection="3d")
    (trajectory_line,) = ax_3d.plot(x, y, z, label="Trajectory")
    ax_3d.set_xlabel("X")
    ax_3d.set_ylabel("Y")
    ax_3d.set_zlabel("Z")
    ax_3d.set_title("Kite Trajectory")
    ax_3d.legend()

    # Time series plots for each selected variable
    ax_vars = []
    for i, variable in enumerate(variables):
        ax = fig.add_subplot(gs[i, 1:])
        ax_subvars = []
        for j, var in enumerate(variable):
            (line,) = ax.plot(t, var[mask], label=labels[i][j])
            ax_subvars.append((line))

        ax.set_ylabel(subplot_labels[i])
        if i == len(variables) - 1:
            ax.set_xlabel("Time")
        ax.legend()
        ax.grid(True)
        ax_vars.append(ax_subvars)

    # Cycle slider
    slider_ax_cycle = fig.add_axes(
        [0.1, 0.05, 0.3, 0.03], facecolor="lightgoldenrodyellow"
    )
    cycle_slider = Slider(
        slider_ax_cycle, "Cycle", 0, len(unique_cycles) - 1, valinit=0, valstep=1
    )

    # Slider for elevation angle
    slider_ax_elev = fig.add_axes(
        [0.1, 0.1, 0.3, 0.03], facecolor="lightgoldenrodyellow"
    )
    elev_slider = Slider(
        slider_ax_elev, "Elevation", 0, 90, valinit=30, orientation="horizontal"
    )

    # Slider for azimuth angle
    slider_ax_azim = fig.add_axes(
        [0.1, 0.15, 0.3, 0.03], facecolor="lightgoldenrodyellow"
    )
    azim_slider = Slider(
        slider_ax_azim, "Azimuth", 0, 360, valinit=30, orientation="horizontal"
    )

    # Update function for cycle slider
    def update_cycle(val):
        nonlocal flight_data, t, x, y, z, variables
        cycle_idx = int(cycle_slider.val)
        selected_cycle = unique_cycles[cycle_idx]
        mask = flight_data["cycle"] == selected_cycle

        # Update trajectory data
        t = flight_data[mask]["time"].values
        x = flight_data[mask]["kite_pos_east"].values
        y = flight_data[mask]["kite_pos_north"].values
        z = flight_data[mask]["kite_height"].values
        trajectory_line.set_data(x, y)
        trajectory_line.set_3d_properties(z)

        # Update variables
        for (line), variable in zip(ax_vars, variables):
            for j, var in enumerate(variable):
                line[j].set_data(t, var[mask])
            line[j].axes.set_xlim(t.min(), t.max())

        # Redraw the figure
        fig.canvas.draw_idle()

    # Update function for 3D view sliders
    def update_view(val):
        ax_3d.view_init(elev=elev_slider.val, azim=azim_slider.val)
        fig.canvas.draw_idle()

    # Connect sliders to update functions
    cycle_slider.on_changed(update_cycle)
    elev_slider.on_changed(update_view)
    azim_slider.on_changed(update_view)

    plt.show()


def ensure_csv_file(filename):
    """
    Ensure the CSV file is available by checking its existence
    and unzipping it if necessary.

    Parameters:
        csv_filename (str): The name of the CSV file to check.
        zip_filename (str): The name of the ZIP file containing the CSV.
    """
    csv_filename = filename + ".csv"
    zip_filename = filename + ".zip"
    # Check if the CSV file exists
    if not os.path.exists(csv_filename):
        print(f"{csv_filename} not found. Checking for {zip_filename}...")

        # Check if the ZIP file exists
        if os.path.exists(zip_filename):
            print(f"{zip_filename} found. Extracting...")
            with zipfile.ZipFile(zip_filename, "r") as zip_ref:
                zip_ref.extractall(".")  # Extract to the current directory
            print(f"Extracted {csv_filename}.")
        else:
            raise FileNotFoundError(
                f"Neither {csv_filename} nor {zip_filename} exists in the directory."
            )
    else:
        print(f"{csv_filename} is already present.")


# Ensure the CSV file is available
ensure_csv_file("log_2023-05-12_14-22-44")
# Load flight data
df = pd.read_csv("log_2023-05-12_14-22-44.csv")

flight_data = df[df["kite_height"] > 20]

from datetime import datetime

# Convert timestamp to datetime object of initial and final time
datetime_ini = datetime.utcfromtimestamp(flight_data["time"].iloc[0])
datetime_end = datetime.utcfromtimestamp(flight_data["time"].iloc[-1])

print(f"Initial time: {datetime_ini}")
print(f"Final time: {datetime_end}")

# Select variables to plot
tether_force = flight_data["ground_tether_force"]
kite_speed_0 = np.sqrt(
    flight_data["kite_0_vx"] ** 2
    + flight_data["kite_0_vy"] ** 2
    + flight_data["kite_0_vz"] ** 2
)
kite_speed_1 = np.sqrt(
    flight_data["kite_1_vx"] ** 2
    + flight_data["kite_1_vy"] ** 2
    + flight_data["kite_1_vz"] ** 2
)


# Select only 4 lidar speed variables, max, min and 2 in between

reelout_speed = flight_data["ground_tether_reelout_speed"]
power = flight_data["ground_mech_power"]
heading = flight_data["kite_heading"] * 180 / np.pi
course = flight_data["kite_course"] * 180 / np.pi
va = flight_data["airspeed_apparent_windspeed"]

variables = [
    [tether_force],
    [kite_speed_0, kite_speed_1, va],
    [reelout_speed],
    [heading, course],
]
labels = [
    [None],
    ["Sensor 0", "Sensor 1", "Pitot tube"],
    [None],
    ["Heading", "Course"],
]

subplot_labels = [
    "Tether Force (kg)",
    "Kite Speed (m/s)",
    "Reelout Speed (m/s)",
    "Kite Orientation",
]
# Call the function
plot_kite_data_with_sliders(flight_data, variables, labels, subplot_labels)
