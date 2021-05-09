from extraction import Parser
import csv
import os

SRC_DIR = "PATH"
CSV_FILE = "receipt.csv"

COLUMNS = ['Market', 'Date', 'Item', 'Price']

os.system("python scan.py --images input")

parser = Parser()
record = []

for filename in os.listdir(SRC_DIR): 
    if filename.endswith(".jpg") or filename.endswith(".png"):
        parser.parse_receipt(os.path.join(SRC_DIR, filename), record)
    else:
        continue

try: 
    with open(CSV_FILE, 'w') as CSVFILE: 
        writer = csv.DictWriter(CSVFILE, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(record)
    print("Done!")
except IOError: 
    print("I/O Error when writing to CSV file.")
