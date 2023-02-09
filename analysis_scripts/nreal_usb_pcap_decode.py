import os
import sys
from scapy.utils import RawPcapReader
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy
import math


def printable_timestamp(ts, resol):
    ts_sec = ts // resol
    ts_subsec = ts % resol
    ts_sec_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts_sec))
    return '{}.{}'.format(ts_sec_str, ts_subsec)

def decode_packet(bytes_buffer):
    global np_value_len
    array_length = np_value_len
    value_arr = np.empty((array_length))
    
    array_addr = 0
    # 
    gyro_list = [18,21,24]
    
    for addr in gyro_list:
        int_byte_len = 3
        byte_sub = bytes_buffer[addr:addr+int_byte_len] # grab bytes to use for this value
        unscaled_value = int.from_bytes(byte_sub, "little", signed=True) # convert to signed, little endian integer
        value_arr[array_addr] = unscaled_value * 1/2**(8*int_byte_len - 1) *  2000
        array_addr += 1
        
    accel_list = [33,36,39]
    for addr in accel_list:
        int_byte_len = 3
        byte_sub = bytes_buffer[addr:addr+int_byte_len] # grab bytes to use for this value
        unscaled_value = int.from_bytes(byte_sub, "little", signed=True) # convert to signed, little endian integer
        value_arr[array_addr] = unscaled_value * 1/2**(8*int_byte_len - 1) *  16
        array_addr += 1
    
    # timestamp nanoseconds
    addr = 4
    int_byte_len = 8
    byte_sub = bytes_buffer[addr:addr+int_byte_len] # grab bytes to use for this value
    value_arr[array_addr] = int.from_bytes(byte_sub, "little", signed=False) # convert to signed, little endian integer
    
    return value_arr
    

