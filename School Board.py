from bs4 import BeautifulSoup
import requests
import csv
from fuzzywuzzy import fuzz

#decrypt helper function
def decryptCharcode(n,start,end,offset): 
    n = n + offset;
    if (offset > 0 and n > end):
        n = start + (n - end - 1)
    elif (offset < 0 and n < start):
        n = end - (start - n - 1)
    return chr(n);

#decrypt string
def decryptString(enc,offset):
    dec =''
    for i in range(0, len(enc)):
        n = enc[i]
        n = ord(n)
        if (n >= 0x2B and n <= 0x3A):
            dec += decryptCharcode(n,0x2B,0x3A,offset) 
        elif (n >= 0x40 and n <= 0x5A):
            dec += decryptCharcode(n,0x40,0x5A,offset) 
        elif (n >= 0x61 and n <= 0x7A):
            dec += decryptCharcode(n,0x61,0x7A,offset) 
        else:
            dec += enc[i]
    return dec

def scrape():
    URL = "http://www.education.gouv.qc.ca/en/find-a-school-board/"
    r = requests.get(URL)
    soup = BeautifulSoup(r.content,features="lxml")
    match = soup.find_all("tr")

    dList = []
    wordList = ['<a href="','">courriel',' <td>','</td>','">']
    for repElem in match:
        deContent = repElem.decode_contents()
        for word in wordList:
            deContent = deContent.replace(word, 'specialchar')
        storedList = deContent.split("specialchar")
        dList.append(storedList)

    name =[]
    email = []
    diction={}
    for q in range(1,len(dList)):
        name = dList[q][1]
        for i in dList[q]:
            if i.startswith("javascript:linkTo"):
                diction[name] = i    
    #print(diction)
            
    for key in diction:
        email = diction[key].replace(chr(92), '')
        email2 = email.replace("javascript:linkTo_UnCryptMailto('", '')
        email3 = email2.replace("');", '')
        diction[key] = decryptString(email3,-1)
    #print(diction)
    #print(len(diction))

    with open('School Board.csv',newline='', encoding='unicode_escape') as csvfile:
        with open('School_Board_Em.csv','w',newline='', encoding='latin1') as f_out:
            reader = csv.DictReader(csvfile)
            writer = csv.DictWriter(f_out,['School Board','Region','Address','City and Postal Code','Phone Number','Email'])
            writer.writeheader()
            for row in reader:
                for keys in list(diction.keys()):
                    ratio = fuzz.ratio(row['School Board'], keys)
                    if ratio >= 86:
                        emailadd = diction[keys].replace("mailto:",'')
                        row['Email'] = emailadd
                writer.writerow(row)
                #print(row)
        #print(diction.keys())

if __name__ == '__main__':
    scrape()
