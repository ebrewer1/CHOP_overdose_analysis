#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 19:10:36 2020

@author: Ned Brewer
"""
# setup of packages
import os
import wget
import pandas as pd
import numpy as np
import re
from datetime import datetime, timedelta 

# reading in the csv files made in R, and formatting the results dataframe by 
# using existing columns as well as adding blank ones
master_OD = pd.read_csv("OD_selection.csv")
meds = pd.read_csv("medications.csv")
meds_OD = pd.read_csv("medications_OD.csv")
results_OD = pd.DataFrame(master_OD.iloc[:,3])
results_OD = results_OD.rename(columns = {"PATIENT" : "PATIENT_ID"})
results_OD["ENCOUNTER_ID"] = master_OD.iloc[:, 0]
results_OD["HOSPITAL_ENCOUNTER_DATE"] = master_OD.iloc[:, 1]
results_OD["AGE_AT_VISIT"] = master_OD.iloc[:, 7]
for index, row in master_OD.iterrows():
    if row["DEATH_AT_VISIT_IND"] == 0:
        master_OD.loc[index, "DEATH_AT_VISIT_IND"] = 1`
    elif row["DEATH_AT_VISIT_IND"] > 0:
        master_OD.loc[index, "DEATH_AT_VISIT_IND"] = 0
results_OD["DEATH_AT_VISIT_IND"] = master_OD.iloc[:, 8]
results_OD["COUNT_CURRENT_MEDS"] = np.nan
results_OD["COUNT_CURRENT_MEDS"] = np.nan
results_OD["CURRENT_OPIOID_IND"] = np.nan
results_OD["READMISSION_90_DAY_IND"] = np.nan
results_OD["READMISSION_30_DAY_IND"] = np.nan
results_OD["FIRST_READMISSION_DATE"] = np.nan
meds = meds.fillna(value = {'STOP': "2020-09-04"})
meds_OD = meds_OD.fillna(value = {'STOP': "2020-09-04"})

# now that the results dataframe is properly formatted, I iterate through the "master_OD" encounters
# dataframe, adding the current med count at the time of visit, as well as the overdose med indicator
for index, row in master_OD.iterrows():
    start = row["START"] 
    stop = row["STOP"] 
    enc = row["Id"]
    patient = row["PATIENT"]
    meds_current = meds[(meds["START"] <= start) & (meds["STOP"] >= stop) & (meds["PATIENT"] == patient)]
    od_meds_current = meds_OD[(meds_OD["START"] <= start) & (meds_OD["STOP"] >= stop) & (meds_OD["PATIENT"] == patient)]

    if not od_meds_current.empty:
        results_OD.iloc[index, 6] = 1 
    else:
        results_OD.iloc[index, 6] = 0 
    
    medcount = len(meds_current.index)
    results_OD.iloc[index, 5] = medcount

# then I sort the master_OD df first by patient id, then by start date of encounter.
master_OD = master_OD.sort_values(["PATIENT", "START"], ascending=[True, True])
patient_count = 0

# this iteration goes through the sorted master_OD df, to find the next encounter and check if it
# is within 90 days, 30 days, and then make put the date of the first encounter within 90 days
for index, row in master_OD.iterrows():
    start = row["START"] 
    stop = row["STOP"] 
    enc = row["Id"]
    patient = row["PATIENT"]
    if patient_count > 0:
        date_diff = (pd.to_datetime(start) - pd.to_datetime(prev_stop)).days
    if patient_count == 0:
        patient_count += 1
    elif row["PATIENT"] == prev_patient and date_diff <= 90:
        readmit_date = str(results_OD.iloc[prev_index, 9])
        results_OD.iloc[prev_index, 7] = 1
        if readmit_date > start:
            results_OD.iloc[prev_index, 9] = start
        if row["PATIENT"] == prev_patient and date_diff <= 30:
            results_OD.iloc[prev_index, 8] = 1
            if readmit_date > start:
                results_OD.iloc[prev_index, 9] = start
    
    prev_index = index   
    prev_patient = row["PATIENT"]
    prev_stop = row["STOP"]

# this writes the results to a csv
results_OD.to_csv('CHOP_OD_results.csv', index=False)
   