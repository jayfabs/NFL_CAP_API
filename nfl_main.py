from splinter import Browser
from bs4 import BeautifulSoup as soup
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import csv
import sqlite3


#create the chromedriver connection
browser = Browser('chrome')

#specify the webiste and use BeautifulSoup to create the Parser
teams_url = 'https://www.spotrac.com/nfl/cap/'
browser.visit(teams_url)
html1 = browser.html
soup = soup(html1, 'html.parser')

#loop through and replace all the 'span'elemnts as they create double strings later on
for span_tag in soup.find_all('span', style='display:none'):
    span_tag.replace_with('')

#Create a list for the end syntax of each url so we can loop through specific teams
url_end = []
#delete the leauge average row
for average in soup.find_all('tr', class_='average'):
        average.extract()
#Loop through extract team names and formate to match urls ending format
for team in soup.find_all('span', class_='xs-hide'):
    format = team.string.replace(" ", "-")+'/cap/'
    url_end.append(format)

#Create list of team names that we will use for the table_names of each teams data
table_names = []
for average in soup.find_all('tr', class_='average'):
        average.extract()
for team2 in soup.find_all('span', class_='xs-hide'):
    format2 = team2.string.replace(" ", "_")
    table_names.append(format2)

#scrape the website to find elements within the table
cap = soup.find_all('td')

#create the distribution by looping through the element
distribution1 = [value.text.strip() for value in cap]

#Print only the team names and not the \n abrreviation
distribution1 = [s.split('\n')[0] for s in distribution1]

#Create column names for our data
column_names = [
    "Team_id"
    "Teams", 
    "Position", 
    "Signed", 
    "Avg_Age", 
    "Active", 
    "Dead_Cap", 
    "Top_51_Cap", 
    "Cap_Space_(Top 51)", 
    "Total_Cap", 
    "Cap_Space(All)"
]

#Create Dictionary to store the list data
team_dictionary = {}

team_dictionary["Team_id"] = np.arange(1, len(distribution1[0::][::10])+1)
team_dictionary["Teams"] = distribution1[1::][::10]
team_dictionary["Rank"] = distribution1[0::][::10]
team_dictionary["Signed"] = distribution1[2::][::10]
team_dictionary["Avg_Age"] = distribution1[3::][::10]
team_dictionary["Active"] = distribution1[4::][::10]
team_dictionary["Dead_Cap"] = distribution1[5::][::10]
team_dictionary["Top_51_Cap"] = distribution1[6::][::10]
team_dictionary["Cap_Space_Top_51"] = distribution1[7::][::10]
team_dictionary["Total_Cap"] = distribution1[8::][::10]
team_dictionary["Cap_Space_All"] = distribution1[9::][::10]
    
    
#convert that dictionary to a DataFrame so its easier to manage    
team_df = pd.DataFrame(data=team_dictionary)

#close out of chromedriver browser
browser.quit()

# create a connection to an SQLite database
with sqlite3.connect('sport_caps.db') as con:

# write the dataframe to an SQLite table
    team_df.to_sql('nfl_teams', con=con, if_exists='replace', index=False, dtype={'Team_id': 'INTEGER PRIMARY KEY AUTOINCREMENT'})

con.commit()
# close the database connection
con.close()


# Create the list of urls using the base and endings that we defined ad url_end
full_urls = []
base_url = 'https://www.spotrac.com/nfl/'
for front_url in url_end:
    full_url = (base_url + front_url)
    full_urls.append(full_url)

# empty lists to hold dataframes and counter variables 
dfs = []
player_dfs = []
player_id = 1
team_id = 0


# create a new browser instance
with Browser('chrome') as browser:
    for url in full_urls:
        # visit the URL in the browser
        browser.visit(url)

        # get the HTML content of the page
        html = browser.html

        # parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(html, 'html.parser')

        # extract the data you want and convert it into a dataframe
        for span_tag in soup.find_all('span', style='display:none'):
            span_tag.replace_with('')
        table = soup.find('tbody')
        distribution = [value.text for value in table.find_all('tr', role="row")]
        new_distribution = []
        for s in distribution:
            new_distribution += s.split('\n')
            final_distribution = [item for item in new_distribution if item != '']

        
        
    #Create Dictionary to store the list data
        dictionary = {
            "Team_id": distribution1[0::][::10][team_id],
            "Player_id": np.arange(player_id, player_id+len(final_distribution[0::13])),
            "Active_Players": final_distribution[0::13],
            "Position": final_distribution[1::13],
            "Base_Salary": final_distribution[3::13],
            "Signing_Bonus": final_distribution[4::13],
            "Roster_Bonus": final_distribution[5::13],
            "Option_Bonus": final_distribution[6::13],
            "Workout_Bonus": final_distribution[7::13],
            "Restruc_Bonus": final_distribution[8::13],
            "Misc": final_distribution[9::13],
            "Dead_Cap": final_distribution[10::13],
            "Cap_Hit": final_distribution[2::13],
            "Cap_Percentage": final_distribution[12::13]
        }

        
        
    #Create DataFrame from the dictionary
        df = pd.DataFrame(data=dictionary)
    
    #Append the dataframe to the list
        dfs.append(df)
    
    #For Players Table Create New Dictionary and add the data
        active_players = {
            "Player_id": np.arange(player_id, player_id + len(final_distribution[0::13])),
            "Team_id": distribution1[0::][::10][team_id],
            "Active_Players": final_distribution[0::13],
            "Position": final_distribution[1::13],
            "Base_Salary": final_distribution[3::13],
            "Cap_Hit": final_distribution[2::13],
            "Cap_Percentage": final_distribution[12::13]
        }

    
    #Append the dataframe to the list
        player_df = pd.DataFrame(data=active_players,index=None)
        player_dfs.append(player_df)
    #Increment the player_id and team_id for the next iteration
        player_id = player_id + len(final_distribution[0::][::13])
        team_id = team_id + 1

#Combine the Dataframe into one singular one        
full_player_df = pd.concat(player_dfs)

#close out of chromedriver browser
browser.quit()

# create a connection to the database
# important to create the .db file first in sqlite before running this code as some schema error can occur if not
conn = sqlite3.connect('sport_caps.db')

# iterate over each dataframe and table name, and write each dataframe to the corresponding table
for df, table_name in zip(dfs, table_names):
    df.to_sql(table_name, conn, if_exists='replace', index=False, dtype={'Player_id': 'INTEGER PRIMARY KEY AUTOINCREMENT', 'Team_id': 'INTEGER'})

conn.commit()

# close the database connection
conn.close()

conn = sqlite3.connect('sport_caps.db')

# create player table in nfl_cap database

full_player_df.to_sql('Players', conn, if_exists='replace', index=False, dtype={'Player_id': 'INTEGER PRIMARY KEY AUTOINCREMENT'})

conn.commit()

# close the database connection
conn.close()

print("Congrats!! Database Created!!")