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
import sys

#--------------------------------------- VARIABLES ------------------------------------------------#
if sys.argv[1].isdigit():            # now takes both gps and dates
    start           = sys.argv[1]
else:
    start           = to_gps(sys.argv[1])
if sys.argv[2].isdigit():
    end             = sys.argv[2]
else:
    end             = to_gps(sys.argv[2])
file_location1      = sys.argv[3]
file_location2      = sys.argv[4]
if len(sys.argv) != 5:
    detector        = sys.argv[5]    # added detector arg to get H1 data
else:
    detector        = 'L1'

STRIDE = 60
AVERAGE_LEN = 30

omicron_MA_5 = TimeSeries([],dt=STRIDE, t0=start)
omicron_MA_8 = TimeSeries([],dt=STRIDE, t0=start)
omicron_MA_10 = TimeSeries([],dt=STRIDE, t0=start)
omicron_MA_20 = TimeSeries([],dt=STRIDE, t0=start)

mean_list5 = []
mean_list8 = []
mean_list10 = []
mean_list20 = []

channel             = f'{detector}:GDS-CALIB_STRAIN'  # added detector
analysis_ready_flag = f'{detector}:DMT-ANALYSIS_READY:1'
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

    i = 0
    moving_averages       = []                                          
    moving_averages_times = []                                          
     
    while i < len(omicron_rate_vals) - average_length:
        total_points = omicron_rate_vals[i: i + average_length]         
        sma = sum(total_points)/average_length                          
        moving_averages.append(sma)
        moving_averages_times.append(omicron_rate.times.value[i+int(average_length/2)]) 
        i += 1                                                                          

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

filtered_events_5  = filtered_events.filter('snr >= 5')
filtered_events_8  = filtered_events.filter('snr >= 8')
filtered_events_10 = filtered_events.filter('snr >= 10')
filtered_events_20 = filtered_events.filter('snr >= 20')

new_seg_list = check_segs(l1segs.active, STRIDE, AVERAGE_LEN)

for segment in new_seg_list:
    moving_avg_5 = moving_average(filtered_events_5, STRIDE, AVERAGE_LEN, int(segment[0]), int(segment[1]))
    for i in moving_avg_5.value:
        mean_list5.append(i)
    omicron_MA_5.append(moving_avg_5, pad=0)
   
    moving_avg_8 = moving_average(filtered_events_8, STRIDE, AVERAGE_LEN, int(segment[0]), int(segment[1]))
    for i in moving_avg_8.value:
        mean_list8.append(i)
    omicron_MA_8.append(moving_avg_8, pad=0)
    
    moving_avg_10 = moving_average(filtered_events_10, STRIDE, AVERAGE_LEN, int(segment[0]), int(segment[1]))
    for i in moving_avg_10.value:
        mean_list10.append(i)
    omicron_MA_10.append(moving_avg_10, pad=0)

    moving_avg_20 = moving_average(filtered_events_20, STRIDE, AVERAGE_LEN, int(segment[0]), int(segment[1]))
    for i in moving_avg_20.value:
        mean_list20.append(i)
    omicron_MA_20.append(moving_avg_20, pad=0)

std5 = np.std(mean_list5)
std8 = np.std(mean_list8)
std10 = np.std(mean_list10)
std20 = np.std(mean_list20)
mean5 = np.mean(mean_list5)
mean8 = np.mean(mean_list8)
mean10 = np.mean(mean_list10)
mean20 = np.mean(mean_list20)

plot1 = Plot(omicron_MA_5, omicron_MA_8,omicron_MA_10, omicron_MA_20, figsize=(20, 7))
ax1 = plot1.gca()
ax1.set_yscale('log')
ax1.set_ylabel('Glitch rate MA[Hz]')
ax1.set_xlim(start,end)

plot2 = Plot(omicron_MA_5,omicron_MA_8,omicron_MA_10, omicron_MA_20,figsize=(20, 7), label='Omicron Moving Average')
ax2 = plot2.gca()
ax2.axhline(mean5-std5, color='red', linestyle='--', label = 'Mean5-STD')
ax2.axhline(mean5+std5, color='red', linestyle='--', label = 'Mean5+STD')
ax2.axhline(mean8-std8, color='green', linestyle='--', label = 'Mean8-STD')
ax2.axhline(mean8+std8, color='green', linestyle='--', label = 'Mean8+STD')
ax2.axhline(mean10-std10, color='pink', linestyle='--', label = 'Mean10-STD')
ax2.axhline(mean10+std10, color='pink', linestyle='--', label = 'Mean10+STD')
ax2.axhline(mean20-std20, color='cyan', linestyle='--', label = 'Mean20-STD')
ax2.axhline(mean20+std20, color='cyan', linestyle='--', label = 'Mean20+STD')
ax2.set_xlim(start,end)
ax2.legend()

plot1.save(file_location1)
plot2.save(file_location2)