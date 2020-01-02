from pathlib import Path
from simple_salesforce import Salesforce
import requests
import pandas as pd
import re
from io import StringIO
import time
import json

# Get all Paths and definitions:
# authpass file contains all user specific data e.g. File paths
# needs to be in the same folder as python script or executable
authpasspath = Path("authpass.json")
try:
    with open(authpasspath, "r") as read_file:
        authpass = json.load(read_file)
except:
    print("authpass.json has not been provided")
    time.sleep(60)
    exit()

parent = Path(authpass["filepaths"]["parent"])
if parent.is_dir() == False:
    print("Please change filepath parent in authpass.json")
    time.sleep(60)
    exit()


rawpath = parent / Path(authpass["filepaths"]["rawpath"])
destpath = parent / Path(authpass["filepaths"]["destpath"])

MDL_file= rawpath / Path(authpass["filepaths"]["MDL"])
reference_file = parent / destpath / Path(authpass["filepaths"]["reference"])

# Reading in the Reference Master Drug List file
MDL = pd.read_excel(MDL_file, sheet_name=authpass["filepaths"]["MDL_sheetname"])


droogle_file = destpath / Path(authpass["filepaths"]["droogle_file"])

lauer_raw = rawpath / Path(authpass["filepaths"]["lauer_raw"])
lauer_file = destpath / Path(authpass["filepaths"]["lauer_file"])

redbook_raw = rawpath / Path(authpass["filepaths"]["redbook_raw"])
redbook_file = destpath / Path(authpass["filepaths"]["redbook_file"])

iqvia_raw = rawpath / Path(authpass["filepaths"]["iqvia_raw"])
iqvia_file = destpath / Path(authpass["filepaths"]["iqvia_file"])

corrections=authpass["corrections"]


# Salesforce Report ID
report_id = authpass["SalesForce"]["global_drug_report"]
# Get Login data
login = authpass["SalesForce"]["login"]
username = authpass["SalesForce"]["username"]
if username=="":
    username = input("Please insert SalesForce Username:\n>")

password = authpass["SalesForce"]["password"]
if password=="":
    password = input("Please insert SalesForce Password:\n>")

token = authpass["SalesForce"]["token"]
if token=="":
    token = input("Please provide SalesForce Security Token:\n>")
sf_org = authpass["SalesForce"]["sf_org"]


# FUNCTIONS

def extract_packsize(x, y):
    """
    for iqvia
    This function tries to convert x to an integer and returns it. If x is not an
    integer it tries to convert y to an integer and returns it. If y is also not
    an integer it returns None
    """
    try:
        packsize = int(x)

    except:

        try:
            packsize = int(y)

        except:
            packsize = None

    return packsize



def assign_reference_value(test, MDL, searchv, returnv, Error, ErrorM, searchv_start="startany", searchv_ends="endsany"):
    """
    The function takes in the test string and checks if an entry of the Master Drug List
    is present in the test string. If the string is present in  list it returns
    the fitting returnv value (the drug or the api),
    else the function returns the test string.
    """

    param={
        "test&errorM": test+ErrorM,
        "ErrorM": ErrorM,
        "searchdrug": 0,
        "searchapi": 1,
        "startany": "",
        "startwith": "^",
        "returndrug": 0,
        "returnapi": 1,
        "endswith": "$",
        "endsany": ""
    }


    # Make sure that the returnkey is empty
    returnkey = ""
    srvalues = []
    # Iterating through the MDL list to test if the test string is present in the MDL list.
    for drug, API in zip(MDL.Drug, MDL.API):
        # Search and Return variables List:
        #print("Search variables: Drug & API {} : {}                                     \r".format(drug, API), end='')

        srvalues = [drug, API]
        # Define the searchvalue
        searchvalue = "{}{}{}".format((param[searchv_start]),
                                      (srvalues[param[searchv]]),
                                      (param[searchv_ends]))


        # Compile the Regex
        ignorcase = re.compile(searchvalue, re.IGNORECASE)
        # find all solutions and create a solution list
        solution = re.findall(ignorcase, test)
        # If solution found a hit - the Reference value was foudn in the test string
        if solution != []:
            # return the returnvalue
            returnkey = srvalues[param[returnv]]

    if returnkey == "":
        returnkey = param[Error]
    #print(test)
    #print("This is Returnkey " + returnkey)
    return returnkey

