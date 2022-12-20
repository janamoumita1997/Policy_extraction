from pdftoocrmodified import PdfExtract
#
from testing_configjson import *
from tikaparser import TikaExtract

class Extraction:
    def __init__(self):
        print('initialize')
    
    def getExtractData(self):
        self.pdfFile = "/home/mentech/Moumita/documents/fire/fire_policy_document1.pdf"
        self.pdf = PdfExtract(self.pdfFile)
        #print(self.pdf)
        #self.tikapdf = TikaExtract(self.pdfFile)
        self.files = self.pdf.pdf_to_img()
        #print(self.files)
        # print(self.files)
        self.files = self.files[:]            #12      diya diffarence not cover for 5 page
        print(len(self.files))

        # print(self.files)
        self.wordDictionary = self.pdf.ocr_core(self.files)

        #self.pdfContent = self.tikapdf.getContent()
   #     #print("pdf content!!!!!!!!!!!!",self.pdfContent)
        #print(self.wordDictionary)
        resArr = []
        keywords = []
        companyName = self.pdf.getCompanyName(self.wordDictionary) # Detect company name of the policy
        print("companyName>>>>>>>>>>>> ", companyName)
        # result = self.pdf.CheckValueExistances(self.wordDictionary, 'workmen\'s compensation', 'workmen\'s compensation', 5, -5, '', "", False)
        # print(result)
        # #Assign keywords base on company name
        keywords = DO_Document
        # keywords = EmiratesPolicyDocument

        for key in keywords:
            if 'isfullsent' not in key:
                key['isfullsent'] = False
            if 'sort' not in key:
                key['sort'] = False
            if 'skip' not in key:
                key['skip'] = False
            if key['justCheck'] == True:
                if key['searchKey'] != '':
                    result = self.pdf.CheckValueExistances(self.wordDictionary, key['keyName'], key['searchKey'], key['highlimit'], key['lowlimit'], key['expectedVal'], "", key['isSplit'])
                else:
                    result = 'Not Covered'
            else:
                result = ''
                if key['searchKey'] != '':
                    result = self.pdf.getTagValue(self.wordDictionary, key['keyName'], key['searchKey'], key['highlimit'], key['lowlimit'], key['expectedVal'], "", key['isSplit'], key['sort'], key['skip'],key['isfullsent'])
                    # if result == '':
                    #     result = self.tikapdf.getValueFromTikaParcer(self.pdfContent, key['searchKey'])
                print(">>>>>>>>>>>>>>>>>>>>>", result)
            if key['keyName']=='Type of Coverage':
                #print("keyname@@@@@@@@@@@@@@@@@@@@@@")
                if result=='Covered':
                    #print("abc@@@@")
                    result=key['searchKey']
                    print("result>>>>>>>>>>>>>",result)
            if 'doubleSpaceRm' in key and key['doubleSpaceRm'] == True:
                result = result.split('  ')[0]
            try:
                if 'splitWith' in key and key['splitWith'] != '':
                    if 'get' in key and key['get'] is not None:
                        print(result.lower().split(key['splitWith'].lower()))
                        if key['get'] == 'last':
                            key['get'] = len(result.lower().split(key['splitWith'].lower())) - 1
                        result = result.lower().split(key['splitWith'].lower())[key['get']]
                    else:
                        result = result.lower().split(key['splitWith'].lower())[0]
            except Exception as e:
                print(e)
            resArr.append({"keyname": key['keyName'], "value": result.replace('Including for difference between Labour Law compensation and', '')})
        print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
        print(resArr)










obj = Extraction()
obj.getExtractData()
