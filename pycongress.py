"""
Retrieve data on U.S. House of Representatives and Senate members.
"""
import csv
from datetime import datetime
import requests
import xmltodict


def main():
    """
    Retrieve latest listing of House members, committees and subcommittees.
    """
    house_url = "http://clerk.house.gov/xml/lists/MemberData.xml"
    sen_url = "https://www.senate.gov/legislative/LIS_MEMBER/cvc_member_data.xml"
    csvs = {
        "house/metadata.csv": [],
        "house/house_members.csv": [],
        "house/house_com_assignments.csv": [],
        "house/house_coms.csv": [],
        "house/house_sub_coms.csv": [],
        "senate/metadata.csv": [],
        "senate/senators.csv": [],
        "senate/senators_com_assignments.csv": [],
    }
    house_data = parse_xml(house_url)
    sen_data = parse_xml(sen_url)
    csvs["house/metadata.csv"].append(parse_metadata(house_data, "house"))
    csvs["house/house_members.csv"] = [
        parse_member(m) for m in house_data["MemberData"]["members"]["member"]
    ]
    csvs["house/house_coms.csv"] = [
        parse_coms(c) for c in house_data["MemberData"]["committees"]["committee"]
    ]
    csvs["senate/metadata.csv"].append(parse_metadata(sen_data, "senate"))
    csvs["senate/senators.csv"] = [
        parse_senator(s) for s in sen_data["senators"]["senator"]
    ]
    csvs["house/house_sub_coms.csv"] = parse_house_subcoms(house_data)
    csvs["senate/senators_com_assignments.csv"] = parse_sen_assign(sen_data)
    csvs["house/house_com_assignments.csv"] = parse_house_assignments(house_data)
    for k in csvs.keys():
        writer(csvs, k)


def parse_xml(url):
    """
    Parse xml
    """
    return xmltodict.parse(requests.get(url).content)


