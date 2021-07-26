# Running the moving_average script (version 1.1)

Once a new bash shell has been opened, log into the LLO cluster and create the conda environment.<br />

The following are the required arguments, in order:<br />
&nbsp;&nbsp;&nbsp;start time (in GPS or UTC)<br />

&nbsp;&nbsp;&nbsp;end time (in GPS or UTC)<br />

There are also several optional arguments:<br />
&nbsp;&nbsp;&nbsp;-o --output-dir: output directory for timeseries and plots; defaults to the current directory<br />

&nbsp;&nbsp;&nbsp;-d --detector: detector to get omicron glitches from; defaults to 'L1'<br />

&nbsp;&nbsp;&nbsp;-al --averaging_length: number of points to average; defaults to 30<br />

&nbsp;&nbsp;&nbsp;-s --stride: stride between created points in seconds; defaults to 60<br />

&nbsp;&nbsp;&nbsp;-snr --snr_list: list of snr integer values to use, entered as comma separated values or list notation ('5,6,7' or '[5,6,7]'); defaults to '[5,8,10,20]'<br />

Example of running the script:<br />
&nbsp;&nbsp;&nbsp;python moving_average.py 'April 5, 2019' 'April 6, 2019' -o /home/username/public_html/ -d H1 -al 25 -s 90 -snr 7,9,12<br />
