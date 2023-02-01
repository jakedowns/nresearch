import os
import sys
from scapy.utils import RawPcapReader
import time
import numpy as np
from matplotlib import pyplot as plt 
from scipy.spatial.transform import Rotation as R


def printable_timestamp(ts, resol):
    ts_sec = ts // resol
    ts_subsec = ts % resol
    ts_sec_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts_sec))
    return '{}.{}'.format(ts_sec_str, ts_subsec)

def process_pcap(file_name):
    print('Opening {}...'.format(file_name))

    
    arr_size = 0
    
    # run through all packets to get a count for pre-allocating our numpy arrays
    # this runs very fast but this count might also be available directly from scapy
    for (pkt_data, pkt_metadata,) in RawPcapReader(file_name):
        arr_size += 1

    # pre-allocate numpy arrays 
    np_ts_arr = np.empty((arr_size)) # timestamp array
    
    byte_addr_list = [18,21,24,33,36,39,48,50,52] # specify the offset addrs for the bytes you want to evaluate, also specifies ordering for 3x3 matrix reshape
    # byte_addr_list = [52, 50, 48, 39, 36, 33, 24, 21, 18] # alternate ordering
    # byte_addr_list = [48,50,52, 33,36,39,18,21,24] # alternate ordering
    nparr_shape = (arr_size, len(byte_addr_list)) # nparr will be a flat 2d array with packets x byte value
    nparr = np.empty(nparr_shape)
                     
    nparr_3x3mat = np.empty((arr_size,3,3)) # create np array to hold 3x3 matrices for each packet
    nparr_euler = np.empty((arr_size,3)) # creat np array to hold 1x3 array for each packet, will hold euler angles calculated from nparr_3x3mat 
    
    
    
    count = 0
    for (pkt_data, pkt_metadata,) in RawPcapReader(file_name):
        count += 1

        # usb_pkt = USBpcap(pkt_data)
        
        if count % 2000 == 0:
            print(count) # provide progress update if processing is slow

        if count < arr_size + 1: # keeps us within the np array bounds
            pkt_timestamp = (pkt_metadata.tshigh << 32) | pkt_metadata.tslow
            pkt_timestamp_res = pkt_metadata.tsresol

            raw_data_index = 40 # offset within the usb packet to get past the headers and into the raw data
            raw_data = pkt_data[raw_data_index:] 
            
            two_byte_addr_list = [48,50,52] # list of start bytes for values that we are currently decoding as 2byte, signed ints, little endian
            three_byte_addr_list = [18,21,24,33,36,39] # list of start bytes for values that we are currently decoding as 3byte, signed ints, little endian

            ts_sec = pkt_timestamp / pkt_timestamp_res # calculate seconds from the packet timestamp
            np_ts_arr[count-1] = ts_sec
            
            np_temp_arr = np.empty((len(byte_addr_list))) # create a temporary np array to hold your flat values
            
            # print(raw_data.hex())

            # loop through the values of interest, decoding each and adding it to np_temp_arr
            for i in range(len(byte_addr_list)): 
                byte_addr = byte_addr_list[i]
                if byte_addr in two_byte_addr_list:
                    int_byte_len = 2
                else:
                    int_byte_len = 3 # using as default for now
                
                byte_sub = raw_data[byte_addr:byte_addr+int_byte_len] # grab bytes to use for this value
                sig_int_value = int.from_bytes(byte_sub, "little", signed=True) # convert to signed, little endian integer
                
                np_temp_arr[i] = sig_int_value / 2**(8*int_byte_len - 1)               

                      
            nparr[count-1] = np_temp_arr
            
            if len(byte_addr_list) == 9: # need a flat 9 values to create 3x3 matrix
                nparr_3x3mat[count-1] = np.reshape(np_temp_arr, (3,3))
                # nparr[count-1] = np.transpose(np.reshape(np_temp_arr, (3,3)))   # column vs row major
            
                r = R.from_matrix(nparr_3x3mat[count-1]) # create a scipy rotation from the 3x3 mat            
                nparr_euler[count-1] = r.as_euler('zxy', degrees=True) # calculate euler angled from the rotation

        else:
            break # bounds of the pre-allocated numpy arrays has been exceeded   

    
    np_ts_arr = np_ts_arr - np_ts_arr[0] # change the timestamp to be seconds since the start time
    
    # transpose arrays to make it easier to plot signals over time
    nparr_euler = np.transpose(nparr_euler)
    nparr = np.transpose(nparr)
    
    # plot euler angles if they've been calculated
    if len(byte_addr_list) == 9: 
        plt.figure()
        plt.plot(np_ts_arr, nparr_euler[0], label="z_deg")
        plt.plot(np_ts_arr, nparr_euler[1], label="x_deg")
        plt.plot(np_ts_arr, nparr_euler[2], label="y_deg")
        plt.legend() 
        
    # plot decoded values
    # labels here assume that values in byte_addr_list are in order
    
    plt.figure()
    plt.plot(np_ts_arr, nparr[0], label="1a_scaled")
    plt.plot(np_ts_arr, nparr[1], label="1b_scaled")
    plt.plot(np_ts_arr, nparr[2], label="1c_scaled")
    plt.legend() 
    
    plt.figure()
    plt.plot(np_ts_arr, nparr[3], label="2a_scaled")
    plt.plot(np_ts_arr, nparr[4], label="2b_scaled")    
    plt.plot(np_ts_arr, nparr[5], label="2c_scaled")
    plt.legend()
    
    plt.figure()
    plt.plot(np_ts_arr, nparr[6], label="3a_scaled")
    plt.plot(np_ts_arr, nparr[7], label="3b_scaled")
    plt.legend() 
    
    plt.figure()
    plt.plot(np_ts_arr, nparr[8], label="3c_scaled")
    plt.legend()
    plt.show()    
    
    

    print('{} contains {} packets'.format(file_name, count))
    
    return (nparr, np_ts_arr)

if __name__ == '__main__':
    
    # file_name = "C:\\Users\\edwat\\OneDrive\\Documents\\nreal_airs\\capture-12-27-22_ew\\capture-12-27-22\\RollPitchYaw-20230131T194751Z-001\\RollPitchYaw\\roll-pitch-yaw-filtered_tohost_endpoint0x84.pcapng"
    file_name = "new-rotational-capture_filtered.pcapng"
    if not os.path.isfile(file_name):
        print('"{}" does not exist'.format(file_name), file=sys.stderr)
        sys.exit(-1)

    # file has to be processed down to just the relevant packets (e.g. in wireshark: "(usb.darwin.endpoint_address == 0x84) && (usb.dst == "host")")
    nparr, np_ts_arr = process_pcap(file_name)
    sys.exit(0)
