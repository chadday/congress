import requests
import xmltodict
import csv
import os
import sys

def main(path):
    '''
    XML containing the members of the House of Representatives, 116th Congress and committee details
    '''
    url = 'http://clerk.house.gov/xml/lists/MemberData.xml'
    member_headers = ['state_district', 'bioguide_id', 'full_name', 'formal_name', 'title', 'first_name', 'middle_name', 'last_name', 'suffix', 'sortable_name', 'prior_congress', 'official_name', 'party', 'caucus', 'state_code', 'state', 'district', 'town', 'office_building', 'office_room', 'office_zip', 'office_zip_suffix',  'phone', 'last_elected_date', 'sworn_date']
    com_headers = ['comcode', 'comtype', 'comname', 'majority', 'minority', 'building', 'room', 'phone']
    sub_headers = ['subcode', 'subcomname', 'parent_com', 'parent_com_code', 'building', 'room', 'phone', 'majority',  'minority']
    data = parse_xml(url)
    member_records = []
    com_records = []
    sub_records = []
    get_members(data,member_records)
    get_coms(data,com_records)
    get_subs(data,sub_records)
    writer(member_records,path,member_headers,'house_members')
    writer(com_records,path,com_headers,'house_coms')
    writer(sub_records,path,sub_headers,'house_sub_coms')


def parse_xml(url):
    r = requests.get(url)
    data = r.content
    data = xmltodict.parse(data)
    return data

def get_members(data,member_records):
    for i in data['MemberData']['members']['member']:
        stdistrict = i['statedistrict']
        member_info = i['member-info']
        full_name = member_info['namelist']
        bioguideid = member_info['bioguideID']
        l_name = member_info['lastname']
        f_name = member_info['firstname']
        m_name = member_info['middlename']
        sortable_name = member_info['sort-name']
        suff = member_info['suffix']
        courtesy_title = member_info['courtesy']
        prior_cong = member_info['prior-congress']
        off_name = member_info['official-name']
        formal_name = member_info['formal-name']
        party = member_info['party']
        caucus = member_info['caucus']
        postal_code = member_info['state']['@postal-code']
        state = member_info['state']['state-fullname']
        district = member_info['district']
        town = member_info['townname']
        office_building = member_info['office-building']
        office_room = member_info['office-room']
        office_zip = member_info['office-zip']
        office_zip_suff = member_info['office-zip-suffix']
        phone = member_info['phone']
        elected_date = member_info['elected-date']['@date']
        sworn_date = member_info['sworn-date']['@date']
        record = stdistrict, bioguideid, full_name, formal_name, courtesy_title, f_name, m_name, l_name, suff, sortable_name, prior_cong, off_name, party, caucus, postal_code, state, district, town, office_building, office_room, office_zip, office_zip_suff, phone, elected_date, sworn_date
        member_records.append(record)


def get_coms(data,com_records):
    for com in data['MemberData']['committees']['committee']:
        comcode = com['@comcode']
        comtype = com['@type']
        comname = com['committee-fullname']
        majority = com['ratio']['majority']
        minority = com['ratio']['minority']
        building = com['@com-building-code']
        room = com['@com-room']
        phone = com['@com-phone']
        com_record = comcode, comtype, comname, majority, minority, building, room, phone
        com_records.append(com_record)


def get_subs(data,sub_records):
    for com in data['MemberData']['committees']['committee']:
        parent_code = com['@comcode']
        parent_name = com['committee-fullname']
        if 'subcommittee' in com.keys():
            subs = com['subcommittee']
            for s in subs:
                if isinstance(s,dict):
                    subcode = s['@subcomcode']
                    subname = s['subcommittee-fullname']
                    subroom = s['@subcom-room']
                    subbuilding = s['@subcom-building-code']
                    subphone = s['@subcom-phone']
                    submaj = s['ratio']['majority']
                    submin = s['ratio']['minority']
                    sub_record = subcode, subname, parent_name, parent_code, subbuilding, subroom, subphone, submaj, submin
                    sub_records.append(sub_record)

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