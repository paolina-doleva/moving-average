import argparse
import os
from gwpy.time import to_gps

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
    

    # return the argument parser
    return parser