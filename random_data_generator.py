from pathlib import Path
import pandas as pd
import random
import re

from string import ascii_uppercase

# suppress scientific notation for jupyter notebook
#pd.options.display.float_format = '{:20,.2f}'.format
# %matplotlib inline
#%matplotlib inline

"""
This is a "throw-away" script, which creates random data with the same format
as the real, processed data.
"""

# filepaths
f_destpath=Path("fake_data")
f_destpath.mkdir(parents=True, exist_ok=True)
f_droogle_file = f_destpath / Path("droogle2.csv")
f_lauer_file = f_destpath / Path("lauer2.csv")
f_reference_file = f_destpath / Path("reference.csv")
f_redbook_file = f_destpath / Path("redbook.csv")
f_iqvia_file = f_destpath / Path("iqvia.csv")

def create_droogle(f_droogle_file):
    """
    creates a fake droogle file for visualization purpose
    """
    list1 = [["Drug_A", "API_A", "_freetext_ Drug_A freetext", "ManufacturerA"],
            ["Drug_A", "API_A", "_freetext_ Drug_A freetext", "ManufacturerB"],
            ["Drug_A", "API_A", "_freetext_ Drug_A freetext", "ManufacturerC"],
            ["Drug_B", "API_B", "_freetext_ Drug_B freetext", "ManufacturerD"],
            ["Drug_B", "API_B", "_freetext_ Drug_B freetext", "ManufacturerA"],
            ["Drug_C", "API_C", "_freetext_ Drug_C freetext", "ManufacturerA"],
            ["Drug_C", "API_C", "_freetext_ Drug_C freetext", "ManufacturerA"],
            ["Drug_C", "API_C", "_freetext_ Drug_C freetext", "ManufacturerA"],
            ["Drug_D", "API_D", "_freetext_ Drug_D freetext", "ManufacturerD"],
            ["Drug_E", "API_E", "_freetext_ Drug_E freetext", "ManufacturerE"],
            ["Drug_F", "API_F", "_freetext_ Drug_F freetext", "ManufacturerC"]]
    sampling = random.choices(list1, k=1000)

    df = pd.DataFrame(sampling, columns=["Drug", "API", "Drug Name", "Manufacturer"])

    supp = []
    for x in range(20):
        supp.append("Supplier{}".format(x))
    random_supp = random.choices(supp, k=400)
    for x in range(280):
        random_supp.append("Supplier1")
    for x in range(200):
        random_supp.append("Supplier2")
    for x in range(120):
        random_supp.append("Supplier3")
    random.shuffle(random_supp)
    df["Supplier"]=random_supp

    discount = ["NaN", "XX%"]
    df["Cash Discount Percentage"]=random.choices(discount, k=1000)

    documentation = ["CoA & CoC & Pedigree",
                     "CoA & Pedigree",
                     "DSCSA Transaction history",
                     "CoA & CoP & Pedigree",
                     "Pedigree only",
                     "CoC & Pedigree"]
    documentation.extend([documentation[1], documentation[4]]*3)
    df["Documentation"]=random.choices(documentation, k=1000)

    MA_Number = ["NDC: XXXXX-XXXX-XX", "MA: XX/X/XX/XXX/XXX", "MA: XX/X/XX/XXX/XXX"]
    df["NDC or MA Number"]=random.choices(MA_Number, k=1000)

    Product= ["250mg/5ml", "40mg/ml",
              "25% 100ml", "25mg/ml, 2ml Vial",
              "1000mg/20ml", "50mg/ml 1x20ml",
              "1mmol/ml", "40 mg tablet",
              "25mg film-coated tablet", "1x 0,1ml vial / 40mg/ml",
              "100mg/50ml", "300mg", "200mg vial",
              "50mg", "25mg", "400mg", "300mg", "2.5mg",
              "100ml bottles", "200U/10ml", "40mg/0.8ml"
              ]
    df["Product & Strength"]=random.choices(Product, k=1000)

    Unit = ["pack of 1 vial", "packs of 5 vials", "packs of 2 PFS", "Pack of 56 tablets", "packs of 2 PFS",
            "pack of 2 vials", "pack of 30 tablets", "bottles of 120 capsules"]
    df["Unit"]=random.choices(Unit, k=1000)

    nUnit = []
    for x in range(20):
        nUnit.append(random.randint(1, 28000))

    for x in range(980):
        nUnit.append(random.randint(1, 1800))
    random.shuffle(nUnit)
    df["# of Units"] = nUnit

    # 'Comparator Cost Currency'
    Currency = ["USD", "GBP", "EUR", "EUR", "CHF", "CHF"]
    df['Comparator Cost Currency']=random.choices(Currency, k=1000)

    # Comparator Cost

    comp_cost = []
    for x in range(200):
        comp_cost.append(random.uniform(2, 10000))

    for x in range(800):
        comp_cost.append(random.uniform(2, 1500))

    random.shuffle(comp_cost)
    df['Comparator Cost']=comp_cost
    df['Comparator Cost'].describe()

    def convert_currency(x,y):
        conversionrate_to_US={
            "USD": 1,
            "GBP": 1.31,
            "EUR": 1.11,
            "CHF": 1.02,
        }
        return x*conversionrate_to_US[y]

    df["Comparator Cost (converted) Currency"]="USD"
    df["Comparator Cost (converted)"]=df.apply(lambda v: convert_currency(v["Comparator Cost"], v["Comparator Cost Currency"]), axis=1)

    # Markup %
    markup= []
    for x in range(200):
        markup.append(random.uniform(-1, 10))

    for x in range(800):
        markup.append(random.uniform(2, 20))
    random.shuffle(markup)
    df["Markup %"] = markup

    # Number of Lots max. allowed
    lots = []
    for x in range(200):
        lots.append(random.randint(1, 5))

    for x in range(800):
        lots.append(1)
    random.shuffle(lots)
    df['Number of Lots']=lots


    expiration = ['08/10/2019', '30/09/2019', '30/09/2018', '29/02/2020',
           '31/03/2019', '31/10/2018', '31/12/2018', '31/12/2019',
           '31/03/2021', '31/05/2019', '30/06/2018', '30/11/2018',
           '31/08/2020', '30/11/2019', '31/08/2019', '30/09/2020',
           '31/10/2019', '01/07/2019', '31/05/2020', '31/01/2019',
           '31/07/2020', '28/02/2019', '30/04/2018', '31/07/2018',
           '30/06/2020', '31/05/2018', '30/06/2019',
           '05/02/2018', '31/07/2019', '31/07/2021', '31/08/2021',
           '30/11/2020', '31/12/2020', '01/11/2022',
           '01/03/2020', '31/12/2021', '01/10/2020', '01/05/2020',
           '01/02/2020', '01/02/2021', '01/09/2019', '01/03/2021',
           '01/12/2020', '01/11/2019', '01/12/2019', '28/02/2021',
           '01/01/2021', '01/08/2020', '01/01/2020', '31/05/2021',
           '01/09/2021', '01/04/2021', '01/06/2019', '01/11/2020',
           '11/04/2019', '21/11/2018', '01/07/2020', '01/09/2020',
           '30/05/2021', '01/10/2019', '01/06/2020', '30/11/2021',
           '01/07/2021', '31/01/2021', '31/10/2021', '30/06/2017',
           '30/03/2021', '01/12/2021', '01/05/2021', '01/10/2021',
           '31/12/2017', '31/01/2018', '31/03/2018', '31/08/2018',
           '17/05/2020', '30/11/2017', '30/05/2018', '31/08/2017']
    df['Expiration Date']=random.choices(expiration, k=1000)

    quantity = []
    for x in range(800):
        quantity.append(random.uniform(15, 500))
    for x in range(200):
        quantity.append(random.uniform(1, 3000))
    random.shuffle(quantity)
    df['Quantity']=quantity

    destination = []
    for x in range(40):
        destination.append("Destination {}".format(x))
    random_dest = random.choices(destination, k=1000)
    df['Final Destination']=random_dest
    df['Schedule Date']=df['Expiration Date']
    df["Synced Quote"]="XXXXX.XXXX"
    df["Line Description"]="freetext-product specific"
    edt = ["1-2 weeks", "4-5 weeks", "2-3 weeks", "10-15 business days"]
    df['Estimated Delivery Timing']=random.choices(edt, k=1000)
    edt = ["Below 25° C", "15 - 25° C", "Ambient", "2 - 8° C", "-20° C"]
    df['Storage Conditions']=random.choices(edt, k=1000)
    df["Transport Condition to Final Destination"]=df['Storage Conditions']
    df['Schedule Amount (converted) Currency']="USD"
    edt = ["Lead PM 1", "Lead PM 2", "Lead PM 3", "Lead PM 4", "Lead PM 5"]
    df['Lead Project Manager']=random.choices(edt, k=1000)
    df['FCS - PO#']="XXXXXXXXXX-XXX"
    opp_id =[]
    for x in range(1000):
        s = 1529694
        opp_id.append(1529694+random.randint(0,30)+x)
    df['OPPORTUNITY ID']=opp_id
    df['Schedule Amount Currency']=df['Comparator Cost Currency']
    df['Schedule Amount']=df['Quantity']*df['Comparator Cost']
    df['Schedule Amount (converted)']=df.apply(lambda v: convert_currency(v['Schedule Amount'], v['Schedule Amount Currency']), axis=1)
    df['FCS part number']="XXXXXX"
    accounts = []
    for x in range(60):
        accounts.append("Client {}".format(x))
    random_accounts = random.choices(accounts, k=1000)
    df['Account Name']=random_accounts
    df['Expiration Date']=df['Schedule Date']

    list2 = [["Spanish", "Spain"],
             ['English', 'United Kingdom of Great Britain and Northern Ireland'],
             ['English', 'United states of America'],
             ['French', 'France'],
             ['Swedish', 'Sweden'],
             ['Italian', 'Italy'],
             ['German', 'Germany'],
             ['German', 'European Union']
            ]
    sampling = random.choices(list2, k=1000)
    df2 = pd.DataFrame(sampling, columns=['Label Language' ,'Market Presentation'])

    df['Label Language'] = df2['Label Language']
    df['Market Presentation'] = df2['Market Presentation']

    df.to_csv(f_droogle_file, index = False)

