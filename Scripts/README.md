A quick note on the scripts as they were used for various projects

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Convective Initiation and Accumulated Displacement Errors (Summer 2020) 

Scripts: HRRRE_Finalized.py, HREFCode.py, Obs_Data.py, RunHRRRE.sh, RunHREF.sh, RunObs.sh

These scripts were all prepared to assist in finding displacement errors between high resolution model forecasts and observed precipitation from mesoscale convective systems (MCS).
Inputs were taken from the High Resolution Rapid Refresh Ensemble (HRRRE) and the High Resolution Ensemble Forecast (HREF) models, as well as observational data for approximately 30
MCSs. The scripts then computed precipitation centroids for both modeled and observed precipitation; afterwards, spatial displacements were computed between the modeled and observed
precipitation, for all members of the model and across all hours from convection initiation all the way as far as 18 hours after initiation. Functionally, each pairing of .py 
and .sh for HRRRE, HREF, and Obs performs the exact same task; the .py has the meat and bones of the work for establishing data structures and mathematically finding precipitation
centroids, while the .sh iteratively runs through hourly files for each case of interest. As a result, the three different sets of scripts are only included as a formality; 
only one pairing should be viewed to understand the function of the scripts.

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Machine Learning of Severe Wind Reports (Winter 2020 - Ongoing)

Scripts: PopExtract.ipynb, MergedReports.ipynb, LandUseExtract.ipynb (coming soon)

The scripts mentioned above are used as part of a project on machine learning in association with severe wind reports. Of the data available to us for this project, almost 90%
originated from gusts estimated by physical damage; only about 10% emerged from verification through strictly measured winds (i.e. at an ASOS or local mesonet station). The goal of
the project is to enable better verification of estimated severe winds as actually severe, with the addition of other parameters such as local population density, elevation, and
land use category to further fine-tune the dataset. The PopExtract script extracts local average population on a 5x5 km grid surrounding the storm report and appends it to the 
master dataset. The MergedReports.ipynb merges the existing dataset of storm reports with an additional collection of ASOS/AWOS reports from 2007-2018. Finally, the LandUseExtract 
script (which should be added by the end of January 2021) performs functionally the same task as the PopExtract script; however, due to memory limitations resultant from the
exceptionally large nature of the 1km WRF run used for extracting land use, different data storage methods are required.
