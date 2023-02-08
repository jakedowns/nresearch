import os
import sys
from scapy.utils import RawPcapReader
import time
import numpy as np
import matplotlib.pyplot as plt
import scipy


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
        
    # potential 64bit timestamp
    addr = 5
    int_byte_len = 4
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

    # arr_size = 10000

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

    capture_delay_f_vid_start_s = 0 

    np_ts_arr = np_ts_arr - start_epoch_time_s + capture_delay_f_vid_start_s # change the timestamp to be seconds since the start of the connected video

    # timing analysis
    np_ts_arr_diff = np.pad(np.diff(np_ts_arr), (1,0), 'constant')

    start_rel_time_s = np_ts_arr[0] # start time relative to start of video
    end_rel_time_s = np_ts_arr[-1] # end time relative to start

    print("first_packet_time: (" + str(start_rel_time_s) + "s) " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_epoch_time_s)))
    print("last_packet_time: (" + str(end_rel_time_s) + "s) " + time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_epoch_time_s)))
    
    # transpose arrays to make it easier to plot signals against time
    nparr = np.transpose(nparr)
    
    global nparr_euler 
    nparr_euler = np.empty((3, arr_size))
    nparr_euler[0] = np.pad(scipy.integrate.cumtrapz(nparr[0], np_ts_arr),(1,0),mode='constant')
    nparr_euler[1] = np.pad(scipy.integrate.cumtrapz(nparr[1], np_ts_arr),(1,0),mode='constant')
    nparr_euler[2] = np.pad(scipy.integrate.cumtrapz(nparr[2], np_ts_arr),(1,0),mode='constant')        
    

    # plot decoded values
    
    fig = plt.figure()
    fig.suptitle(plot_title)
    ax1 = fig.add_subplot(2,2,1)
    plt.plot(np_ts_arr, nparr[0], label="1a_scaled_dps")
    plt.plot(np_ts_arr, nparr[1], label="1b_scaled_dps")
    plt.plot(np_ts_arr, nparr[2], label="1c_scaled_dps")
    plt.legend() 
    plt.grid(True)

    fig.add_subplot(2,2,2, sharex=ax1)
    plt.plot(np_ts_arr, nparr[3], label="2a_scaled_g")
    plt.plot(np_ts_arr, nparr[4], label="2b_scaled_g")    
    plt.plot(np_ts_arr, nparr[5], label="2c_scaled_g")
    plt.legend()
    plt.grid(True)
    
    fig.add_subplot(2,2,3, sharex=ax1)
    plt.plot(np_ts_arr, nparr_euler[0], label="1a_integ_deg")
    plt.plot(np_ts_arr, nparr_euler[1], label="1b_integ_deg")    
    plt.plot(np_ts_arr, nparr_euler[2], label="1c_integ_deg")
    plt.legend()
    plt.grid(True) 

    print('{} contains {} packets'.format(file_name, count))
    
    return (nparr, np_ts_arr)


if __name__ == '__main__':
    
    file_names = ["new-rotational-capture_filtered.pcapng"]

    # file has to be processed down to just the relevant packets (e.g. in wireshark: "(usb.darwin.endpoint_address == 0x84) && (usb.dst == "host")")

    for file_name in file_names:
        if not os.path.isfile(file_name):
            print('"{}" does not exist'.format(file_name), file=sys.stderr)
            sys.exit(-1)
        
        nparr, np_ts_arr = process_pcap(file_name)
    plt.show()  
    
    sys.exit(0)
