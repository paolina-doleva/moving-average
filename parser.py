import argparse
import os
from gwpy.time import to_gps

def snr_list(arg):
    if arg is list:
        return arg
    else:
        try:
            snr_list = list(map(int, arg.strip('[]').split(',')))
            return snr_list
        except Exception:
            raise ValueError('Please enter a list of snr values')
        

def create_parser():
    """Create a command-line parser for this entry point
    """
    # initialize argument parser
    parser = argparse.ArgumentParser(
        prog='moving_avg',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # required arguments
    parser.add_argument('gpsstart', type=to_gps, help='GPS start time or date and time start')
    parser.add_argument('gpsend', type=to_gps, help='GPS end time or date and time end')

    # optional arguments
    parser.add_argument(
        '-o',
        '--output-dir',
        default=os.curdir,
        type=os.path.abspath,
        help='output directory for plots and timeseries',
    )
    parser.add_argument(
        '-d',
        '--detector',
        default = 'L1',
        help='initials of detector',
    )
    parser.add_argument(
        '-al',
        '--averaging_length',
        default=30,
        type=int,
        help='integer number of points to average',
    )
    parser.add_argument(
        '-s',
        '--stride',
        default = 60,
        type=int,
        help='stride between points in seconds',
    )
    parser.add_argument(
        '-snr',
        '--snr_list',
        default = [5, 8, 10, 20],
        type=snr_list,
        help='list of snr\'s to average separated by commas'
    )
    

    # return the argument parser
    return parser