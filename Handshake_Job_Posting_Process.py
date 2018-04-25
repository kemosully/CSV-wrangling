import numpy as np
import pandas as pd
import os
import datetime
import sys
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

'''
This program takes two files that are exports from Handshake and
joins them so that we have an employer ID for every job posting. 
It also processes the student school years column so that just the 
minimum academic level is in a column.

The combined and cleaned file is saved as a tab delimited text file
in the same directory as the two files originated.
~Katie Mahoney O'Sullivan
'''

# open gui to select job posting file
root=tk.Tk()

root.job_posting_csv=filedialog.askopenfilename(
	initialdir = "/",title = "Select Job Postings file",
	filetypes = (("csv","*.csv"),("all files","*.*")))
# save directory so we don't have to search again
directory=os.path.dirname(root.job_posting_csv)
# open gui to select the employer id file
root.employer_id_csv=filedialog.askopenfilename(
	initialdir = directory,title = "Select Employer ID file",
	filetypes = (("csv","*.csv"),("all files","*.*")))

if root.job_posting_csv=='':
	messagebox.showinfo("Process Exited","No job posting file was selected. Process Ended.")
	sys.exit()
elif root.employer_id_csv=='':
	messagebox.showinfo("Process Exited","No employer id file was selected. Process Ended.")
	sys.exit()
else:

	# read the csv files into dataframes
	job_posting_raw=pd.read_csv(root.job_posting_csv)
	employer_id=pd.read_csv(root.employer_id_csv)

	# inner join employer id to job postings
	# since the two test files don't have same date range
	raw_combined_df=pd.merge(job_posting_raw, employer_id, how='inner', 
		left_on='Id', right_on='Postings ID', suffixes=("","_emp"))

	'''# left join employer id to job postings
	raw_combined_df=pd.merge(job_posting_raw, employer_id, how='left', 
		left_on='Id', right_on='Postings ID', suffixes=("","_emp"))
	#print(raw_combined_df.head(n=15))'''

	# select the needed columns into a separate data frame
	combined_df=raw_combined_df.loc[:,
		['Employer ID','Employer','Title','Job Type','Apply Start Date',
		'Postings ID','Expires','School Years','Majors']]
	# rename headers to not have spaces & match the columns in documentation
	combined_df=combined_df.rename(columns={'Employer ID':'employer_id',
		'Employer':'employer_name','Title':'job_title','Job Type':'job_type',
		'Apply Start Date':'apply_start_date','Postings ID':'postings_id','Expires':'expires_date',
		'School Years':'student_school_years','Majors':'qualifications_name'})
	# make sure the IDs are integers
	combined_df[['employer_id','postings_id']]=combined_df[['employer_id',
		'postings_id']].fillna(0.0).astype(int)

	#format dates so they are yyyy-M-d	
	combined_df['apply_start_date']=pd.to_datetime(combined_df['apply_start_date'], format='%Y-%m-%d %H:%M:%S UTC')
	combined_df['expires_date']=pd.to_datetime(combined_df['expires_date'], format='%Y-%m-%d %H:%M:%S UTC')
	combined_df['apply_start_date']=combined_df['apply_start_date'].dt.date
	combined_df['expires_date']=combined_df['expires_date'].dt.date
		
	# select the minimum school year for the student school years column
	combined_df['minimum_academic_level'] = np.where(
		combined_df['student_school_years'].isnull(), 'None Specified',
		np.where(combined_df.student_school_years.str.contains('Freshman'), 'Freshman', 
		np.where(combined_df.student_school_years.str.contains('Sophomore'), 'Sophomore',
		np.where(combined_df.student_school_years.str.contains('Junior'), 'Junior',
		np.where(combined_df.student_school_years.str.contains('Senior'), 'Senior',
		np.where(combined_df.student_school_years.str.contains('Masters'), 'Masters',
		np.where(combined_df.student_school_years.str.contains('Doctorate'), 'Doctorate',
		np.where(combined_df.student_school_years.str.contains('Postdoctoral Studies'), 'Postdoctoral Studies',
		np.where(combined_df.student_school_years.str.contains('Alumni'), 'Alumni', 'None Specified')))))))))

	# test output
	#print(combined_df.head(n=15))

	# save tab delimited file back to the same directory with a date-stamp
	combined_filename=str(directory+'/handshake_job_postings_for_batch_'+str(datetime.date.today())+'.txt')
	combined_df.to_csv(combined_filename, sep='\t', index=False)

	#show message that process was completed
	messagebox.showinfo("Process Complete","The following file has been created:\n"+combined_filename)