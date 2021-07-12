# Running the moving_average script (version 1.0)

Once a new bash shell has been opened, log into the LLO cluster and create the conda environment.<br />
The following are the required arguments, in order:<br />
    start time (in GPS or UTC)
    end time (in GPS or UTC)
    plot 1 save location (it is recommended that the name of the .jpg file is specified, as well)
    plot 2 save location
Additional Arguments:
    stride
    average length
Example of running the script:
    python moving_average.py 'April 5, 2019' 'April 6, 2019' '/home/username/public_html/plot1.jpg' '/home/username/public_html/plot2.jpg'
