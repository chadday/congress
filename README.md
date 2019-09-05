# congress

A repo to house some standard code and files containg public information about the U.S. Congress


```house.py``` parses xml files containing the details on each House of Representatives member. The files are located [here](http://clerk.house.gov/member_info/).

```senate.py``` parses xml files containing the details of each Senator. The files are located [here](https://www.senate.gov/general/common/generic/XML_Availability.htm).

Each folder contains csvs of information on the House and Senate members and committees. I'll be adding more as needed. These are meant to serve as quick resources since we use them so often.

## Installation

See ```requirements.txt```

## Usage

Get fresh House listings
```
python house.py /path/to/output/files
```

Get fresh Senate listings
```
python senate.py /path/to/output/files
```

