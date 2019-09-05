import requests
import xmltodict
import csv
import os
import sys


def main(path):
    '''
    XML containing the members of the House of Representatives, 116th Congress and committee details
    '''
    url = 'https://www.senate.gov/legislative/LIS_MEMBER/cvc_member_data.xml'
    sen_headers = ['state', 'bioguideid', 'member_id', 'first_name', 'last_name', 'suffix', 'party', 'town', 'office', 'state_rank']
    com_agn_headers = ['bioguideid', 'first_name', 'last_name', 'comcode', 'comname', 'position']
    data = parse_xml(url)
    senators = []
    com_records = []
    get_senators(data,senators)
    get_com_assignments(data,com_records)
    writer(senators,path,sen_headers,'senators')
    writer(com_records,path,com_agn_headers,'senators_com_assignments')


def parse_xml(url):
    r = requests.get(url)
    data = r.content
    data = xmltodict.parse(data)
    return data

def get_senators(data,senators):
    for i in data['senators']['senator']:
        state = i['state']
        memid = i['@lis_member_id']
        bioguideid = i['bioguideId']
        first_name = i['name']['first']
        last_name = i['name']['last']
        suffix = i['name']['suffix']
        party = i['party']
        town = i['homeTown']
        state_rank = i['stateRank']
        office = i['office']
        record = state, bioguideid, memid, first_name, last_name, suffix, party, town, office, state_rank
        senators.append(record)


def get_com_assignments(data,com_records):
    for com in data['senators']['senator']:
        bioguideid = com['bioguideId']
        first_name = com['name']['first']
        last_name = com['name']['last']
        for d in com['committees']['committee']:
            comcode = d['@code']
            comname = d['#text']
            if '@position' in d.keys():
                position = d['@position']
            else:
                position = None
        com_record = bioguideid, first_name, last_name, comcode, comname, position
        com_records.append(com_record)


def writer(data,path,headers,name):
    '''
    Creates a new csv of the current list of foias on the FBI's recently added page
    '''
    with open(path+'/'+name+'.csv', "w") as outfile:
        writer = csv.writer(outfile, quotechar='"')
        writer.writerow(headers)
        for csv_row in data:
            writer.writerow(csv_row)
        print("CSV File Ready")



if __name__=="__main__":
    try:
        dir_path = os.path.abspath(sys.argv[1])
        print("Using {}".format(dir_path))
        main(dir_path)
    except IndexError:
        msg = "ERROR: You must invoke this script with a target directory" +\
            "\n\tpython senate.py /path/to/files"
        print(msg)
