# LinkedinPeople 
Fetch people names and roles starting from company name or company id.
Use hunter.io search to get company email pattern and create the resulting table
Optionally generate company usernames dictionary files and csv file 

## Usage
```shell
root@kali:~/script/search/LinkedinPeople# python LinkedinPeople.py -h
usage: LinkedinPeople.py [-h] [-e EMAIL] [-p PASSWORD] [-s SEARCH] [-d DOMAIN]
                         [--dict] [--csv] [--company-id COMPANYID]
                         [--api-key API_KEY]

Linkedin Company People Harvester

optional arguments:
  -h, --help            show this help message and exit
  -e EMAIL, --email EMAIL
                        Linkedin email
  -p PASSWORD, --password PASSWORD
                        Linkedin password
  -s SEARCH, --search SEARCH
                        Linkedin search string
  -d DOMAIN, --domain DOMAIN
                        Email domain
  --dict                Write usernames dictionaries
  --csv                 Write search output to csv file
  --company-id COMPANYID
                        Company ID number
  --api-key API_KEY     Hunter api key
  ```
