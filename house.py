'''
Retrieve data on U.S. House of Representatives members.
'''
import csv
from datetime import datetime
import requests
import xmltodict


def main():
    '''
    Retrieve latest listing of House members, committees and subcommittees.
    '''
    house_url = 'http://clerk.house.gov/xml/lists/MemberData.xml'
    csvs = {
        'house/metadata.csv': [],
        'house/house_members.csv': [],
        'house/house_coms.csv': [],
        'house/house_sub_coms.csv': []
    }
    data = parse_xml(house_url)
    csvs['house/metadata.csv'].append(parse_metadata(data))
    csvs['house/house_members.csv'] = [parse_member(m)
                                       for m in data['MemberData']['members']['member']]
    csvs['house/house_coms.csv'] = [parse_coms(c)
                                    for c in data['MemberData']['committees']['committee']]
    csvs['house/house_sub_coms.csv'] = [parse_subcoms(
        c) for c in data['MemberData']['committees']['committee'] if parse_subcoms(c) is not None]
    for k in csvs.keys():
        writer(csvs, k)


def parse_xml(url):
    '''
    Parse xml
    '''
    return xmltodict.parse(requests.get(url).content)


def parse_metadata(data):
    '''
    Flattens House file metadata
    '''
    metadata = data['MemberData']['title-info']
    metadata['publish-date'] = data['MemberData']['@publish-date']
    metadata['data-retrieve-datetime'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return metadata


def parse_member(member):
    '''
    Flattens member data
    '''
    mi = member['member-info']
    return {
        'state_district': member['statedistrict'],
        'bioguide_id': mi['bioguideID'],
        'sortable_name': mi['sort-name'],
        'full_name': mi['namelist'],
        'title': mi['courtesy'],
        'first_name': mi['firstname'],
        'middle_name': mi['middlename'],
        'last_name': mi['lastname'],
        'suffix': mi['suffix'],
        'official_name': mi['official-name'],
        'formal_name': mi['formal-name'],
        'prior_congress': mi['prior-congress'],
        'party': mi['party'],
        'caucus': mi['caucus'],
        'state_code': mi['state']['@postal-code'],
        'state': mi['state']['state-fullname'],
        'district': mi['district'],
        'town': mi['townname'],
        'office_building': mi['office-building'],
        'office_room': mi['office-room'],
        'office_zip': mi['office-zip'],
        'office_zip_suffix': mi['office-zip-suffix'],
        'phone': mi['phone'],
        'last_elected_date': mi['elected-date']['@date'],
        'sworn_date': mi['sworn-date']['@date']
    }


def parse_coms(com):
    '''
    Flattens committee data
    '''
    return {
        'comcode': com['@comcode'],
        'comtype': com['@type'],
        'comname': com['committee-fullname'],
        'majority': com['ratio']['majority'],
        'minority': com['ratio']['minority'],
        'building': com['@com-building-code'],
        'room': com['@com-room'],
        'phone': com['@com-phone']
    }


def parse_subcoms(com):
    '''
    Flattens subcommittee data
    '''
    if 'subcommittee' in com.keys():
        subs = com['subcommittee']
        for s in subs:
            if isinstance(s, dict):
                return {
                    'subcode': s['@subcomcode'],
                    'subcomname': s['subcommittee-fullname'],
                    'parent_com': com['committee-fullname'],
                    'parent_com_code': com['@comcode'],
                    'building': s['@subcom-building-code'],
                    'room': s['@subcom-room'],
                    'phone': s['@subcom-phone'],
                    'majority': s['ratio']['majority'],
                    'minority':  s['ratio']['minority']
                }


def writer(csvs, key):
    '''
    Writes list of dictionaries to a csv
    '''
    with open(f"./{key}", "w", encoding="utf-8", newline='') as outfile:
        headers = csvs[key][0].keys()
        dict_writer = csv.DictWriter(outfile, headers)
        dict_writer.writeheader()
        dict_writer.writerows(csvs[key])


if __name__ == "__main__":
    main()
