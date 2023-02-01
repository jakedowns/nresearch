import os
import sys
from scapy.utils import RawPcapReader
import time
import numpy as np
from matplotlib import pyplot as plt 
import pandas as pd


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
    num_bytes = 64 # number of bytes to run stats on 
    np_ts_arr = np.empty((arr_size)) # pre-allocate numpy arrays 
    nparr = np.empty((arr_size,num_bytes)) # nparr will be a flat 2d array with packets x byte value
    
    count = 0    
    for (pkt_data, pkt_metadata,) in RawPcapReader(file_name):
        count += 1
        
        if count % 2000 == 0:
            print(count)

        if count < arr_size + 1:
            pkt_timestamp = (pkt_metadata.tshigh << 32) | pkt_metadata.tslow
            pkt_timestamp_res = pkt_metadata.tsresol

            # print(printable_timestamp(pkt_timestamp, pkt_timestamp_res) + ": " + str(len(pkt_data)) + " " + str(pkt_data.hex()))
            raw_data_index = 40
            raw_data = pkt_data[raw_data_index:]

            ts_sec = pkt_timestamp / pkt_timestamp_res
            np_ts_arr[count-1] = ts_sec
            
            np_temp_arr = np.empty((num_bytes))
            
            # print(raw_data.hex())

            for i in range(num_bytes):
                byte_sub = raw_data[i]
                
                sig_int_value = byte_sub # unsigned int decode is automatic here

                np_temp_arr[i] = sig_int_value
                
            nparr[count-1] = np_temp_arr
            

        else:
            break # bounds of the pre-allocated numpy arrays has been exceeded   

    
    np_ts_arr = np_ts_arr - np_ts_arr[0] # change the timestamp to be seconds since the start time
    
    # transpose array to make it easier to plot signals over time
    nparr = np.transpose(nparr)
    
    # create a Dataframe to hold the stats data for ease of printout / display
    stats_columns=["byte_num","average", "min", "max", "unique_values"]
    df = pd.DataFrame(columns=stats_columns)
        
    # calculate stats
    for i in range(64):
        temp_list = []
        temp_list.append(i)
        temp_list.append(np.average(nparr[i]))
        temp_list.append(int(np.min(nparr[i])))
        temp_list.append(int(np.max(nparr[i])))
        temp_list.append(len(np.unique(nparr[i])))
        
        df = pd.concat([df, pd.DataFrame([temp_list], columns=stats_columns)]) 
    
    with pd.option_context('display.max_rows', None,
                       'display.max_columns', None,
                       'display.precision', 3,
                       ):
        print(df)

    print('{} contains {} packets'.format(file_name, count))
    
    return (nparr, np_ts_arr, df)

if __name__ == '__main__':
    
    file_name = "new-rotational-capture_filtered.pcapng"
    
    if not os.path.isfile(file_name):
        print('"{}" does not exist'.format(file_name), file=sys.stderr)
        sys.exit(-1)

    # file has to be processed down to just the relevant packets (e.g. in wireshark: "(usb.darwin.endpoint_address == 0x84) && (usb.dst == "host")")
    nparr, np_ts_arr, df = process_pcap(file_name) 
    sys.exit(0)
