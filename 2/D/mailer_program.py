"""
Run this with
python3 mailer_program.py [maildata.csv] [dept code]

CSV file should contain header, and columns are to be in the format [email] [name] [department]
"""

import csv
import sys
import time

from smtplib import SMTP

# save a hash of dept: {email: name}
dept_roster = {}

class InvalidDeptException(Exception):
    def __init__(self):
        self.msg = ("Invalid Department! Please try again.")
        super(Exception, self).__init__(self.msg)

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

def edit(to_send, name):
    with open(to_send, "r+") as content:
        pass

# dept provided here is already verified to be valid
def mail_to(dept, to_send):
    if dept == "all":
        for dept in dept_roster:
            mail_to(dept)
    else:
        counter = 0

        dept_emails = dept_roster[dept]

        print("Mailing to department: " + dept)

        for email in dept_emails:
            # with SMTP(host) as smtp:  # smtp quits automatically

            name = dept_roster[dept][email]

            edited_to_send = edit(to_send, name)

            print("Sending to " + name + "...")

            counter += 1

        # send summary
        end = time.time()
        print(str(counter) + " mail(s) sent \n")

def check_dept():
    # keep looping until user gets it right
    while True:
        try:
            dept = input("Please enter the department code: ").lower()

            start = time.time()

            if dept == "all":
                to_send = input("Please provide the absolute address of your email text file: ")

                print("\nMailing to all")

                mail_to("all", to_send)

                print("Total time taken: " + '%.3f' % ((time.time() - start) * 10 ** 3) + "ms\n")
                break
            else:
                if dept in dept_roster:
                    to_send = input("Please provide the absolute address of your email text file: ")

                    mail_to(dept, to_send)

                    print("Total time taken: " + '%.3f' % ((time.time() - start) * 10 ** 3) + "ms\n")
                    break
                else:
                    raise InvalidDeptException

        except InvalidDeptException as ex1:
            print(ex1.msg)

maildata = sys.argv[1]
# excess args ignored

maildata_rows = read_csv(maildata)

# assumes csv contains header
maildata_entries = maildata_rows[1:]

for entry in maildata_entries:
    email, name, dept = entry
    dept = dept.lower() # case insensitive
    if dept not in dept_roster:
        dept_roster[dept] = {email: name}
    else:
        if email not in dept_roster[dept]:
            dept_roster[dept][email] = name
        # ignore duplicate email, saves the earlier entry

# print(dept_roster)

if dept_roster:
    print("Department Roster successfully populated!\n")
else:
    print("Department Roster Unsuccessful :(\n")

# ask for dept code and verify
check_dept()