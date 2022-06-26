import scrapetools as sc

print("IndeedExpress - job posting scraper")
scrapedjobs=[]
scrapedjobs=sc.scrape_indeed(scrapedjobs)

if scrapedjobs:
    sc.export_scrape(scrapedjobs)
    print("All done!")
else:
    print("Nothing to export!")