def correcting_entries(df, dictionary, inplace=True):
    """
    This Function allows to correct wrong entries in the Database.
    df: pd.dataframe or pd.dataframecolumn eg. df["columnname"]
    dictionary = dict(), containing the values to be corrected as key
        and the correct values as value
    inplace: boolean True corrects the values inplace
    """
    for key in dictionary:
        print(key + " -> " + dictionary[key])
        df.replace(to_replace =key, value = dictionary[key], regex = True, inplace=inplace)

    if inplace==False:
        return df


# Crossreferencing Master Drug and API entries
def crossreferencing(df, ColumnName, newColumnName, searchv, returnv, Error="test&errorM", ErrorM="(notMDL)", position=0, mdl=MDL,
                    searchv_start="startwith", searchv_ends="endsany"):
    """
    Analyses each row of the Column (ColumnName) from the dataframe (df) and crossreferences it
    either to the drug (searchv=searchdrug) or to the API (searchv=searchapi) of the MasterDrugList (MDL).
    In the newly generated column it either inserts the drug (returnv=returndrug) or the API
    (returnv=returnapi). In case that the drugname or api is not in the reference list it returns
    either
    Inserts a new column with the name "newColumname" containing either the Drugname or API from MDL.

    """
    start = time.time()
    print("Crossreferencing {} rows".format(df[ColumnName].count()))
    df.insert(loc=position,
              column=newColumnName,
              value=df.apply(lambda x: assign_reference_value(x[ColumnName],
                                                              mdl,
                                                              searchv,
                                                              returnv,
                                                              Error,
                                                              ErrorM), axis=1))
    end = time.time()
    elapsed = end-start

    print("{} rows were crossreferenced in {} seconds".format(df[ColumnName].count(), elapsed))

def append_referencelist(reference, dataframe):
    addition = dataframe[["Drug","API"]].drop_duplicates()
    df = pd.merge(reference, addition, how="outer")
    return df

# Droogle:
def cleanup_droogle(username, password, token, sf_org, report_id, droogle_file, reference, corrections):
    """
    Complete droogle cleanup. First "Droogle" Data is pulled from SalesForce using
    a predefined SalesForce Report and with the use of request.get(). The dataset is further
    loaded into a pandas dataframe. The dataset is further cleaned with correcting entries function.
    The DataFrame is cross-referenced and saved as .csv file.
    """

    corrections = corrections

    sf = Salesforce(username=username,
                password=password,
                security_token=token)
    sf_org=sf_org
    report_id=report_id

    sf_report_loc = "{0}{1}?view=d&snip&export=1&enc=UTF-8&xf=csv".format(sf_org, report_id)
    #print(sf_report_loc)

    response = requests.get(sf_report_loc, headers=sf.headers, cookies={"sid": sf.session_id})
    new_report = response.content.decode("utf-8")
    # Save the report to a DataFrame.
    droogle = pd.read_csv(StringIO(new_report))
    # Getting Rid of the Confidential warnings and copyright stuff
    droogle.drop(droogle.tail(5).index,inplace=True)

    # Replacing weird values in Market presentation:
    correcting_entries(droogle["Market Presentation"], corrections, inplace=True)



    # Crossreferencing the Master Drug entries
    crossreferencing(droogle,
                     "Drug Name",
                     "Drug",
                     "searchdrug",
                     "returndrug")

    crossreferencing(droogle,
                     "Drug Name",
                     "API", "searchdrug",
                     "returnapi",
                     position=1)

    reference = append_referencelist(reference, droogle)
    print("Saving droogle as .csv file")
    droogle.to_csv(droogle_file, index = False)

    return (droogle, reference)

