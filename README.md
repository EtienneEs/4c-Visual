# 4c-Visual
This Documentation is about [_4c-Visual_][1], a tool developed by Dr. Etienne Schmelzer. It allows to clean and cross-reference data from 4 different Databases (SalesForce, IQVIA, Redbook & Lauer).

[_4c-Visual_][1] is (a small) visualization element of the __4c-Initiative__. __4c__ stands for ___Comprehensive, Clean and Central Comparator___ _Business Intelligence Tool_.    
The _4c-Initiative_ aims to automate, standardize and centralize the Comparator Workflow.

- [Introduction](#Introduction)
- [Setup & authpass.json file](#Setup)
- [Core Elements](#Core)
    - [4c-update](#4c-update)
    - [4c-Visual](#4c-visual)

<a name = "Introduction"></a>
## Introduction - The Need to simplify our access to Data

_Data driven decision making (DDDM)_ has become one of the fundamental concepts of modern businesses. A modern business leverages all its available data in order to take informed decisions. But leveraging all available data is in general difficult and cumbersome as
the data sources are often decentralized, heterogeneous and chaotic. In order to facilitate the
access to four different data sources (SalesForce, IQVIA, Redbook & Lauer) [_4c-Visual_][1] has been created. [_4c-Visual_][1] is a combination of a Python script ([4c-update][2])/an executable and the Business Intelligence Tool [Power BI (by Microsoft)](https://powerbi.microsoft.com/de-de/).

<div class="fluid-width-video-wrapper">
<iframe width="933" height="700" src="https://app.powerbi.com/view?r=eyJrIjoiMTVjOTc5MGQtMWI1Zi00OTcxLWI5MGYtZmExMmJiODYxMzc0IiwidCI6ImI2N2Q3MjJkLWFhOGEtNDc3Ny1hMTY5LWViZWI3YTZhM2I2NyIsImMiOjN9" frameborder="0" allowFullScreen="true">[Link][1]</iframe>
</div>

[_Open in full screen_][1]



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

### Credentials & Settings: authpass.json
The authpass.json file contains the necessary credentials and stores some
important settings, which are explained below.  
_An example is given in [authpass_example.json](authpass_example.json)_.

- __commands__  
Set to "True" if you would like to clean and cross-reference the rawdataset.
    - droogleupdate: Pulls the Data from SalesForce, cleans and cross-references it
    - lauerupdate: Cleans and cross-references the data from Lauer
    - redbookupdate: Cleans and cross-references the data from Redbook
    - iqviaupdate: Cleans and cross-references the data from iqvia



- __"SalesForce"__  
Contains the Credentials for pulling the Data from Salesforce
    - "global_drug_report" contains the report id of the SalesForce Report



- __"SF-Sandbox" - optional__  
_Optional!!_ Only for development purpose - contains Credentials for a Sandbox.


- __"filepaths"__  
Contains the file paths for the raw data and processed data.  

    - parent contains the file path (to your working directory)
    _I recommend to use a working directory on SharePoint. It will allow you to synchronize your future Power Bi reports._
    - rawdata: Contains your Rawdata
    - destpath: Will contain your processed and cross-referenced files


- __"corrections"__  
Contains the corrections for Market Presentation. You can extend this dictionary.

- __"corrections_iqvia"__  
Contains the corrections for the Iqvia Database - correcting some quantities

- __"SQLServer" - optional__  
_Not needed for 4c-Visual!_ Only for development purpose.
Contains the Settings for MSSQL Server

- __"DjangoSQLServerSettings" - optional__  
    _Not needed for 4c-Visual!_ Only for development purpose.
    Contains the Database Settings for the Django Settings file.


<a name= "Core"></a>
## Core elements of 4c-Visual
4c-Visual is a combination of [4c-update][2] and the Power Bi Report [4c.pbix][3].      
The python script [4c-update][2] extracts, cleans and cross-references the data and can also be
turned into a scheduled executable.  
In contrast the Power Bi Report [4c.pbix][3] in combination with the Microsoft Premium Server
acts as a platform to visualize and distribute the data to the stakeholders/consumers.

<a name = "4c-update"></a>
### 4c-update
The Python script [4c-update][2] is the core piece of this project. It extracts, cleans,
cross-references and saves the data as .csv file for the [4c.pbix][3] Report to be picked up.  
Each data source is processed in four steps:

- Extraction
- Clean up
- Cross-referencing
- Saving as .csv

#### Extraction

- Extracting the data from the source  
    Except for SalesForce all Data is available as .csv files, which are updated only once per Quarter.  
    Therefore [authpass.json][6] contains the Setting "commands" which allows to choose
    independently which data source will be processed and updated.

- formatting it into a pandas Dataframe

__Notes for SalesForce__  
Previous business practice used a SalesForce Report in order to extract the Data from SalesForce.
For simplicity a similar Report was build and used to extract the Data. [4c-update.py][2] contains a GET request
which extracts a "csv"-style content, which is loaded into a pandas DataFrame.  
_If you would like to use a SOQL Query to retrieve your data check out my [SF_connector.py][5]._

#### Clean up
Not all available data is important and necessary for our business, therefore data is filtered and reduced to the essential informations
before loading & processing. Additionally Human data entries can be inconsistent and errorprone. In order to reduce errors and redundancy the
available is corrected, normalized and cleaned.  

- deleting unnecessary rows/columns
- correcting entries
    Allows to clean and standardize the entries in the datasets.
    - The dictionary "corrections" in [authpass.json][6] contains the corrections for the Market Presentations for the SalesForce Data.
        This dictionary can be extended.
    - The dictionary "corrections_iqvia" in [authpass.json][6] contains the corrections for the Quantities in the IQVIA dataset.
        This dictionary can be extended.

#### Cross-referencing
- loading the Reference File [MasterDrugList.xlx]
The current Business workflow dictates that new projects/opportunities are entered manually by a
Project Manager. Unfortunately, manual freetext entries are often source of inconsistent data entries.
Often not only a drugname is entered but also combined with package sizes, commas or further information, thereby distorting
the real proportions and quantities. In order to minimize misspresentations and normalize the data the Drugname & API entries are
cross-referenced with a [MasterDrugList.xlsx][4] containing the majority of traded Drugs and APIs of the business. The Entries
of this Excel file are used as a template to filter the manually entered Drugnames & APIs with regular expressions.  
If the cross-referencing function finds a matching entry it assigns the correct entry in a new Reference column named "Drug" or "API".  
If no match is found in the [MasterDrugList.xlsx][4] the complete string of the dataset, together with a __(not MLD)__ is assigned in the
new Reference column.   

The Reference columns (Drugname & API) are further appended to either a new or an already existing Reference file (depending on "newreference" setting in [authpass.json][6]).  
 _Spoiler:_ The Reference columns will later allow the stakeholders/consumers to search all datasets with only one search.  

- loading the Reference File [MasterDrugList.xlsx][4]
- cross-referencing
    - if match is found: the correct Drugname is assigned  
    - if no match: the original value is assigned together with __(not_MDL)__
- Reference file is generated or appended
    - if "newreference" = True in [authpass.json][6] a new Reference file is generated
    - if "newreference" = False in [authpass.json][6] the existing Reference file is appended

#### Saving
All processed datasets are saved as .csv file in the destination folder



<a name = "4c-visual"></a>
### 4c-Visual
_Some explanation about Power Bi ... to be continued..._

_[4c-Visual][1]_
[![_4c-Visual_](4c-Visual_preview.png)][1]





[//]: # (References)

[1]: https://app.powerbi.com/view?r=eyJrIjoiMTVjOTc5MGQtMWI1Zi00OTcxLWI5MGYtZmExMmJiODYxMzc0IiwidCI6ImI2N2Q3MjJkLWFhOGEtNDc3Ny1hMTY5LWViZWI3YTZhM2I2NyIsImMiOjN9
[2]: (4c-update.py)
[3]: (4c_showcase.pbix)
[4]: (MasterDrugList.xlsx)
[5]: (SF_Connector.py)
[6]: (authpass_example.json)
