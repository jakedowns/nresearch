import numpy as np
import matplotlib.pyplot as pyplot
import scipy
import sys
import imufusion

def plot_bool(axis, x, y, label):
    axis.plot(x, y, "tab:cyan", label=label)
    pyplot.sca(axis)
    pyplot.yticks([0, 1], ["False", "True"])
    axis.grid()
    axis.legend()

# read in data from log

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


# re-run Fusion with different parameters

sample_rate = 1000  # Hz

gyroscope = np.transpose(np.vstack((gyro1,gyro2, gyro3)))
accelerometer = np.transpose(np.vstack((accel1_g,accel2_g,accel3_g)))
magnetometer = np.transpose(np.vstack((mag1_uT,mag2_uT,mag3_uT)))


# Instantiate algorithms
offset = imufusion.Offset(sample_rate)
ahrs = imufusion.Ahrs()

ahrs.settings = imufusion.Settings(imufusion.CONVENTION_NWU,  # convention
                                   0.5,  # gain
                                   10,  # acceleration rejection
                                   20,  # magnetic rejection
                                   5 * sample_rate)  # rejection timeout = 5 seconds

# Process sensor data
delta_time = np.diff(timestamp, prepend=timestamp[0])

euler = np.zeros((len(timestamp), 3))
internal_states = np.zeros((len(timestamp), 6))
flags = np.zeros((len(timestamp), 5))
compass_heading = np.zeros((len(timestamp), 1))

mag_post_hard_offset = np.zeros((1, 3))
mag_w_hard_offset = np.zeros((len(timestamp), 3))
compass_heading_hard_offset = np.zeros((len(timestamp), 1))




for i in range(3):
    mag_post_hard_offset[0,i] = (np.max(magnetometer[:, i]) + np.min(magnetometer[:, i])) / 2




for index in range(len(timestamp)):
    compass_heading[index] = imufusion.compass_calculate_heading(imufusion.CONVENTION_NWU, accelerometer[index], magnetometer[index])

    mag_hard_offset = mag_post_hard_offset
    mag_w_hard_offset[index] = magnetometer[index] - mag_hard_offset

    compass_heading_hard_offset[index] = imufusion.compass_calculate_heading(imufusion.CONVENTION_NWU, accelerometer[index], mag_w_hard_offset[index])
    
    
    gyroscope[index] = offset.update(gyroscope[index])

    ahrs.update(gyroscope[index], accelerometer[index], mag_w_hard_offset[index], delta_time[index])
    # ahrs.update_no_magnetometer(gyroscope[index], accelerometer[index], delta_time[index])

    euler[index] = ahrs.quaternion.to_euler()

    ahrs_internal_states = ahrs.internal_states
    internal_states[index] = np.array([ahrs_internal_states.acceleration_error,
                                          ahrs_internal_states.accelerometer_ignored,
                                          ahrs_internal_states.acceleration_rejection_timer,
                                          ahrs_internal_states.magnetic_error,
                                          ahrs_internal_states.magnetometer_ignored,
                                          ahrs_internal_states.magnetic_rejection_timer])

    ahrs_flags = ahrs.flags
    flags[index] = np.array([ahrs_flags.initialising,
                                ahrs_flags.acceleration_rejection_warning,
                                ahrs_flags.acceleration_rejection_timeout,
                                ahrs_flags.magnetic_rejection_warning,
                                ahrs_flags.magnetic_rejection_timeout])
    
    



# Plot generation


# Plot Euler angles
figure, axes = pyplot.subplots(nrows=12, sharex=True, gridspec_kw={"height_ratios": [6, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1]})

figure.suptitle("Euler angles, internal states, and flags")

axes[0].plot(timestamp, euler[:, 0], "tab:red", label="Roll")
axes[0].plot(timestamp, euler[:, 1], "tab:green", label="Pitch")
axes[0].plot(timestamp, euler[:, 2], "tab:blue", label="Yaw")
axes[0].set_ylabel("Degrees")
axes[0].grid()
axes[0].legend()

# Plot initialising flag
plot_bool(axes[1], timestamp, flags[:, 0], "Initialising")

# Plot acceleration rejection internal states and flags
axes[2].plot(timestamp, internal_states[:, 0], "tab:olive", label="Acceleration error")
axes[2].set_ylabel("Degrees")
axes[2].grid()
axes[2].legend()

plot_bool(axes[3], timestamp, internal_states[:, 1], "Accelerometer ignored")

axes[4].plot(timestamp, internal_states[:, 2], "tab:orange", label="Acceleration rejection timer")
axes[4].grid()
axes[4].legend()

plot_bool(axes[5], timestamp, flags[:, 1], "Acceleration rejection warning")
plot_bool(axes[6], timestamp, flags[:, 2], "Acceleration rejection timeout")

# Plot magnetic rejection internal states and flags
axes[7].plot(timestamp, internal_states[:, 3], "tab:olive", label="Magnetic error")
axes[7].set_ylabel("Degrees")
axes[7].grid()
axes[7].legend()

plot_bool(axes[8], timestamp, internal_states[:, 4], "Magnetometer ignored")

axes[9].plot(timestamp, internal_states[:, 5], "tab:orange", label="Magnetic rejection timer")
axes[9].grid()
axes[9].legend()

plot_bool(axes[10], timestamp, flags[:, 3], "Magnetic rejection warning")
plot_bool(axes[11], timestamp, flags[:, 4], "Magnetic rejection timeout")

# Input data plots

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


# Magnetometer data plots

figure, axes = pyplot.subplots(nrows=4, sharex=True)

figure.suptitle("Mag data: raw, compass heading, hard offsets, compass heading")

axes[0].plot(timestamp, magnetometer[:, 0], "tab:red", label="x")
axes[0].plot(timestamp, magnetometer[:, 1], "tab:green", label="y")
axes[0].plot(timestamp, magnetometer[:, 2], "tab:blue", label="z")
axes[0].set_ylabel("uT")
axes[0].grid()
axes[0].legend()

axes[1].plot(timestamp, compass_heading, "tab:red", label="heading")
axes[1].set_ylabel("deg")
axes[1].grid()
axes[1].legend()

axes[2].plot(timestamp, mag_w_hard_offset[:, 0], "tab:red", label="x")
axes[2].plot(timestamp, mag_w_hard_offset[:, 1], "tab:green", label="y")
axes[2].plot(timestamp, mag_w_hard_offset[:, 2], "tab:blue", label="z")
axes[2].set_ylabel("uT")
axes[2].grid()
axes[2].legend()

axes[3].plot(timestamp, compass_heading_hard_offset, "tab:red", label="heading")
axes[3].set_ylabel("deg")
axes[3].grid()
axes[3].legend()

pyplot.show()