def clean_lauer(lauer_raw, lauer_file, reference):
    """
    Complete Lauer cleanup. Takes in .csv file from Lauer (german formating).
    Dropping unnecessary rows and columns.
    Cross-referencing the entries.
    Saving and returning the processed dataset.

    lauer_raw: filepath to the .csv file containing the rawdata
    lauer_file: filepath for the processed dataset
    reference: MDL reference dataframe
    """

    # Lauer:
    # Reading in a European CSV file (; as separators and , as decimal separator)
    lauer=pd.read_csv(lauer_raw, sep=';', decimal=",")
    r_rows = lauer["APU / HAP"].count()

    # Cleaning up the APU column to retain only rows with APU (dropping around 151 000 rows)
    lauer=lauer.drop(lauer[(lauer["APU / HAP"] == 0) & (lauer["PpU (APU exkl. NBR)"] == 0)].index)
    c1_rows = lauer["APU / HAP"].count()

    print("Total rows after dropping rows without APU or PPU {} rows".format(c1_rows))


    # Drop rows which do not state the Active Pharmaceutical Ingredient
    lauer= lauer.drop(lauer[lauer["Wirkstoffe"].isna()].index)
    c2_rows = lauer["APU / HAP"].count()

    print("Total rows after dropping rows without API: {} rows".format(c2_rows))


    # Test if a Drug is in the Database
    #lauer2[lauer2["Artikelname (Hauptbegriff)"]=="CISPLATIN"]

    print("Original Dataset: {} rows\nCleaned Dataset: {} rows".format(r_rows,c2_rows))

    # Crossreferencing the Master Drug entries
    crossreferencing(lauer,
                     "Artikelname",
                     "Drug",
                     "searchdrug",
                     "returndrug")

    crossreferencing(lauer,
                     "Wirkstoffe",
                     "API", "searchapi",
                     "returnapi",position=1)

    # Renaming the columns
    print("Renaming the columns to standardize")
    lauer.rename(columns={"Artikelname (Hauptbegriff)": "Product",
                  "Wirkstoffe": "API_l",
                  "Artikelname": "Product-Int",
                  "Menge": "Amount",
                  "Anbieter": "Supplier_short",
                  "Anbietername": "Supplier"
                 }, inplace=True)

    # Deleting unnecessary columns
    del lauer['$']
    del lauer['Gh']

    #print(reference[["Drug","API"]][(reference['Drug'] == "Perjeta")])
    reference = append_referencelist(reference, lauer)
    #print(reference[["Drug","API"]][(reference['Drug'] == "Perjeta")])
    print("Saving lauer to .csv file")
    lauer.to_csv(lauer_file, sep=',', decimal=".", index=False)
    return (lauer, reference)

def clean_redbook(redbook_raw, redbook_file, reference):
    """
    Reading in Redbook rawdata.
    Dropping unnecessary rows
    Cross-referencing the entries with the Reference dataframe.
    Saving and returning processed data and appended reference dataframe

    redbook_raw: filepath to the .csv file containing the rawdata
    redbook_file: filepath for the processed dataset
    reference: MDL reference dataframe
    """
    redbook = pd.read_csv(redbook_raw)
    # Drop rows which do not contain a WAC Package Price
    redbook= redbook.drop(redbook[redbook["WAC Package Price"].isna()].index)

    crossreferencing(redbook,
                     "Product Name",
                     "Drug",
                     "searchdrug",
                     "returndrug")

    crossreferencing(redbook,
                     "Active Ingredient",
                     "API", "searchapi",
                     "returnapi",position=1)

    #redbook["calculated Units"]= round(redbook["AWP Package Price"]/ redbook["AWP Unit Price"])
    #redbook["calculated WAC per Unit"]=redbook["WAC Package Price"] / redbook["calculated Units"]
    redbook =redbook[["Drug", "API",
     "Product Name",
     "Active Ingredient",
     "Manufacturer/Distributor",
     "Generic",
     "Code Type",
     "Identifier",
     "Form",
     "Strength",
     "Package Size",
     "WAC Package Price",
     "AWP Package Price",
     "AWP Unit Price"
     ]]

    #print(reference[["Drug","API"]][(reference['Drug'] == "Perjeta")])
    reference = append_referencelist(reference, redbook)
    #print(reference[["Drug","API"]][(reference['Drug'] == "Perjeta")])
    print("Saving redbook to .csv file")
    redbook.to_csv(redbook_file, sep=',', decimal=".", index=False)

    return (redbook, reference)

