import datetime as dt
import numpy as np
from sqlalchemy import *
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import Table, MetaData
from flask import Flask, jsonify, request


engine = create_engine("sqlite:///Resources/sport_caps.db")

Base = automap_base()
Base.prepare(engine)

Teams = Base.classes.nfl_teams
Players = Base.classes.Players

session = Session(engine)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

from flask import request
def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()
    
@app.route("/")
def welcome():
    return(
        f"Welcome To The Sport Cap API<br/>"
        f"We Currently Offer Cap/Salary #s for Football <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/teams<br/>"
        f"/api/v1.0/players<br/>"
        f"/api/v1.0/teams/name<br/>"
        f"/api/v1.0/players/name<br/>"
        f"<p> /team/'name' should be full name of desired team with '_' in spaces. For example new york giants =  New_York_Giants"
        f"<p> /players/'name' should be full name of player with spaces for example 'Saquon Barkley' "
    )

@app.route("/api/v1.0/teams")
def full_teams():
    results = session.query(
        Teams.Team_id,
        Teams.Teams, 
        Teams.Rank,
        Teams.Signed,
        Teams.Avg_Age,
        Teams.Dead_Cap,
        Teams.Top_51_Cap,
        Teams.Cap_Space_Top_51,
    ).all()

    teams_list = []
    for r in results:
        team_dict = {
            "team_id": r[0],
            "team_name": r[1],
            "rank": r[2],
            "signed": r[3],
            "average_age": r[4],
            "dead_cap": r[5],
            "top_51_cap": r[6],
            "cap_space_left": r[7],
        }
        teams_list.append(team_dict)
    
    
    
    session.close()
    return jsonify(teams_list)

@app.route("/api/v1.0/players")
def full_players():
    results = session.query(
        Players.Player_id, 
        Players.Active_Players,
        Players.Position,
        Players.Team_id,
        Players.Base_Salary,
        Players.Cap_Hit,
        Players.Cap_Percentage,
    ).all()

    player_list = []
    for r in results:
        player_dict = {
            "player_id": r[0],
            "player_name": r[1],
            "position": r[2],
            "team_id": r[3],
            "base_salary": r[4],
            "cap_hit": r[5],
            "cap%": r[6],
        }
        player_list.append(player_dict)
    
    session.close()
    return jsonify(player_list)

@app.route("/api/v1.0/teams/<name>")
def team_names(name=None):
    #generate the table name based on the input
    table_name = f"{name}"

    metadata = MetaData(bind=session.bind)
    table = Table(table_name, metadata, autoload=True)
    # query the table with the generated name
    results = session.query(
        table.c.Team_id,
        table.c.Player_id, 
        table.c.Active_Players,
        table.c.Position,
        table.c.Base_Salary,
        table.c.Signing_Bonus,
        table.c.Roster_Bonus,
        table.c.Option_Bonus,
        table.c.Workout_Bonus,
        table.c.Restruc_Bonus,
        table.c.Misc,
        table.c.Dead_Cap,
        table.c.Cap_Hit,
        table.c.Cap_Percentage,
    ).all()

    teams_list = []
    for r in results:
        team_dict = {
            "team_id": r[0],
            "player_id": r[1],
            "player_name": r[2],
            "position": r[3],
            "base_salary": r[4],
            "signing_bonus": r[5],
            "roster_bonus": r[6],
            "option_bonus": r[7],
            "workout_bonus": r[8],
            "restruc_bonus": r[9],
            "misc": r[10],
            "dead_cap": r[11],
            "cap_hit": r[12],
            "cap%": r[13],

        }
        teams_list.append(team_dict)
    
    
    
    session.close()
    return jsonify(teams_list)

@app.route("/api/v1.0/players/<name>")
def player_names(name=None):
    metadata = MetaData()
    
    Players = Table('Players', metadata, autoload=True, autoload_with=engine)
    # build a select statement to query the Players table
    select_stmt = select([
        Players.c.Player_id,
        Players.c.Team_id,
        Players.c.Active_Players,
        Players.c.Position,
        Players.c.Base_Salary,
        Players.c.Cap_Hit,
        Players.c.Cap_Percentage,
    ]).where(
        Players.c.Active_Players == name,
            
        )
    

    # execute the select statement and fetch the results
    results = session.execute(select_stmt).fetchall()

    # build a list of dictionaries representing each row
    players_list = []
    for r in results:
        player_dict = {
            "player_id": r[0],
            "team_id": r[1],
            "player_name": r[2],
            "position": r[3],
            "base_salary": r[4],
            "cap_hit": r[5],
            "cap%": r[6],
        }
        players_list.append(player_dict)

    session.close()

    # return the list of players as a JSON response
    return jsonify(players_list)

if __name__ == "__main__":
    app.run(debug=True)
