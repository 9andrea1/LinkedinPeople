# LinkedinPeople
Fetch people names and roles starting from company name.
Optionally generate dictionary files and download pdf profiles 

## Usage
```shell
root@kali:~/script/search/LinkedinPeople# python LinkedinPeople.py --help
usage: LinkedinPeople.py [-h] [-e EMAIL] [-p PASSWORD] [-s SEARCH] [-w] [-d]

Linkedin Company People Harvester

optional arguments:
  -h, --help            show this help message and exit
  -e EMAIL, --email EMAIL
                        Linkedin email
  -p PASSWORD, --password PASSWORD
                        Linkedin password
  -s SEARCH, --search SEARCH
                        Linkedin search string
  -w, --pdf             Write harvested profile to pdf
  -d, --dict            Write dictionaries
  ```