def clean_iqvia(iqvia_raw, iqvia_file, reference, corrections_iqvia):

    """
    Reading in the IQVIA dataset.
    Unpivoting/Melting of the different Quarters (humanfriendly to machinefriendly).
    Dropping unnecessary rows and colums.
    Performing some Calculations (Price per standard unit).
    Extracting packsizes from string field.
        (not consistent in string, changes place -
         see function "extract packsizes" for more information)
    Cross-referencing.
    Renaming some columns
    Saving and returning processed data and appended reference dataframe

    iqvia_raw: filepath to the .csv file containing the rawdata
    iqvia_file: filepath for the processed dataset
    reference: MDL reference dataframe
    corrections_iqvia: dictionary with corrections
    """

    # IQVIA:
    iqvia = pd.read_excel(iqvia_raw)

    # Cleaning up the rows by deleting Weird Drug deliveries with two drugs in one row:
    # print(iqvia["Int-Product"].str.contains('&')])
    iqvia.drop(iqvia[iqvia["Int-Product"].str.contains('&')].index, axis=0, inplace=True)

    # Unpivoting Standard Units per Quarter
    print("Unpivoting Standard Units per Quarter")
    iqvia_unit=pd.melt(iqvia,
                    id_vars=iqvia.columns[0:7],
                    value_vars=iqvia.columns[7:20],
                    var_name="Quarter",
                    value_name="Standard Units")


    # Unpivoting Price per Quarter
    print("Unpivoting Price per Quarter")
    iqvia_price=pd.melt(iqvia,
                     id_vars=iqvia.columns[0:7],
                     value_vars=iqvia.columns[20:],
                     var_name="Quarter",
                     value_name = "Price_US")

    # Cleaning up the Quarters in the unit dataframe
    iqvia_unit["Quarter"]=iqvia_unit["Quarter"].str.replace("_.*","")
    # Cleaning up the Quarters in the price dataframe
    iqvia_price["Quarter"]=iqvia_price["Quarter"].str.replace("_.*", "")
    # merging the dataframes:
    iqvia=pd.merge(iqvia_unit, iqvia_price)
    # Dropping Nan row-wise
    iqvia=iqvia.dropna(0)

    # Show Rows with Nan values
    # iqvia[iqvia.isna().any(axis=1)]

    # Only keep rows with positive values in Standard Units:
    iqvia = iqvia[(iqvia['Standard Units'] > 0) | (iqvia['Standard Units'].isnull())]

    # Calculating Price per standard unit
    iqvia["Price per Standard Unit"]=iqvia["Price_US"]/iqvia["Standard Units"]

    # Replacing weird Values:
    print("Correcting weird entries in iqvia")
    correcting_entries(df=iqvia["Int-Pack"], dictionary=corrections_iqvia, inplace=True)

    # Extract the Packsize
    print("Extracting Packsize")
    # Create helper column
    iqvia["SplitString"]=iqvia["Int-Pack"].str.split(' ', expand=False)
    # Create helper column for Packsize extraction
    iqvia["SecondLastItem"]=iqvia["SplitString"].str[-2]
    # helper column for Packsize extraction
    iqvia["LastItem"]=iqvia["SplitString"].str[-1]


    # Applying function to several rows
    iqvia["Packsize"] = iqvia.apply(lambda x: extract_packsize(x["SecondLastItem"], x["LastItem"]), axis=1)

    # delete the unnecessary helper columns:
    iqvia=iqvia.drop(["SplitString", "SecondLastItem","LastItem"], axis=1)

    # Calculate Price per Packs
    iqvia["Price Per Pack"]=iqvia["Price per Standard Unit"]*iqvia["Packsize"]

    #Rounding the Price in order to not have a to long float
    iqvia["Price Per Pack"] = iqvia["Price Per Pack"].round(2)

    # Getting some idea of the distribution of the Standard units
    # iqvia["Standard Units"].describe().apply(lambda x: format(x, 'f'))

    # Displaying rows which show values below 2 standard unitsiqvia[(iqvia['Standard Units'] < 2)]
    # iqvia[(iqvia['Standard Units'] < 2)]

    # Checking for specific values in a dataset
    #iqvia[["Drug","API", "Int-Product", "Molecule List"]][(iqvia['Int-Product'] == "DrugX & Drug Y")]

    # Crossreferencing the Master Drug entries
    crossreferencing(df=iqvia,
                     ColumnName="Int-Product",
                     newColumnName="Drug",
                     searchv="searchdrug",
                     returnv="returndrug",
                     searchv_start="startwith",
                     searchv_ends="endswith")


    #print(iqvia.head())
    crossreferencing(df=iqvia,
                     ColumnName="Molecule List",
                     newColumnName="API",
                     searchv="searchapi",
                     returnv="returnapi",
                     position=1,
                     searchv_start="startwith",
                     searchv_ends="endswith")

    # Renaming of columns
    iqvia.rename(columns={"Price_US": "Total Sales",
                          "Standard Units": "Standard Units per Q"}, inplace=True)

    reference = append_referencelist(reference, iqvia)
    #print(reference[["Drug","API"]][(reference['Drug'] == "Drug X")])
    print("Saving iqvia dataset")
    iqvia.to_csv(iqvia_file, index = False)

    return (iqvia, reference)

