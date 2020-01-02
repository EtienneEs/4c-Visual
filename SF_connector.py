import json
from simple_salesforce import Salesforce
from django.contrib.staticfiles.storage import staticfiles_storage

import re


class SFOpps():
    def __init__(self, authpass):

        self.authpass = authpass
        with open(authpass, "r") as read_file:
            self.authpass=json.load(read_file)


        self.SFLogin = self.authpass["SalesForce"]
        self.username = self.SFLogin["username"]
        self.password = self.SFLogin["password"]
        self.isSandbox = self.SFLogin["isSandbox"]
        self.token = self.SFLogin["token"]
        self.instance = self.SFLogin["sf_org"]

        # Creating a Salesforce session
        self.session= Salesforce(username=self.username,
                                 password=self.password,
                                 security_token=self.token,
                                 instance_url=self.instance,
                                 sandbox=self.isSandbox)
        # Defining report fields we want to have. related tables: e.g. Owner.Name
        self.field_names=["Id",
                          "CreatedDate",
                          "OPPORTUNITY_ID__c",
                          "Owner.Name",
                          "Lead_Project_Manager_BSD__r.Name",
                          "Lead_Project_Manager_BSD__r.Username",
                          "Amount",
                          "Name",
                          "NextStep",
                          "Comparator_INT_ST__c",
                          "type",
                          "CloseDate",
                          "Quote_Requested_Date__c",
                          "StageName",
                          "probability",
                          "Leading_FCS_Site_for_PM_Queue__c",
                          "Leading_FCS_Site_for_Quote_Setup__c",
                          "Description",
                          "Account.Name",
                          "LastModifiedDate",
                          "SyncedQuoteId",
                         ]
        self.soql = """
        SELECT {}
        FROM Opportunity
        WHERE Name LIKE '%com%'
        AND (NOT Name LIKE '%destruction%')
        AND (NOT Name LIKE '%dist%')
        AND (NOT Name LIKE '%pkg%')
        AND (NOT Name LIKE '%compas%')
        AND (NOT Name LIKE '%pack%')
        AND (NOT Name LIKE '%company%')
        AND (NOT Name LIKE '%component%')
        AND (NOT Name LIKE '%outcome%')
        AND (NOT Name LIKE '%forecast%')
        AND (NOT StageName LIKE '%Closed%')
        AND (NOT NextStep LIKE '%provided%')
        AND (NOT NextStep LIKE '%sent%')
        AND (NOT NextStep LIKE '%stalled%')
        AND Quote_Requested_Date__c >= 2019-01-01
                    """.format(','.join(self.field_names))

    def get_results(self):
        self.results = self.session.query_all(self.soql)['records']
        return self.results


class ProductList():
    """
    This Class takes the Description of one Opportunity and returns a clean and iterable product list.
    It further contains the attribute RFQorRFI, which returns the first lines of the description.
    """
    def __init__(self, description):

        self.description=description

        def decipher(description):
            if "|NAME" in description:

                description = re.sub("([\n\s]NAME)", "|NAME", description)
                # Getting rid of new line Character
                description = description.replace("\r", "")
                # Getting rid of another new line Character
                description = description.replace("\n", "")
                # Replace unnecessary :
                description = description.replace(":", "")
                # Replace annoying |MORETHAN3 from Mark ;)
                description = description.replace("|MORETHAN3", "")

                encodings = ["RFQ",
                             "NAME",
                             "GEN",
                             "STR",
                             "QTY",
                             "LEAD",
                             "CTRY",
                             "DOC",
                             "CT",
                             "SHELF",
                             "LOTS",
                             "MFR",
                             "RESU",
                             "NOTE",
                            ]
                for code in encodings:
                    teststring = "[0-9]*{}[0-9]?[\?]?".format(code)
                    description = re.sub(teststring, code, description)



                prod_list = re.split("\|NAME", description)
                RFQorRFI =prod_list.pop(0)
                prod_list = ["|NAME" + p for p in prod_list]
                return (RFQorRFI, prod_list)
            else:
                return ("No Cipher Codes", ["NO Cipher CODE"])

        self.RFQorRFI, self.prod_list = decipher(self.description)


    def l(self):
        if "NO Cipher" in self.prod_list[0]:
            return 0
        else:
            return len(self.prod_list)

    def __str__(self):
        return str(self.prod_list)

    def aslist(self):
        return self.prod_list

    def __iter__(self):
        return iter(self.aslist())

class ProductDetails():
    """
    The ProductDetails class allows to decode a single product entry of the Description field
    into the appropriate attributes.
    It further allows to also clean and harmonize the data before entering into the Database.
    """
    def __init__(self, product):

        self.product=product
        self.prod_details = re.split("\|", self.product)
        # deletes the first, empty list element.
        del self.prod_details[0]



        def match_code(prod_details, code, delete_code=True):
            """
            This function checks if the CIPHER Code is present and returns
            the matching element. If the default setting of delete_code=True,
            the CIPHER codes will further be deleted.
            """
            matches = [s for s in prod_details if code in s]
            try:
                match =matches[0]
                if delete_code == True:
                    pattern = "{}(\s)?".format(code)
                    match = re.sub(pattern, "", match)


            except:
                # If a code is not found it returns a specific error.
                match="{} not found".format(code)

            return match

        # assigning the attributes to the corresponding product details
        self.name=match_code(self.prod_details, "NAME")
        self.generic= match_code(self.prod_details, "GEN")
        self.strength= match_code(self.prod_details, "STR")
        self.quantity= match_code(self.prod_details, "QTY")
        self.lead= match_code(self.prod_details, "LEAD")
        self.ct_data= match_code(self.prod_details, "CT")
        self.documentation= match_code(self.prod_details, "DOC")
        self.country= match_code(self.prod_details, "CTRY")
        self.shelflife= match_code(self.prod_details, "SHELF")
        self.lots= match_code(self.prod_details, "LOTS")
        self.manufacturer= match_code(self.prod_details, "MFR")
        self.resupply= match_code(self.prod_details, "RESU")
        self.note= match_code(self.prod_details, "NOTE")


    def __str__(self):
        return self.name
