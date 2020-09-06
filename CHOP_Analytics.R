# package setup, read in relational databases, creating drug list
library(dplyr)
library(tidyverse)
allergies <- read_csv("/Users/Ned/Downloads/allergies.csv")   
encounters <- read_csv("/Users/Ned/Downloads/encounters.csv")
medications <- read_csv("/Users/Ned/Downloads/medications.csv")
patients <- read_csv("/Users/Ned/Downloads/patients.csv")
procedures <- read_csv("/Users/Ned/Downloads/procedures.csv")
drug_list <- c("Hydromorphone 325 MG", "Fentanyl 100",
               "Oxycodone-acetaminophen 100 Ml")

# filter for drug OD, and date
encounters_OD <- encounters %>% 
  filter(REASONDESCRIPTION == "Drug overdose", START > "1999-07-15 00:00:00")

# merge encounters with patients by patient ID, remove unnecessary columns
master_OD <- encounters_OD %>% 
  left_join(patients, by = c("PATIENT" = "Id")) %>% 
  subset(select = -c(ENCOUNTERCLASS, CODE, PROVIDER, DESCRIPTION, COST, REASONCODE, SSN, DRIVERS, PASSPORT, PREFIX, FIRST, 
                     LAST, SUFFIX, MAIDEN, MARITAL, RACE, ETHNICITY, 
                     GENDER, BIRTHPLACE, ADDRESS, CITY, STATE, ZIP))

# format date columns, create "age at visit" column, filte for ages 18-35 at time of visitt, then create "death at visit indicator" column, 
master_OD$START <- (as.Date(master_OD$START, format = '%y-%m-%d'))
master_OD$STOP <- (as.Date(master_OD$STOP, format = '%y-%m-%d'))
master_OD$AGE_AT_VISIT <- (master_OD$START - master_OD$BIRTHDATE) / 365
master_OD <- filter(master_OD, master_OD$AGE_AT_VISIT > 18, master_OD$AGE_AT_VISIT < 36)
master_OD$DEATH_AT_VISIT_IND <- master_OD$DEATHDATE - master_OD$STOP

#remove unnecessary medications, and create overdose medications list from drug list
medications <- medications %>% 
  subset(select = -c(CODE, COST, REASONCODE, 
                     TOTALCOST, REASONDESCRIPTION, DISPENSES))
medications_OD <- medications %>% filter(str_detect(medications$DESCRIPTION, str_c(drug_list, collapse="|")))

#create csv files for export to python for iteration
write_csv(master_OD, "/Users/Ned/Desktop/Python_WD/OD_selection.csv")
write_csv(medications, "/Users/Ned/Desktop/Python_WD/medications.csv")
write_csv(medications_OD, "/Users/Ned/Desktop/Python_WD/medications_OD.csv")