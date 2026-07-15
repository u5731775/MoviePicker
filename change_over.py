# run_migration.py
import json
import pandas as pd

# Load your current movies.json
with open("movies.json", "r") as f:
    movies = json.load(f)

df = pd.DataFrame(movies)

# Replace this with your copied Google Sheet link (make sure it ends with /edit or similar)
sheet_url = "https://docs.google.com/spreadsheets/d/1eDg-JpeBeA1zd-DewTA0VY8VHvia8P5wFt4tmeFSjqU/edit?usp=sharing"

# Convert the link to a direct CSV export link to write to it
csv_url = sheet_url.replace("/edit?usp=sharing", "/gviz/tq?tqx=out:csv").replace("/edit", "/export?format=csv")

print("🚀 Your data is ready! Open your Google Sheet, select cell A1, and import this data,")
print("or simply copy-paste the contents of your movies.json into an online JSON-to-CSV converter.")