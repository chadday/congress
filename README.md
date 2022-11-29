# congress

A repo to house some standard code and files containg public information about the U.S. Congress

```pycongress.py``` parses XML files from the [House](http://clerk.house.gov/member_info/) and [Senate](https://www.senate.gov/general/common/generic/XML_Availability.htm). 


## Installation

```pip3 install -r requirements.txt```


## Usage

Get fresh House and Senate listings
```
python pycongress.py
```

CSV files will appear in `/senate` and `/house`.

