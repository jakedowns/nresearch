import numpy as np
import matplotlib.pyplot as pyplot
import scipy
import sys

def plot_bool(axis, x, y, label):
    axis.plot(x, y, "tab:cyan", label=label)
    pyplot.sca(axis)
    pyplot.yticks([0, 1], ["False", "True"])
    axis.grid()
    axis.legend()


filename = sys.argv[1]
arr = np.loadtxt(filename, delimiter=",", skiprows=2, usecols=list(np.arange(0,28)))

arr = np.transpose(arr)

ts_nanosecond = arr[0]
seconds = (ts_nanosecond - ts_nanosecond[0]) / 1e9
timestamp = seconds


gyro1 = arr[1]
gyro2 = arr[2]
gyro3 = arr[3]
accel1_g = arr[4]
accel2_g = arr[5]
accel3_g = arr[6]
mag1_uT = arr[7]
mag2_uT = arr[8]
mag3_uT = arr[9]
euler1 = arr[10]
euler2 = arr[11]
euler3 = arr[12]
quat1 = arr[13]
quat2 = arr[14]
quat3 = arr[15]
quat4 = arr[16]
accel_err_deg = arr[17]
accel_ignored = arr[18]
accel_rej_timer = arr[19]
mag_err_deg = arr[20]
mag_ignored = arr[21]
mag_rej_timer = arr[22]
initialising = arr[23]
accel_rej_warn = arr[24]
accel_rej_timeout = arr[25]
mag_rej_warn = arr[26]
mag_rej_timeout = arr[27]


mag_included = False

# Plot Euler angles
if mag_included:
    figure, axes = pyplot.subplots(nrows=12, sharex=True, gridspec_kw={"height_ratios": [6, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1]})
else:
    figure, axes = pyplot.subplots(nrows=7, sharex=True, gridspec_kw={"height_ratios": [6, 1, 2, 1, 1, 1, 1]})

figure.suptitle("Euler angles, internal states, and flags")

axes[0].plot(timestamp, euler1, "tab:red", label="Roll")
axes[0].plot(timestamp, euler2, "tab:green", label="Pitch")
axes[0].plot(timestamp, euler3, "tab:blue", label="Yaw")
axes[0].set_ylabel("Degrees")
axes[0].grid()
axes[0].legend()

# Plot initialising flag
plot_bool(axes[1], timestamp, initialising, "Initialising")

# Plot acceleration rejection internal states and flags
axes[2].plot(timestamp, accel_err_deg, "tab:olive", label="Acceleration error")
axes[2].set_ylabel("Degrees")
axes[2].grid()
axes[2].legend()

plot_bool(axes[3], timestamp, accel_ignored, "Accelerometer ignored")

axes[4].plot(timestamp, accel_rej_timer, "tab:orange", label="Acceleration rejection timer")
axes[4].grid()
axes[4].legend()

plot_bool(axes[5], timestamp, accel_rej_warn, "Acceleration rejection warning")
plot_bool(axes[6], timestamp, accel_rej_timeout, "Acceleration rejection timeout")

if mag_included:

    # Plot magnetic rejection internal states and flags
    axes[7].plot(timestamp, mag_err_deg, "tab:olive", label="Magnetic error")
    axes[7].set_ylabel("Degrees")
    axes[7].grid()
    axes[7].legend()

    plot_bool(axes[8], timestamp, mag_ignored, "Magnetometer ignored")

    axes[9].plot(timestamp, mag_rej_timer, "tab:orange", label="Magnetic rejection timer")
    axes[9].grid()
    axes[9].legend()

    plot_bool(axes[10], timestamp, mag_rej_warn, "Magnetic rejection warning")
    plot_bool(axes[11], timestamp, mag_rej_timeout, "Magnetic rejection timeout")

    pyplot.figure()
    pyplot.plot(timestamp, mag1_uT, label="mag_a")
    pyplot.plot(timestamp, mag2_uT, label="mag_b")
    pyplot.plot(timestamp, mag3_uT, label="mag_c")
    pyplot.grid()
    pyplot.legend()

pyplot.show()