def create_lauer(f_lauer_file):
    """
    creates a fake lauer file for visualization purpose
    """
    list2 = [["Drug_A", "API_A", "XXXX", "API_A", "Drug_A freetext", "unit",  "Supp", "SupplierA", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_A", "API_A", "XXXX", "API_A", "Drug_A freetext", "unit",  "Supp", "SupplierB", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_A", "API_A", "XXXX", "API_A", "Drug_A freetext", "unit",  "Supp", "SupplierC", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_B", "API_B", "XXXX", "API_B", "Drug_B freetext", "unit",  "Supp", "SupplierD", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_B", "API_B", "XXXX", "API_B", "Drug_B freetext", "unit",  "Supp", "SupplierA", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_C", "API_C", "XXXX", "API_C", "Drug_C freetext", "unit",  "Supp", "SupplierA", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_C", "API_C", "XXXX", "API_C", "Drug_C freetext", "unit",  "Supp", "SupplierA", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_C", "API_C", "XXXX", "API_C", "Drug_C freetext", "unit",  "Supp", "SupplierA", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_D", "API_D", "XXXX", "API_D", "Drug_D freetext", "unit",  "Supp", "SupplierD", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_E", "API_E", "XXXX", "API_E", "Drug_E freetext", "unit",  "Supp", "SupplierE", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_F", "API_F", "XXXX", "API_F", "Drug_F freetext", "unit",  "Supp", "SupplierC", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_A", "API_A", "XXXX", "API_A", "Drug_A freetext", "unit",  "Supp", "ParalleletraderA", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_A", "API_A", "XXXX", "API_A", "Drug_A freetext", "unit",  "Supp", "ParalleletraderB", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_A", "API_A", "XXXX", "API_A", "Drug_A freetext", "unit",  "Supp", "ParalleletraderC", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_B", "API_B", "XXXX", "API_B", "Drug_B freetext", "unit",  "Supp", "ParalleletraderA", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_B", "API_B", "XXXX", "API_B", "Drug_B freetext", "unit",  "Supp", "ParalleletraderB", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_B", "API_B", "XXXX", "API_B", "Drug_B freetext", "unit",  "Supp", "ParalleletraderD", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_C", "API_A", "XXXX", "API_A", "Drug_A freetext", "unit",  "Supp", "ParalleletraderA", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_C", "API_A", "XXXX", "API_A", "Drug_A freetext", "unit",  "Supp", "ParalleletraderB", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_C", "API_A", "XXXX", "API_A", "Drug_A freetext", "unit",  "Supp", "ParalleletraderC", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_D", "API_B", "XXXX", "API_B", "Drug_B freetext", "unit",  "Supp", "ParalleletraderA", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_D", "API_B", "XXXX", "API_B", "Drug_B freetext", "unit",  "Supp", "ParalleletraderB", 12345678, "NaN", 123, 123, 123, 123],
            ["Drug_D", "API_B", "XXXX", "API_B", "Drug_B freetext", "unit",  "Supp", "ParalleletraderD", 12345678, "NaN", 123, 123, 123, 123],
            ]
    sampling = list2

    df_l = pd.DataFrame(sampling, columns=["Drug", "API", 'Product', "API_l", "Product-Int", "Einh.", "Supplier_short", "Supplier", "PZN", "V", "Gewicht Pack. [g]", "Höhe Pack. [mm]", "Breite Pack. [mm]", "Tiefe Pack. [mm]"])
    apu = []
    for x in range(len(df_l)):
        apu.append(random.uniform(2, 1500))
    df_l["APU / HAP"]=apu
    df_l["PpU (APU exkl. NBR)"]=[x-6 for x in apu]
    df_l["PpU-bas. Taxe-EK"]=[x-random.randint(2,10) for x in apu]
    df_l["PpU-bas. Taxe-VK"]=[x-random.randint(-3,10) for x in apu]
    df_l["Amount"]=[random.randint(1,3000) for x in range(len(df_l))]
    df_l.to_csv(f_lauer_file, index = False)
    return df_l

def create_redbook(f_redbook_file, df_l):
    """
    creates a fake redbook file for visualization purpose
    """
    list3 = [["Drug_A", "API_A", "Drug_A freetext", "API_A", "SupplierA", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_A", "API_A", "Drug_A freetext", "API_A", "SupplierB", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_A", "API_A", "Drug_A freetext", "API_A", "SupplierC", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_B", "API_B", "Drug_B freetext", "API_B", "SupplierD", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_B", "API_B", "Drug_B freetext", "API_B", "SupplierA", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_C", "API_C", "Drug_C freetext", "API_C", "SupplierA", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_C", "API_C", "Drug_C freetext", "API_C", "SupplierA", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_C", "API_C", "Drug_C freetext", "API_C", "SupplierA", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_D", "API_D", "Drug_D freetext", "API_D", "SupplierD", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_E", "API_E", "Drug_E freetext", "API_E", "SupplierE", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_F", "API_F", "Drug_F freetext", "API_F", "SupplierC", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_A", "API_A", "Drug_A freetext", "API_A", "ParalleletraderA", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_A", "API_A", "Drug_A freetext", "API_A", "ParalleletraderB", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_A", "API_A", "Drug_A freetext", "API_A", "ParalleletraderC", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_B", "API_B", "Drug_B freetext", "API_B", "ParalleletraderA", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_B", "API_B", "Drug_B freetext", "API_B", "ParalleletraderB", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_B", "API_B", "Drug_B freetext", "API_B", "ParalleletraderD", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_C", "API_A", "Drug_A freetext", "API_A", "ParalleletraderA", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_C", "API_A", "Drug_A freetext", "API_A", "ParalleletraderB", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_C", "API_A", "Drug_A freetext", "API_A", "ParalleletraderC", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_D", "API_B", "Drug_B freetext", "API_B", "ParalleletraderA", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_D", "API_B", "Drug_B freetext", "API_B", "ParalleletraderB", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ["Drug_D", "API_B", "Drug_B freetext", "API_B", "ParalleletraderD", "N", "NDC", "XXXXX-XXXX-XX", "TAB", "250mg"],
            ]


    df_red = pd.DataFrame(list3, columns=['Drug', 'API', 'Product Name', 'Active Ingredient',
           'Manufacturer/Distributor', 'Generic', 'Code Type', 'Identifier',
           'Form', 'Strength'])
    df_red['WAC Package Price'] = df_l["APU / HAP"]*3.5
    df_red['Package Size']=[random.randint(1,50) for x in range(len(df_red))]
    df_red["AWP Package Price"]=[x*random.uniform(1.5, 4) for x in df_red['WAC Package Price']]
    df_red["AWP Unit Price"]=df_red["AWP Package Price"]/df_red['Package Size']
    df_red.to_csv(f_redbook_file, index = False)

def create_iqvia(f_iqvia_file):
    """
    creates a fake iqvia file for visualization purpose
    """
    list4 = [["Drug_A", "API_A", "Drug_A freetext", "API_A", "SupplierA", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_A", "API_A", "Drug_A freetext", "API_A", "SupplierB", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_A", "API_A", "Drug_A freetext", "API_A", "SupplierC", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_B", "API_B", "Drug_B freetext", "API_B", "SupplierD", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_B", "API_B", "Drug_B freetext", "API_B", "SupplierA", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_C", "API_C", "Drug_C freetext", "API_C", "SupplierA", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_C", "API_C", "Drug_C freetext", "API_C", "SupplierA", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_C", "API_C", "Drug_C freetext", "API_C", "SupplierA", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_D", "API_D", "Drug_D freetext", "API_D", "SupplierD", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_E", "API_E", "Drug_E freetext", "API_E", "SupplierE", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_F", "API_F", "Drug_F freetext", "API_F", "SupplierC", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_A", "API_A", "Drug_A freetext", "API_A", "ParalleletraderA", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_A", "API_A", "Drug_A freetext", "API_A", "ParalleletraderB", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_A", "API_A", "Drug_A freetext", "API_A", "ParalleletraderC", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_B", "API_B", "Drug_B freetext", "API_B", "ParalleletraderA", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_B", "API_B", "Drug_B freetext", "API_B", "ParalleletraderB", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_B", "API_B", "Drug_B freetext", "API_B", "ParalleletraderD", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_C", "API_A", "Drug_A freetext", "API_A", "ParalleletraderA", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_C", "API_A", "Drug_A freetext", "API_A", "ParalleletraderB", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_C", "API_A", "Drug_A freetext", "API_A", "ParalleletraderC", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_D", "API_B", "Drug_B freetext", "API_B", "ParalleletraderA", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_D", "API_B", "Drug_B freetext", "API_B", "ParalleletraderB", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ["Drug_D", "API_B", "Drug_B freetext", "API_B", "ParalleletraderD", "packaging_infos", "XXMG/XMG", "vial/dry,quantity"],
            ]



    df_iqvia = pd.DataFrame(list4*20, columns=['Drug', 'API', 'Int-Product', 'Molecule List',
           'Corporation', 'NFC123', 'Int-Strength', 'Int-Pack'
           ])

    # automated country list
    # import country_list as cl
    # for x in cl.countries_for_language("en_US"):
    #    countries.append(x[1])

    countries = ['KOREA', 'MALAYSIA', 'THAILAND', 'BULGARIA', 'CANADA', 'COLOMBIA',
           'CROATIA', 'CZECH REPUBLIC', 'ESTONIA', 'FINLAND', 'FRANCE',
           'GERMANY', 'GREECE', 'HUNGARY', 'IRELAND', 'ITALY', 'NETHERLANDS',
           'NORWAY', 'POLAND', 'ROMANIA', 'SLOVAKIA', 'SLOVENIA', 'SPAIN',
           'SWEDEN', 'SWITZERLAND', 'UK', 'INDIA', 'SOUTH AFRICA', 'TAIWAN',
           'RUSSIA', 'AUSTRALIA', 'AUSTRIA', 'CHINA', 'ECUADOR', 'HONG KONG',
           'JAPAN', 'LEBANON', 'LITHUANIA', 'PORTUGAL', 'PUERTO RICO',
           'SINGAPORE', 'UAE', 'US', 'BANGLADESH', 'ARGENTINA', 'BELARUS',
           'BELGIUM', 'BOSNIA', 'BRAZIL', 'CENTRAL AMERICA', 'CHILE',
           'DOMINICAN REPUBLIC', 'EGYPT', 'INDONESIA', 'KAZAKHSTAN', 'KUWAIT',
           'LATVIA', 'LUXEMBOURG', 'MEXICO', 'NEW ZEALAND', 'PERU',
           'PHILIPPINES', 'SAUDI ARABIA', 'SERBIA', 'TUNISIA', 'TURKEY',
           'URUGUAY', 'VIETNAM', 'ALGERIA', 'FRENCH WEST AFRICA', 'JORDAN',
           'PAKISTAN', 'SRI LANKA', 'VENEZUELA', 'MOROCCO']

    for x in range(len(df_iqvia)//4):
        countries.append('US')
    for x in range(len(df_iqvia)//8):
        countries.append('JAPAN')
        countries.append('GERMANY')
        countries.append('UK')
    for x in range(len(df_iqvia)//16):
        countries.append('CANADA')
        countries.append('FRANCE')
        countries.append('SPAIN')
        countries.append('ITALY')
    random.shuffle(countries)
    df_iqvia["Country"]=random.choices(countries, k=len(df_iqvia))
    quarter = ['Q1 2016', 'Q2 2016', 'Q3 2016', 'Q4 2016', 'Q1 2017', 'Q2 2017',
           'Q3 2017', 'Q4 2017', 'Q1 2018', 'Q2 2018', 'Q3 2018', 'Q4 2018',
           'Q1 2019']
    df_iqvia["Quarter"]=random.choices(quarter, k=len(df_iqvia))
    df_iqvia['Standard Units per Q']=[random.uniform(300, 16000) for x in range(len(df_iqvia))]
    df_iqvia['Total Sales']=df_iqvia['Standard Units per Q']*4#random.uniform(12281, 469641)
    df_iqvia['Price per Standard Unit']=[random.uniform(400, 5500) for x in range(len(df_iqvia))]

    df_iqvia['Price per Standard Unit']=df_iqvia.apply(lambda v: v['Price per Standard Unit']*4 if v["Country"] == 'United States' else  v['Price per Standard Unit'], axis=1)
    df_iqvia['Standard Units per Q']=df_iqvia.apply(lambda v: v['Standard Units per Q']*4 if v["Country"] == 'United States' else  v['Standard Units per Q'], axis=1)

    packsize = [random.randint(1,2) for x in range(len(df_iqvia)//2)]
    for x in range(len(df_iqvia)//2):
        packsize.append(random.randint(1,28))
    df_iqvia['Packsize']=packsize
    df_iqvia['Price Per Pack'] = df_iqvia['Packsize']*df_iqvia['Price per Standard Unit']

    df_iqvia.to_csv(f_iqvia_file, index=False)

def main():
    """
    Create random data for visualization
    """
    create_droogle(f_droogle_file)
    df_l=create_lauer(f_lauer_file)
    create_reference(f_reference_file)
    create_redbook(f_redbook_file, df_l)
    create_iqvia(f_iqvia_file)


if __name__ == '__main__':

    main()

    print("Awesome - random data has been generated")
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
