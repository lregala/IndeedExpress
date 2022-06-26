import os
import re
import time
import random
import requests
import pandas as pd
import tkinter as tk
import urllib.parse

from tkinter import filedialog
from datetime import datetime
from bs4 import BeautifulSoup

class jobrecord:
    def __init__(self,rec):
        self.index = rec[0]
        self.id = rec[1]
        self.url = rec[2]
        self.title = rec[3]
        self.company = rec[4]
        self.loc = rec[5]
        self.desc = rec[6]
    def summarize(self):
        tempstr = f"{self.title}   {self.company}"
        print(tempstr)

    def to_dict(self):
        return {
            'index': self.index,
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'company': self.company,
            'loc': self.loc,
            'desc': self.desc
        }

class jobsearch:
    def __init__(self,title,loc,base_url,navlink=""):
        self.title = title.strip()
        self.loc = loc.strip()
        self.base_url = base_url
        self.navlink = navlink

    def generate_navlink(self):
        enc_title = urllib.parse.quote(self.title)
        enc_loc = urllib.parse.quote(self.loc)
        self.navlink = self.base_url + enc_title + "&l=" + enc_loc
        return self.navlink

def get_date_as_str():
    today = datetime.now()
    str_dt = today.strftime('%m%d%Y-%H%M')
    return str_dt

def raise_above_all(window,mode):
    if mode==1:
        window.attributes('-topmost', 1)
    else:
        window.attributes('-topmost', 0)

def get_nav(regexp,pg):
    temp = re.search(regexp, str(pg))
    temp = (temp.group(0)).split('"')
    temp = temp[0]
    return temp

def navigate(nav):
    nlink = ""
    base_url = "https://ca.indeed.com"
    for btns in nav.find_all("span", class_="np"):
        np = (btns.parent).parent


        nav_text = get_nav('(?<=aria-label=").*', np)
        if nav_text != "Next":
            continue
        else:
            nlink = base_url + get_nav('(?<=href=").*', np)


    return nlink

def print_msg(mode,**kwargs):
    if mode == 'h':
        print(f"Page: {kwargs.get('p')}    {kwargs.get('n')}")
        header_str = '''n     wait_time (s)       job_ID                                  job_URL  \
                                        job_title                       company         location'''
        print(header_str)
    elif mode == 'f':
        print("***End of Page***")
        print(f"Total time: {kwargs.get('t')} sec.")
    elif mode == 'b':
        sc = kwargs.get('sc')
        print(f"{sc[0]}       {sc[1]} s       {sc[2]}        {sc[3]}       {sc[4]}     {sc[5]}       {sc[6]}")
    else:
        print(f"Scraping complete. {kwargs.get('j')} job(s) will be exported. Awaiting confirmation...")

def scrape_indeed(scrapedjobs):
    base_url = "https://ca.indeed.com/jobs?q="
    searchjob = jobsearch(input("Job title: "), input("Location: "), base_url)
    nav_link = searchjob.generate_navlink()
    print(nav_link)
    page = 1
    total_time = 0
    jcount = 0
    try:
        while nav_link:
            source = requests.get(nav_link).text
            soup = BeautifulSoup(source, 'lxml')
            counter = 0

            print_msg('h',p=page,n=nav_link)
            for jobs in soup.find_all('td', class_='resultContent'):
                counter += 1
                jcount +=1
                jobparam = jobs.find('h2', class_='jobTitle').a

                job_title = jobparam.text
                company = jobs.find('span', class_='companyName').text
                location = jobs.find('div', class_='companyLocation').text

                tag = re.search("(?<=jobTitle-).*", str(jobparam))
                job_ID = (tag.group(0))[0:16]

                prefix_str = "https://ca.indeed.com/viewjob?jk="
                job_URL = prefix_str + job_ID

                rand_time = random.uniform(0, 3)
                wait_time = round(2 + rand_time, 2)
                time.sleep(wait_time)
                total_time += wait_time
                subsource = requests.get(job_URL).text
                subsoup = BeautifulSoup(subsource, 'lxml')
                job_desc = (subsoup.find('div', class_='jobsearch-jobDescriptionText').text).replace("\n", "")

                scr_arr = [counter,wait_time,job_ID,job_URL,job_title,company,location]
                print_msg('b', sc=scr_arr)

                out_arr = [jcount, job_ID, job_URL, job_title, company, location, job_desc]
                scrapedjobs.append(jobrecord(out_arr))

            nav = soup.find("ul", class_="pagination-list")

            nav_link = navigate(nav)
            nav_link = nav_link.replace("+", "%20")
            nav_link = nav_link.replace("&amp;", "&")
            page += 1

    except:
        print_msg('f',t=total_time)
    finally:
        print_msg('n', j=jcount)
        return scrapedjobs

def export_scrape(scrapedjobs):
    df = pd.DataFrame([t.to_dict() for t in scrapedjobs])
    df.columns = ['index', 'ID', 'URL', 'Title', 'Company', 'Location', 'Job Description']

    strdate = get_date_as_str()

    default_fname = "scrape_results-" + strdate + ".xlsx"
    desktop = os.path.expanduser("~/Downloads")

    root = tk.Tk()
    try:
        # with block automatically closes file
        root.overrideredirect(True)
        root.attributes("-alpha", 0)
        root.lift()
        raise_above_all(root,1)
        with filedialog.asksaveasfile(mode='w', defaultextension=".xlsx", initialfile=default_fname,
                                      initialdir=desktop) as file:
            df.to_excel(file.name,index=False)

    except AttributeError:
        # if user cancels save, filedialog returns None rather than a file object, and the 'with' will raise an error
        print("User cancelled save!")

    root.destroy()  # close the dialogue box




