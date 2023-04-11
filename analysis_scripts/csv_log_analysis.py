import numpy as np
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as pyplot
import scipy
import sys

def plot_bool(axis, x, y, label):
    axis.plot(x, y, "tab:cyan", label=label)
    pyplot.sca(axis)
    pyplot.yticks([0, 1], ["False", "True"])
    axis.grid()
    axis.legend()

def euler_diff(rotation_old, rotation_new):
    quat_diff = rotation_new * rotation_old.inv()

    euler_diff = quat_diff.as_euler('xyz',degrees=True)

    return euler_diff


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
quat_w = arr[13]
quat_x = arr[14]
quat_y = arr[15]
quat_z = arr[16]
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

# re-run Fusion with different parameters

sample_rate = 1000  # Hz

gyroscope = np.transpose(np.vstack((gyro1,gyro2, gyro3)))
accelerometer = np.transpose(np.vstack((accel1_g,accel2_g,accel3_g)))
magnetometer = np.transpose(np.vstack((mag1_uT,mag2_uT,mag3_uT)))


diff_length = len(quat_w)

euler_x_diff = np.zeros((diff_length,1))
euler_y_diff = np.zeros((diff_length,1))
euler_z_diff = np.zeros((diff_length,1))

for i in range(1,len(quat_w)):
    rotation_old = R.from_quat([quat_x[i-1], quat_y[i-1], quat_z[i-1], quat_w[i-1]])
    rotation_new = R.from_quat([quat_x[i], quat_y[i], quat_z[i], quat_w[i]])

    euler_diff_arr = euler_diff(rotation_old, rotation_new)

    time_difference = timestamp[i] - timestamp[i-1]

    euler_x_diff[i] = euler_diff_arr[0] / time_difference
    euler_y_diff[i] = euler_diff_arr[1] / time_difference
    euler_z_diff[i] = euler_diff_arr[2] / time_difference


mag_included = False

# Plot Euler angles
if mag_included:
    figure, axes = pyplot.subplots(nrows=12, sharex=True, gridspec_kw={"height_ratios": [6, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1]})
else:
    figure, axes = pyplot.subplots(nrows=7, sharex=True, gridspec_kw={"height_ratios": [6, 1, 2, 1, 1, 1, 1]})

figure.suptitle("Euler angles, internal states, and flags\n" + filename)

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

figure, axes = pyplot.subplots(nrows=3, sharex=True)

figure.suptitle("Gyro, accel, mag data")

axes[0].plot(timestamp, gyroscope[:, 0], "tab:red", label="Roll")
axes[0].plot(timestamp, gyroscope[:, 1], "tab:green", label="Pitch")
axes[0].plot(timestamp, gyroscope[:, 2], "tab:blue", label="Yaw")
axes[0].set_ylabel("dps")
axes[0].grid()
axes[0].legend()

axes[1].plot(timestamp, accelerometer[:, 0], "tab:red", label="x")
axes[1].plot(timestamp, accelerometer[:, 1], "tab:green", label="y")
axes[1].plot(timestamp, accelerometer[:, 2], "tab:blue", label="z")
axes[1].set_ylabel("G")
axes[1].grid()
axes[1].legend()

axes[2].plot(timestamp, magnetometer[:, 0], "tab:red", label="x")
axes[2].plot(timestamp, magnetometer[:, 1], "tab:green", label="y")
axes[2].plot(timestamp, magnetometer[:, 2], "tab:blue", label="z")
axes[2].set_ylabel("uT")
axes[2].grid()
axes[2].legend()


# pyplot.figure()
# pyplot.plot(timestamp, euler_x_diff, "tab:red", label="Roll")
# pyplot.plot(timestamp, euler_y_diff, "tab:green", label="Pitch")
# pyplot.plot(timestamp, euler_z_diff, "tab:blue", label="Yaw")
# pyplot.ylabel("Degrees")
# pyplot.xlabel("Time Elapsed (s)")

pyplot.show()