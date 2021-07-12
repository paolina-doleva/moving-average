# Running the moving_average script (version 1.0)

Once a new bash shell has been opened, log into the LLO cluster and create the conda environment.<br />

The following are the required arguments, in order:<br />
    start time (in GPS or UTC)<br />
    end time (in GPS or UTC)<br />
    plot 1 save location (it is recommended that the name of the .jpg file is specified, as well)<br />
    plot 2 save location<br />
    
Example of running the script:<br />
    python moving_average.py 'April 5, 2019' 'April 6, 2019' '/home/username/public_html/plot1.jpg' '/home/username/public_html/plot2.jpg'<br />
