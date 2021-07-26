"""
Created by: Paolina Doleva 
Version:    1.0
Date:       July 7, 2021
"""

from gwpy.table import EventTable
from gwpy.table.filters import in_segmentlist              
from gwpy.segments import DataQualityFlag, Segment
from gwpy.timeseries import TimeSeries           
from gwtrigfind import find_trigger_files       
from gwpy.plot import Plot
from gwpy.time import to_gps

import numpy as np
from matplotlib import cm
import sys
import os
import parser

#--------------------------------------- VARIABLES ------------------------------------------------#
# make parser and get args
parser = parser.create_parser()
args = parser.parse_args()

actual_start = int(args.gpsstart)
actual_end = int(args.gpsend)
folder_location = args.output_dir
detector = args.detector
STRIDE = args.stride # 60s default
AVERAGE_LEN = args.averaging_length # 30 default
snr_list = args.snr_list # [5, 8, 10, 20] default

out_folder = os.path.join(folder_location, f'm{AVERAGE_LEN*STRIDE//60}avg')
ts_cushion = STRIDE * AVERAGE_LEN / 2
start, end = actual_start-ts_cushion, actual_end+ts_cushion   # start earlier and end later to account for averaging

channel             = f'{detector}:GDS-CALIB_STRAIN'  # added detector
analysis_ready_flag = f'{detector}:DMT-ANALYSIS_READY:1'

omicron_MA_dict = {}
for snr in snr_list:
    omicron_MA_dict[snr] = {}
    omicron_MA_dict[snr]['ts'] = TimeSeries([], dt=STRIDE, t0=actual_start, channel=channel, name=f'MA_{snr}')
    omicron_MA_dict[snr]['mean_list'] = []

#--------------------------------------------------------------------------------------------------#

#--------------------------------------- FUNCTIONS ------------------------------------------------#

"""
            moving_average: calculates the moving average for a given period of time on a given
                            event table
            events:         event table containing filtered events
            stride:         the time in seconds for each bin
            avg_len:        the number of data points to be calculated together
            user_start:     start time
            user_end:       end time
"""
def moving_average(events, stride, avg_len, user_start, user_end):
    omicron_rate = events.event_rate(stride, start=user_start, end=user_end)    
    omicron_rate_vals    = omicron_rate.value                         
    average_length       = avg_len
    real_start, real_end = user_start+(stride*avg_len/2), user_end-(stride*avg_len/2)
    moving_averages       = []                                          
    moving_averages_times = np.arange(real_start, real_end+stride, step=stride)
    
    for i in range(len(omicron_rate_vals)-average_length+1): 
        total_points = omicron_rate_vals[i: i + average_length]         
        sma = sum(total_points)/average_length                          
        moving_averages.append(sma)
        time = omicron_rate.times.value[i+int(average_length/2)]                                                                 

    omicron_MA = TimeSeries(moving_averages, times=moving_averages_times)
    return omicron_MA

"""
            check_segs: checks the segments for extremely short periods of time during which
                        the detector was active
            seg_ls:     a list containing the segments
            stride:     the time in seconds for each bin
            avg_len:    the number of data points to be calculated together
"""
def check_segs(seg_ls, stride, avg_len):
    segs_len = len(seg_ls)
    new_seg_ls = []

    for i in range(segs_len):
        segment = seg_ls[i]

        if (segment[1]-segment[0])<(stride*avg_len):
            continue

        new_seg_ls.append(segment)

    return new_seg_ls
#--------------------------------------------------------------------------------------------------#

l1segs = DataQualityFlag.query_dqsegdb(analysis_ready_flag,start,end)
cache  = find_trigger_files(channel, 'omicron', start, end)
events = EventTable.read(cache,tablename='sngl_burst', columns=['peak', 'snr'])

keep = in_segmentlist(events.get_column('peak'), l1segs.active)
filtered_events = events[keep]

for snr in snr_list:
    omicron_MA_dict[snr]['filtered_events'] = filtered_events.filter(f'snr >= {snr}')

new_seg_list = check_segs(l1segs.active, STRIDE, AVERAGE_LEN)

# do averaging
for segment in new_seg_list:
    for snr in snr_list:
        moving_avg = moving_average(omicron_MA_dict[snr]['filtered_events'], STRIDE, AVERAGE_LEN, int(segment[0]), int(segment[1]))
        for i in moving_avg.value:
            omicron_MA_dict[snr]['mean_list'].append(i)
        omicron_MA_dict[snr]['ts'].append(moving_avg, pad=0)

# check if output folder exists
if not os.path.exists(out_folder):
    os.makedirs(out_folder)

# save timeseries
for snr in snr_list:
    out_path = os.path.join(out_folder, '{}.gwf'.format(omicron_MA_dict[snr]['ts'].name))
    omicron_MA_dict[snr]['ts'].write(out_path, format='gwf')

# get standard deviation and mean
for snr in snr_list:
    omicron_MA_dict[snr]['std'] = np.std(omicron_MA_dict[snr]['mean_list'])
    omicron_MA_dict[snr]['mean'] = np.mean(omicron_MA_dict[snr]['mean_list'])

# plotting
c_map = cm.get_cmap('magma', len(snr_list))
    
plot1 = Plot(figsize=(20, 7))
ax1 = plot1.gca()
for index, snr in enumerate(snr_list):
    ax1.plot(omicron_MA_dict[snr]['ts'], label=omicron_MA_dict[snr]['ts'].name, color=c_map.colors[index])
ax1.set_yscale('log')
ax1.set_ylabel('Glitch rate MA[Hz]')
ax1.set_xlim(start,end)
ax1.legend()

plot2 = Plot(figsize=(20, 7))
ax2 = plot2.gca()
for index, snr in enumerate(snr_list):
    ax2.plot(omicron_MA_dict[snr]['ts'], label=omicron_MA_dict[snr]['ts'].name, color=c_map.colors[index])
    ax2.axhline(omicron_MA_dict[snr]['mean']-omicron_MA_dict[snr]['std'], linestyle='--', label=f'Mean{snr}-STD', color=c_map.colors[index])
    ax2.axhline(omicron_MA_dict[snr]['mean']+omicron_MA_dict[snr]['std'], linestyle='--', label=f'Mean{snr}+STD', color=c_map.colors[index])
ax2.set_xlim(start,end)
ax2.legend()

plot1.save(os.path.join(out_folder, 'plot_1.jpg'))
plot2.save(os.path.join(out_folder, 'plot_2.jpg'))