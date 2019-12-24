# 4c-Visual
This Documentation is about [_4c-Visual_][1], a tool developed by Dr. Etienne Schmelzer. It allows to clean and cross-reference data from 4 different Databases (SalesForce, IQVIA, Redbook, Lauer).

- [Introduction](#Introduction)
    - [4c-update](#4c-update)
    - [4c-Visual](#4c-visual)
- [Setup & authpass.json file](#Setup)


<figure class="video_container">
<iframe width="933" height="700" src="https://app.powerbi.com/view?r=eyJrIjoiMTVjOTc5MGQtMWI1Zi00OTcxLWI5MGYtZmExMmJiODYxMzc0IiwidCI6ImI2N2Q3MjJkLWFhOGEtNDc3Ny1hMTY5LWViZWI3YTZhM2I2NyIsImMiOjN9" frameborder="0" allowFullScreen="true"></iframe>
</figure>


<a name = "Introduction"></a>
## Introduction

### The Need to simplify our access to Data

_Data driven decision making (DDDM)_ has become one of the fundamental concepts of modern businesses. A modern business leverages all its available data in order to take informed decisions. But leveraging all available data is in general difficult and cumbersome as
the data sources are often decentralized, heterogeneous and chaotic. In order to facilitate the
access to four different data sources (SalesForce, IQVIA, Redbook & Lauer) [_4c-Visual_][1] has been created. [_4c-Visual_][1] is a combination of a Python script ([4c-update][2]) and the Business Intelligence Tool [Power BI](https://powerbi.microsoft.com/de-de/) (by Microsoft).

<a name = "4c-update"></a>
### 4c-update
The Python script [4c-update][2]


<a name = "4c-visual"></a>
### 4c-Visual





<a name = "Setup"></a>
## Setup - Environment

- Install the Environment (mainly Conda + simple_salesforce and some additional packages)  
_Use the [environment.yml](environment.yml) or [requirements.txt](requirements.txt) file._
````
conda env create -f environment.yml
````

- Activate the Environment:
````
conda activate clean
````

Now to the authpass.json file. It contains the necessary credentials and stores some
settings. An example is given in [authpass_example.json](authpass_example.json)

### commands
Set to "True" if you would like to clean and cross-reference the rawdataset.
- droogleupdate: Pulls the Data from SalesForce, cleans and cross-references it
- lauerupdate: Cleans and cross-references the data from Lauer
- redbookupdate: Cleans and cross-references the data from Redbook
- iqviaupdate: Cleans and cross-references the data from iqvia  

### "SalesForce"
Contains the Credentials for pulling the Data from Salesforce
- "global_drug_report" contains the report id of the SalesForce Report

### "SF-Sandbox" - optional
_Optional!!_ Only for development purpose - contains Credentials for a Sandbox.

### "filepaths"
Contains the filepaths for 4c-update.
- parent contains the filepath (to your working directory)
_I recommend to use a working directory on SharePoint. It will allow you to synchronize your future Power Bi reports._
- rawdata: Contains your Rawdata
- destpath: Will contain your processed and cross-referenced files


### "corrections"
Contains the corrections for Market Presentation. You can extend this dictionary.

### "corrections_iqvia"
Contains the corrections for the Iqvia Database - correcting some quantities

### "SQLServer" - optional
___Not needed for 4c-Visual!___ Only for development purpose.
Contains the Settings for MSSQL Server

### "DjangoSQLServerSettings" - optional
___Not needed for 4c-Visual!___ Only for development purpose.
Contains the Database Settings for the Django Settings file.


<iframe width="933" height="700" src="https://app.powerbi.com/view?r=eyJrIjoiMTVjOTc5MGQtMWI1Zi00OTcxLWI5MGYtZmExMmJiODYxMzc0IiwidCI6ImI2N2Q3MjJkLWFhOGEtNDc3Ny1hMTY5LWViZWI3YTZhM2I2NyIsImMiOjN9" frameborder="0" allowFullScreen="true"></iframe>

[1]: [https://app.powerbi.com/view?r=eyJrIjoiMTVjOTc5MGQtMWI1Zi00OTcxLWI5MGYtZmExMmJiODYxMzc0IiwidCI6ImI2N2Q3MjJkLWFhOGEtNDc3Ny1hMTY5LWViZWI3YTZhM2I2NyIsImMiOjN9]
[2]: (4c-update.py)
