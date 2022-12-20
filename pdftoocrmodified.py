import pdf2image
from pytesseract import Output
import cv2
import numpy as np 

try:
    from PIL import Image
except ImportError:
    import Image
import pytesseract


class PdfExtract:

    def __init__(self, pdffile):
        self.source = pdffile

    def pdf_to_img(self):
        return pdf2image.convert_from_path(self.source)

    def ocr_core(self, files):
        wordDictOfDict = {}
        counter = 0
        for file in files:
            pageWiseWordDictOfDict = {}
            counter1 = 0
            #print("name of file?? ",file)
            text = pytesseract.image_to_string(file)
            #print("what is the text??? ",text)
            image = np.array(file)
            #print("what is in image?? ",image)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # window_name = 'Image'
            # cv2.imshow(window_name, rgb)
            results = pytesseract.image_to_data(rgb, output_type=Output.DICT)
            strval = ""
            wordDict = {}
            # highlimit = 5
            # lowlimit = -5
            # # lineText = "Takaful Contract No.:"
            # lineText = "Plan End Date:"
            # finalY = 0
            # finalText = 0
            
            for i in range(0, len(results["text"])):
                # extract the bounding box coordinates of the text region from
                # the current result
                x = results["left"][i]
                y = results["top"][i]
                w = results["width"][i]
                h = results["height"][i]
                # extract the OCR text itself along with the confidence of the
                # text localization
                text = results["text"][i]
                conf = int(results["conf"][i])
                if conf > 0:
                    strval += "//" + text + " " + str(x) + " " + str(y) + " " + str(w) + " " +str(h) 
                    wordDict['text'] =  text
                    wordDict['x'] =  x
                    wordDict['y'] =  y
                    wordDict['w'] =  w
                    wordDict['h'] =  h
                    pageWiseWordDictOfDict[counter1] = wordDict
                    # print(wordDict)
                    wordDict = {}
                    counter1 = counter1 + 1
            wordDictOfDict[counter] = pageWiseWordDictOfDict
            counter = counter + 1
        return wordDictOfDict

    def extraxtVal(self, string, key, keyName, isSplit):
        try:
            #print('>>>>>>>>>>>')
            value = string[string.find(key) + len(key):].replace(':', '').replace('—', '').replace('AED', '').strip()
            print('before split >>>>>>>> ', value)
            #print(isSplit)
            if isSplit:
                returnVal = ''
                flag = 0
                print('after split >>>>>>>> ', value.split(' '))
                valueSplit = value.split(' ')
                if keyName == 'VAT Amount':
                    returnVal = valueSplit[len(valueSplit) - 1]
                elif keyName == 'Gross Premium Amount':
                    returnVal = valueSplit[len(valueSplit) - 1]
                elif keyName == 'Basmah Cancer Charges':
                    returnVal = valueSplit[len(valueSplit) - 1]
                elif keyName == 'Basmah HCV Charges':
                    returnVal = valueSplit[len(valueSplit) - 1]
                else:
                    for val in valueSplit:
                        #print('>>>>>>>>>>>>>>>> ', val)
                        if val.strip() != '' and val.strip() != '0.00':
                            flag = 1
                            returnVal = val.strip()
                            break
                    if flag == 0:
                        returnVal = valueSplit[0]
                return returnVal
            else:
                return value
        except Exception as e:
            print(e)

    def getTagValue(self, wordDictOfDict, keyName, mainText, highlimit, lowlimit, expectedVal, agentName, isSplit, sort, skip, isfullsent):

        # highlimit = 45
        # lowlimit = -45
        finalY = 0
        finalText = 0
        assumedline = ""
        lineText = list(mainText.split(" "))[0]

        if expectedVal != '':
            expectedVal = expectedVal.split(',')
            for j in range(0, len(wordDictOfDict)):
                flag1 = 0
                for i in range(0, len(wordDictOfDict[j])):
                    info = wordDictOfDict[j][i]
                    flag = 0
                    for eVal in expectedVal:
                        if info['text'].find(eVal) > -1:
                            assumedline = eVal
                            flag = 1
                            flag1 = 1
                            break
                    if flag == 1:
                        flag1 = 1
                        break
                if flag1 == 1:
                    break
            return assumedline
        else:
            value = ''
            for j in range(0, len(wordDictOfDict)):
                flag=0
                print("page no>>>>>>>>>>>>>>", j)
                for i in range(0, len(wordDictOfDict[j])):
                    flag1=0

                    info = wordDictOfDict[j][i]
                    #print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!",len(wordDictOfDict[j][i]))
                    if (info['text'].lower() == lineText.lower()):
                        # print("202020", info['text'])
                        # print("info", info)
                        finalText = lineText
                        finalY = info['y']  
                        assumedline = ""  
                        oArr = []   
                        for id, info in wordDictOfDict[j].items():
                            #print("info['y'] >>", info['y'])
                            #print("finalY >> ", finalY)
                            #print("lowlimit >> ", lowlimit)
                            #print("highlimit >> ", highlimit)
                            if (info['y'] > (finalY + lowlimit)) and (info['y'] < (finalY + highlimit)):
                                assumedline += " " + info['text']
                                oArr.append({"text": info["text"], "x": info["x"], "y": info["y"]})
                        print('@@@@@@@@@@@@@@@@@@@@@@@ ',assumedline)

                        print('@@@@@@@@@@@@@@@@@@@@@@@ ',mainText + ' ............... ' + keyName)
                        # print('@@@@@@@@@@@@@@@@@@@@@@@ >> ', assumedline.lower().find(mainText.lower()))
                        if mainText.lower() == "date:":
                            if (assumedline.lower().find(mainText.lower()) > -1) and (assumedline.lower().find('plan start date') <= -1):
                                lines = sorted(oArr, key=lambda k: k['x'], reverse=False)
                                resText = ''
                                for d in lines:
                                    resText += " " + d['text']
                                #print('#############', resText)
                                assumedline = resText
                                if agentName.lower() != 'oman':
                                    value = self.extraxtVal(assumedline, mainText, keyName, isSplit)
                                else:
                                    value = self.extraxtValForOman(assumedline, mainText, keyName, isSplit)
                                if str(value).strip() != '':
                                    flag=1
                                    flaf1=1
                                   #print('>>>> break')
                                    break
                        elif mainText == "PERIOD OF INSURANCE : TO" and skip == False:
                            assumedline = assumedline.strip()
                            srchVal = assumedline.find("PERIOD OF INSURANCE FROM")
                            if srchVal != -1:
                                pol_sch = assumedline.split('PERIOD OF INSURANCE FROM')[1]

                                # print("pol_sch1010", pol_sch)

                                startdate = pol_sch.split(' TO ')[0].strip()
                                enddate = pol_sch.split(' TO ')[1][:10]

                                # print("--00--", startdate)
                                #print("--0011--", enddate)
                                value = enddate
                        elif mainText == 'Territorial Limit' and skip == False:
                            assumedline = assumedline.strip()
                            srchVal = assumedline.find("Territorial Limit")

                            if srchVal > -1:
                                fstval = assumedline.split("Territorial Limit")[1]
                                actualval = fstval.split("Jurisdiction")[0]

                                value = actualval

                        elif mainText == "Jurisdiction" and skip == False:
                            assumedline = assumedline.strip()
                            srchVal = assumedline.find("Extensions Standard")
                            if srchVal != -1:
                                fstAssume = assumedline.split("Extensions Standard")[0]
                                actualval = fstAssume.split("Jurisdiction")[1].strip()

                                value = actualval

                        elif mainText == "Estimated Annual Wages (in AED)" and skip == False:
                            iy = info['y']
                            fy = finalY
                            # print('0000000000000000000000000000000000000000000')
                            for k in range(i, len(wordDictOfDict[j])):
                                info = wordDictOfDict[j][k]
                                if (info['text'] == 'Total'):
                                    #print('?????????????????????????')
                                    finalY = info['y']  
                                    assumedline = ""  
                                    oArr = []   
                                    for id, info in wordDictOfDict[j].items():
                                        if (info['y'] > (finalY + lowlimit)) and (info['y'] < (finalY + highlimit)):
                                            assumedline += " " + info['text']
                                            oArr.append({"text": info["text"], "x": info["x"], "y": info["y"]})
                                    flag=1        
                                    flag1=1

                                    break
                            #print(assumedline)
                            
                            value = self.extraxtVal(assumedline, 'Total', keyName, isSplit)
                        else:
                            # print(oArr)
                            # print("****************** ", assumedline)
                            #print('@@@@@@@@@@@@@@@@@@@@@@@ ',mainText + ' ............... ' + keyName)
                            if assumedline.lower().find(mainText.lower()) > -1:
                                # print('$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$', oArr)
                                if sort:
                                    lines = sorted(oArr, key=lambda k: k['x'], reverse=False)
                                else:
                                    lines = oArr
                                # print(lines)
                                # break
                                resText = ''
                                for d in lines:
                                    resText += " " + d['text']
                                # print('#############', resText)
                                # break
                                assumedline = resText

                                if isfullsent == False:
                                    if agentName.lower() != 'oman':
                                        value = self.extraxtVal(assumedline, mainText, keyName, isSplit)
                                    else:
                                        value = self.extraxtValForOman(assumedline, mainText, keyName, isSplit)
                                else:
                                    value=assumedline
                                if str(value).strip() != '':
                                   #print('>>>> break')
                                   flag=1
                                   flag1=1
                                   break
                if flag==1:
                    break
                # check break flag
            #print('index position >>>>>> ', i)
            if agentName.lower() != 'oman':
                return value
            else:
                return value

    def CheckValueExistances(self, wordDictOfDict, keyName, mainText, highlimit, lowlimit, expectedVal, agentName, isSplit = False):
        finalY = 0
        finalText = 0
        assumedline = ""
        lineText = list(mainText.split(" "))[0]

        if expectedVal != '':
            expectedVal = expectedVal.split(',')
            for j in range(0, len(wordDictOfDict)):
                flag1=0
                for i in range(0,len(wordDictOfDict[j])):
                    info = wordDictOfDict[j][i]
                    flag = 0
                    for eVal in expectedVal:
                        #print("dec test >>> ", info['text'])
                        #print("except >>>  ", eVal)
                        if info['text'].find(eVal) > -1:
                            assumedline = eVal
                            flag = 1
                            flag1=1
                            break
                    if flag == 1:
                        flag1=1
                        break
                if flag1==1:
                    break

            return assumedline
        else:
            value = ''
            for j in range(0, len(wordDictOfDict)):
                flag=0
                for i in range(0,len(wordDictOfDict[j])):
                    flag1=0
                    info = wordDictOfDict[j][i]
                    if (info['text'].lower().find(lineText.lower())>-1):
                        # print("202020", info['text'])
                        # print("info", info)
                        finalText = lineText
                        finalY = info['y']  
                        assumedline = ""  
                        oArr = []   
                        for id, info in wordDictOfDict[j].items():
                            if (info['y'] > (finalY + lowlimit)) and (info['y'] < (finalY + highlimit)):
                                assumedline += " " + info['text']
                                oArr.append({"text": info["text"], "x": info["x"], "y": info["y"]})
                        #print('@@@@@@@@@@@@@@@@@@@@@@@ ',assumedline)
                        if assumedline.lower().find(mainText.lower()) > -1:
                            value = 'Covered'
                            flag=1
                            flag1=1
                            break
                    if flag1==1:
                        flag=1
                        break
                if flag==1:
                    break
                #print('index position >>>>>> ', i)
            if value == '':
                return 'Not Covered'
            else:
                return value
            



    def getCompanyName(self, wordDictOfDict):
        try:
            highlimit = 5
            lowlimit = -5
            finalY = 0
            finalText = 0
            companyName = '';
            # print('11111111111111111', wordDictOfDict)
            for id, info in wordDictOfDict.items():
                if info['text'].strip().lower() == 'tokio':
                    companyName = 'TOKIO'
                    break
                # print(info['text'])
                elif info['text'].strip().lower() == 'oman':
                    companyName = 'Oman'
                    break
                elif info['text'].strip().lower() == 'sagr':
                    companyName = 'AL SAGR'
                    break
                elif info['text'].strip().lower() == 'fidelity':
                    companyName = 'Fidelity_U'
                    break
                elif info['text'].strip().lower() == 'arabia':
                    companyName = 'Arabia'
                    break
                elif info['text'].strip().lower() == 'takaful' or info['text'].strip().lower() == 'ciskaful':
                    companyName = 'Takaful'
                    break
                elif info['text'].strip().lower() == 'aig':
                    companyName = 'AIG'
                    break
                elif info['text'].strip().lower() == 'axa' or info['text'].strip().lower() == 'ava':
                    companyName = 'AXA'
                    break
                elif info['text'].strip().lower() == 'adnic':
                    companyName = 'ADNIC'
                    break

                elif info['text'] == 'RSA':
                    companyName = 'RSA'
                    break
                elif info['text'].strip().lower() == 'emirates':
                    companyName = 'emirates'
                    break
                elif info['text'].strip().lower() == 'orient':
                    companyName = 'orient'
                    break
            return companyName
        except Exception as e:
            print(e)
            return '2'

    def getProductLobName(self, wordDictOfDict):
        try:
            companyId = 0;
            #print('11111111111111111')
            for id, info in wordDictOfDict.items():
                # print(info['text'])
                if info['text'].strip().lower() == 'workmen\'s':
                        companyId = 'workmen\'s compensation'
                        flag = 1
                        break
                if info['text'].strip().lower() == 'directors':
                        companyId = 'Directors & Officers'
                        flag = 1
                        break
            return companyId
        except Exception as e:
            print(e)
            return 0



#################################

# lineText = "Plan End Date"
# lineText = "Plan Start Date(Effective Date)"
# lineText = "Takaful Contract No"
# lineText = "Participant Name:"

# pdf = PdfExtract("document_2.pdf")
# files = pdf.pdf_to_img()
#print(files)
# wordDictionary = pdf.ocr_core(files)
# print("length", wordDictionary)
# index = 0
# # sentence = pdf.getTagValue(wordDictionary, lineText, True)
# sentence = pdf.getEndrosementType(wordDictionary)


# print(lineText + '  :  ' +sentence)