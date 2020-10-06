"""
Run this with
python mailer_program.py [maildata.csv] [dept code]
"""

import csv
import sys

from smtplib import SMTP

def read_csv(csvfilename):
    """
    Reads a csv file and returns a list of list
    containing rows in the csv file and its entries.
    """
    rows = []

    with open(csvfilename) as csvfile:
        file_reader = csv.reader(csvfile)
        for row in file_reader:
            rows.append(row)
    return rows

def mail(host):
    with SMTP(host) as smtp:  # smtp quits automatically
        # send to host

maildata = sys.argv[1]
dept_code = sys.argv[2]

maildata_rows = read_csv(maildata)

# assumes csv contains header
maildata_entries = maildata_rows[1:]

for data in maildata_entries:
    name, email, dept = data
    mail(email)

