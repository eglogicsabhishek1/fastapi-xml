import xml.etree.ElementTree as ET
from faker import Faker
import random
from uuid import uuid4
from datetime import datetime
import sys

# Initialize faker with Swiss German locale
fake = Faker('de_CH')

def create_fake_job():
    job = ET.Element("job")

    guid = str(uuid4().int >> 64)
    url = f"https://ch.jooble.org/external/{guid}?cpc=d0FVdlZFWw%3D%3D&utm_source=affiliate"
    title = f"{fake.job()} ({fake.random_element(elements=['m/w/d'])})"
    company = fake.company()
    city = fake.city()
    state = f"{city}; {fake.canton()}"
    date_updated = datetime.now().strftime("%Y-%m-%d 00:00:00")
    cpc = round(random.uniform(0.05, 0.15), 5)

    def cdata(text):
        return f"<![CDATA[{text}]]>"

    def sub_elem(parent, tag, text=""):
        e = ET.SubElement(parent, tag)
        e.text = cdata(text)
        return e

    # Build job XML
    sub_elem(job, "guid", guid)
    sub_elem(job, "referencenumber", guid)
    sub_elem(job, "url", url)
    sub_elem(job, "title", title)

    region = ET.SubElement(job, "region")
    sub_elem(region, "country", "CH")
    sub_elem(region, "state", state)
    sub_elem(region, "city", city)

    sub_elem(job, "date_updated", date_updated)
    sub_elem(job, "cpc", str(cpc))
    sub_elem(job, "currency", "CHF")
    sub_elem(job, "company", company)
    sub_elem(job, "date_expired")
    sub_elem(job, "jobtype")

    salary = ET.SubElement(job, "salary")
    sub_elem(salary, "min")
    sub_elem(salary, "max")
    sub_elem(salary, "currency")
    sub_elem(salary, "rate")

    description = (
        f"<p>{company} sucht aktuell neue Mitarbeiter für Positionen wie:</p>"
        f"<h2>{title}</h2><p>Ort: {city} / Teilzeit / Flexibel</p>"
    )
    sub_elem(job, "description", description)

    return job

def main():
    # Allow number of jobs to be passed from command line
    num_jobs = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    jobs_root = ET.Element("jobs")
    for _ in range(num_jobs):
        jobs_root.append(create_fake_job())

    tree = ET.ElementTree(jobs_root)
    ET.indent(tree, space="    ", level=0)

    # Dynamic file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"output_{timestamp}.xml"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(ET.tostring(jobs_root, encoding="utf-8", xml_declaration=True).decode("utf-8"))

    print(f"XML file '{filename}' created successfully with {num_jobs} job(s).")

if __name__ == "__main__":
    main()
    