def parse_metadata(data, chamber):
    """
    Flattens file metadata
    """
    if chamber == "house":
        metadata = data["MemberData"]["title-info"]
        metadata["publish-date"] = data["MemberData"]["@publish-date"]
        metadata["data-retrieve-datetime"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    if chamber == "senate":
        metadata = data["senators"]["lastUpdate"]
        metadata["data-retrieve-datetime"] = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    return metadata


def parse_member(member):
    """
    Flattens member data
    """
    mi = member["member-info"]
    return {
        "state_district": member["statedistrict"],
        "bioguide_id": mi["bioguideID"],
        "sortable_name": mi["sort-name"],
        "full_name": mi["namelist"],
        "title": mi["courtesy"],
        "first_name": mi["firstname"],
        "middle_name": mi["middlename"],
        "last_name": mi["lastname"],
        "suffix": mi["suffix"],
        "official_name": mi["official-name"],
        "formal_name": mi["formal-name"],
        "prior_congress": mi["prior-congress"],
        "party": mi["party"],
        "caucus": mi["caucus"],
        "state_code": mi["state"]["@postal-code"],
        "state": mi["state"]["state-fullname"],
        "district": mi["district"],
        "town": mi["townname"],
        "office_building": mi["office-building"],
        "office_room": mi["office-room"],
        "office_zip": mi["office-zip"],
        "office_zip_suffix": mi["office-zip-suffix"],
        "phone": mi["phone"],
        "last_elected_date": mi["elected-date"]["@date"],
        "sworn_date": mi["sworn-date"]["@date"],
    }


def parse_senator(sen):
    """
    Flattens senator data
    """
    return {
        "state": sen["state"],
        "bioguideid": sen["bioguideId"],
        "member_id": sen["@lis_member_id"],
        "first_name": sen["name"]["first"],
        "last_name": sen["name"]["last"],
        "suffix": sen["name"]["suffix"],
        "party": sen["party"],
        "town": sen["homeTown"],
        "office": sen["office"],
        "state_rank": sen["stateRank"],
    }


def parse_coms(com):
    """
    Flattens committee data
    """
    return {
        "comcode": com["@comcode"],
        "comtype": com["@type"],
        "comname": com["committee-fullname"],
        "majority": com["ratio"]["majority"],
        "minority": com["ratio"]["minority"],
        "building": com["@com-building-code"],
        "room": com["@com-room"],
        "phone": com["@com-phone"],
    }


def parse_house_subcoms(data):
    """
    Flattens subcommittee data
    """
    subs = []
    for com in data["MemberData"]["committees"]["committee"]:
        if "subcommittee" in com.keys():
            for s in com["subcommittee"]:
                if isinstance(s, dict):
                    subs.append(
                        {
                            "subcode": s["@subcomcode"],
                            "subcomname": s["subcommittee-fullname"],
                            "parent_com": com["committee-fullname"],
                            "parent_com_code": com["@comcode"],
                            "building": s["@subcom-building-code"],
                            "room": s["@subcom-room"],
                            "phone": s["@subcom-phone"],
                            "majority": s["ratio"]["majority"],
                            "minority": s["ratio"]["minority"],
                        }
                    )
    return subs


def parse_sen_assign(data):
    """
    Flatten Senate committee assignments
    """
    assigns = []
    for sen in data["senators"]["senator"]:
        for d in sen["committees"]["committee"]:
            if "@position" in d.keys():
                position = d["@position"]
            else:
                position = None
            assigns.append(
                {
                    "bioguideid": sen["bioguideId"],
                    "first_name": sen["name"]["first"],
                    "last_name": sen["name"]["last"],
                    "comcode": d["@code"],
                    "comname": d["#text"],
                    "position": position,
                }
            )
    return assigns


def parse_house_assignments(data):
    """
    Flattens House committee assignments
    """
    assigns = []
    for m in data["MemberData"]["members"]["member"]:
        mi = m["member-info"]
        if "committee" in m["committee-assignments"].keys():
            if isinstance(m["committee-assignments"]["committee"], dict):
                com = m["committee-assignments"]["committee"]
                if "@comcode" in com.keys():
                    if "@leadership" in com.keys():
                        leadership = com["@leadership"]
                    else:
                        leadership = None
                    assigns.append(
                        {
                            "state_district": m["statedistrict"],
                            "bioguide_id": mi["bioguideID"],
                            "sortable_name": mi["sort-name"],
                            "comtype": "committee",
                            "comcode": com["@comcode"],
                            "comrank": com["@rank"],
                            "leadership": leadership,
                        }
                    )
            else:
                for com in m["committee-assignments"]["committee"]:
                    if "@leadership" in com.keys():
                        leadership = com["@leadership"]
                    else:
                        leadership = None
                    assigns.append(
                        {
                            "state_district": m["statedistrict"],
                            "bioguide_id": mi["bioguideID"],
                            "sortable_name": mi["sort-name"],
                            "comtype": "committee",
                            "comcode": com["@comcode"],
                            "comrank": com["@rank"],
                            "leadership": leadership,
                        }
                    )
        if "subcommittee" in m["committee-assignments"].keys():
            if isinstance(m["committee-assignments"]["subcommittee"], dict):
                scom = m["committee-assignments"]["subcommittee"]
                if "@leadership" in scom.keys():
                    leadership = scom["@leadership"]
                else:
                    leadership = None
                assigns.append(
                    {
                        "state_district": m["statedistrict"],
                        "bioguide_id": mi["bioguideID"],
                        "sortable_name": mi["sort-name"],
                        "comtype": "subcommittee",
                        "comcode": scom["@subcomcode"],
                        "comrank": scom["@rank"],
                        "leadership": leadership,
                    }
                )
            else:
                for scom in m["committee-assignments"]["subcommittee"]:
                    if "@leadership" in scom.keys():
                        leadership = scom["@leadership"]
                    else:
                        leadership = None
                    assigns.append(
                        {
                            "state_district": m["statedistrict"],
                            "bioguide_id": mi["bioguideID"],
                            "sortable_name": mi["sort-name"],
                            "comtype": "subcommittee",
                            "comcode": scom["@subcomcode"],
                            "comrank": scom["@rank"],
                            "leadership": leadership,
                        }
                    )
    return assigns


def writer(csvs, key):
    """
    Writes list of dictionaries to a csv
    """
    with open(f"./{key}", "w", encoding="utf-8", newline="") as outfile:
        headers = csvs[key][0].keys()
        dict_writer = csv.DictWriter(outfile, headers)
        dict_writer.writeheader()
        dict_writer.writerows(csvs[key])


if __name__ == "__main__":
    main()