def main():
    """
    Main program. Depending on commands in authpass.json droogle, lauer redbook & iqvia
    is processed. For debugging main() returns the different DataFrames.
    """
    # Creating a new Reference Dataframe or appending current Reference file
    if authpass["commands"]["newreference"] == "True":
        reference = pd.DataFrame(columns=["Drug", "API"])
    else:
        reference = pd.read_csv(reference_file)

    droogle=None
    lauer=None
    redbook=None
    iqvia=None

    # Droogle
    if authpass["commands"]["droogleupdate"]=="True":


        print("\nCleaning droogle")
        print("-"*20)

        droogle, reference = cleanup_droogle(username=username,
                                             password=password,
                                             token=token,
                                             sf_org=sf_org,
                                             report_id=report_id,
                                             droogle_file=droogle_file,
                                             reference=reference,
                                             corrections=corrections)

    # Lauer
    if authpass["commands"]["lauerupdate"]=="True":

        print("\nCleaning lauer")
        print("-"*20)

        lauer, reference = clean_lauer(lauer_raw, lauer_file, reference)

    # Redbook
    if authpass["commands"]["redbookupdate"]=="True":

        print("\nCleaning redbook")
        print("-"*20)

        redbook, reference = clean_redbook(redbook_raw, redbook_file, reference)

    # IQVIA
    if authpass["commands"]["iqviaupdate"]=="True":

        print("\nCleaning iqvia")
        print("-"*20)

        iqvia, reference = clean_iqvia(iqvia_raw=iqvia_raw,
                                       iqvia_file=iqvia_file,
                                       reference=reference,
                                       corrections_iqvia=authpass["corrections_iqvia"])


    # Saving reference file
    reference.to_csv(reference_file, index=False)
    if authpass["commands"]["newreference"]=="True":
        print("New Reference File was created")
    else:
        print("The Reference File was updated")
    return (reference, droogle, lauer, redbook, iqvia)

# EXECUTION of 4c-update
reference, droogle, lauer, redbook, iqvia = main()

print("\nThe Script has run successfully - Awesome\n")

print("""
                    Exterminate!
                   /
      _n__n__
     /       \===V==<D
    /_________\\
     |   |   |
    ------------               This script was
    |  || || || \+++----<(     written for you
    =============              by Etienne Schmelzer
    | O | O | O |
   (| O | O | O |\)
    | O | O | O | \\
   (| O | O | O | O\)
 ======================
""")
# For the executable
time.sleep(10)