def process_pcap(file_name):
    print('Opening {}...'.format(file_name))

    plot_title = file_name.split('\\')[-1]
    
    arr_size = 0
    
    # run through all packets to get a count for pre-allocating our numpy arrays
    # this runs very fast but this count might also be available directly from scapy
    for (pkt_data, pkt_metadata,) in RawPcapReader(file_name):
        arr_size += 1

    # arr_size =  10000 # use to limit to a subset of packets available for testing

    # pre-allocate numpy arrays 
    global np_ts_arr
    np_ts_arr = np.empty((arr_size)) # timestamp array
    
    global np_value_len
    np_value_len = 7
    nparr_shape = (arr_size, np_value_len) # nparr will be a flat 2d array with packets x byte value
    global nparr
    nparr = np.empty(nparr_shape)
                     
       
    count = 0
    for (pkt_data, pkt_metadata,) in RawPcapReader(file_name):
        count += 1

        # usb_pkt = USBpcap(pkt_data)
        
        if count % 20000 == 0:
            print(count) # provide progress update if processing is slow

        if count < arr_size + 1: # keeps us within the np array bounds
            pkt_timestamp = (pkt_metadata.tshigh << 32) | pkt_metadata.tslow
            pkt_timestamp_res = pkt_metadata.tsresol

            raw_data_index = 40 # offset within the usb packet to get past the headers and into the raw data
            raw_data = pkt_data[raw_data_index:] 
            
            ts_sec = pkt_timestamp / pkt_timestamp_res # calculate seconds from the packet timestamp
            np_ts_arr[count-1] = ts_sec
            
            np_temp_arr = decode_packet(raw_data)
            nparr[count-1] = np_temp_arr

        else:
            break # bounds of the pre-allocated numpy arrays has been exceeded   

    
    start_epoch_time_s = np_ts_arr[0]
    end_epoch_time_s = np_ts_arr[-1]

    np_ts_arr = np_ts_arr - start_epoch_time_s # change the timestamp to be seconds since the start of the connected video

    # timing analysis
    np_ts_arr_diff = np.pad(np.diff(np_ts_arr), (1,0), 'constant')

    start_rel_time_s = np_ts_arr[0] # start time
    end_rel_time_s = np_ts_arr[-1] # end time relative to start

    print("first_packet_time: (" + str(start_rel_time_s) + "s) " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_epoch_time_s)))
    print("last_packet_time: (" + str(end_rel_time_s) + "s) " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_epoch_time_s)))
    
    # transpose arrays to make it easier to plot signals against time
    nparr = np.transpose(nparr)
    
    np_ns_arr = (nparr[6] - nparr[6,0]) / 1e9
    np_ns_arr_diff = np.pad(np.diff(np_ns_arr), (1,0), 'constant')
    
    
    global nparr_euler 
    nparr_euler = np.empty((3, arr_size))
    nparr_euler[0] = np.pad(scipy.integrate.cumtrapz(nparr[0], np_ns_arr),(1,0),mode='constant')
    nparr_euler[1] = np.pad(scipy.integrate.cumtrapz(nparr[1], np_ns_arr),(1,0),mode='constant')
    nparr_euler[2] = np.pad(scipy.integrate.cumtrapz(nparr[2], np_ns_arr),(1,0),mode='constant')  
    
    
    # testing alternate methods to integrate gyro data into euler
    # which can work on a dynamic capture, packet by packet
    
    # nparr_euler_alt1 = np.empty((3, arr_size))
    # nparr_euler_alt1[:,0] = [0,0,0]
    
    # for i in range(arr_size-1):
    #     ts_seq = np_ns_arr[i:i+2]
    #     for j in range(3):                   
    #         gyro_seq = nparr[j,i:i+2]
    #         nparr_euler_alt1[j,i+1] = nparr_euler_alt1[j,i] + np.trapz(gyro_seq,ts_seq)
            
    # nparr_euler_alt2 = np.empty((3, arr_size))
    # nparr_euler_alt2[:,0] = [0,0,0]
     
    # for i in range(arr_size-1):
    #     ts_seq = np_ns_arr[i:i+2]
    #     delta_x = ts_seq[1] - ts_seq[0]
    #     for j in range(3):                   
    #         gyro_seq = nparr[j,i:i+2]           
    #         nparr_euler_alt2[j,i+1] = nparr_euler_alt2[j,i] + delta_x* np.sum(gyro_seq)/2
        
    
    # creates a csv file with the euler angles interpolated into so many fps for animation
    
    # fps = 30
    # frames = math.floor(end_rel_time_s * fps)
    # frame_cnt = np.arange(frames)
    # animation_s = frame_cnt / fps
    
    # print(frames)
    
    # anim_output = np.empty((4, frames))
    # anim_output[0] = frame_cnt
    # anim_output[1] = np.interp(animation_s, np_ns_arr, nparr_euler[0])
    # anim_output[2] = np.interp(animation_s, np_ns_arr, nparr_euler[1])
    # anim_output[3] = np.interp(animation_s, np_ns_arr, nparr_euler[2])

    # np.savetxt("anim_output.csv", np.transpose(anim_output), delimiter=",")
     
    

    # plot decoded values
    
    fig = plt.figure()
    fig.suptitle(plot_title)
    ax1 = fig.add_subplot(2,2,1)
    plt.plot(np_ns_arr, nparr[0], label="1a_scaled_dps")
    plt.plot(np_ns_arr, nparr[1], label="1b_scaled_dps")
    plt.plot(np_ns_arr, nparr[2], label="1c_scaled_dps")
    plt.legend() 
    plt.grid(True)

    fig.add_subplot(2,2,2, sharex=ax1)
    plt.plot(np_ns_arr, nparr[3], label="2a_scaled_g")
    plt.plot(np_ns_arr, nparr[4], label="2b_scaled_g")    
    plt.plot(np_ns_arr, nparr[5], label="2c_scaled_g")
    plt.legend()
    plt.grid(True)
    
    fig.add_subplot(2,2,3, sharex=ax1)
    plt.plot(np_ns_arr, nparr_euler[0], label="1a_integ_deg")
    plt.plot(np_ns_arr, nparr_euler[1], label="1b_integ_deg")    
    plt.plot(np_ns_arr, nparr_euler[2], label="1c_integ_deg")
    plt.legend()
    plt.grid(True) 
    
    # fig.add_subplot(2,2,4, sharex=ax1)
    # plt.plot(np_ns_arr, nparr_euler_alt2[0], label="1a_integ_deg_alt2")
    # plt.plot(np_ns_arr, nparr_euler_alt2[1], label="1b_integ_deg_alt2")    
    # plt.plot(np_ns_arr, nparr_euler_alt2[2], label="1c_integ_deg_alt2")
    # plt.legend()
    # plt.grid(True) 
    
    # fig.add_subplot(2,2,4, sharex=ax1)
    # plt.plot(animation_s, anim_output[1], label="1a_integ_deg")
    # plt.plot(animation_s, anim_output[2], label="1b_integ_deg")    
    # plt.plot(animation_s, anim_output[3], label="1c_integ_deg")
    # plt.legend()
    # plt.grid(True) 
    
    
    # plotting nanosecond timestamp from packet against wireshark packet
    
    # plt.figure()
    # plt.plot(np_ns_arr, np_ns_arr, label="timestamp_ns/1e9")
    # plt.plot(np_ns_arr, np_ts_arr, '--', label="wireshark_ts_s")
    # plt.legend()
    # plt.grid(True) 
    
    # plt.figure()
    # plt.plot(np_ns_arr, np_ns_arr_diff, label="diff_timestamp_ns/1e9")
    # # plt.plot(np_ns_arr, np_ts_arr_diff, '--', label="diff_wireshark_ts_s")
    # plt.legend()
    # plt.grid(True) 

    print('{} contains {} packets'.format(file_name, count))
    
    return (nparr, np_ns_arr)


if __name__ == '__main__':
    
    file_names = ["new-rotational-capture_filtered.pcapng"]

    # file has to be processed down to just the relevant packets (e.g. in wireshark: "(usb.darwin.endpoint_address == 0x84) && (usb.dst == "host")")

    for file_name in file_names:
        if not os.path.isfile(file_name):
            print('"{}" does not exist'.format(file_name), file=sys.stderr)
            sys.exit(-1)
        
        nparr, np_ns_arr = process_pcap(file_name)
    plt.show()  
    
    sys.exit(0)
