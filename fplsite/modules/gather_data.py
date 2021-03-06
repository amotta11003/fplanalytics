#%%
import os
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
from pandas import Series, DataFrame
import time

#%%
# BUILD PLAYER DATAFRAME containing info (first_name, second_name, goals_scored, assists, total_points, minutes, goals_conceded,
    # creativity, threat, bonus, bps, ict_index, clean_sheets, red_cards, yellow_cards, selected_by_percent, now_cost
    # , team_name, position)

def fpl_player_to_csv():
    # SCRAPE "https://fantasy.premierleague.com/player-list" for position data
    chromedriver = "/Users/ajanimotta/Downloads/chromedriver"
    driver = webdriver.Chrome(chromedriver)
    driver.get("https://fantasy.premierleague.com/player-list")
    html = driver.page_source
    soup = BeautifulSoup(html, 'lxml')

    # grab web_name/ position data from tables
    position_data = {}
    counter = 1
    tables = soup.findAll('table', attrs={'class': 'Table-ziussd-1 hOInPp'})
    for table in tables:
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            tds = row.find_all('td')
            web_name = tds[0]
            team = tds[1]
            points = tds[2]
            if 0 < counter < 3:
                position = 'GKP'
            elif 2 < counter < 5:
                position = 'DEF'
            elif 4 < counter < 7:
                position = 'MID'
            else:
                position = 'FWD'
            position_data[(web_name.text, team.text, points.text)] = position
        counter = counter + 1

    # Build dataframe containing info (first_name, second_name, goals_scored, assists, total_points, minutes, goals_conceded,
    # creativity, threat, bonus, bps, ict_index, clean_sheets, red_cards, yellow_cards, selected_by_percent, now_cost
    # , team_name, position)

    f = open("csv/cleaned_players.csv", "r")
    player_stats_df = pd.read_csv(f)
    player_stats_df = player_stats_df[['first_name', 'second_name', 'goals_scored', 'assists', 'total_points', 'minutes',
    'goals_conceded', 'clean_sheets', 'red_cards', 'yellow_cards', 'bonus', 'selected_by_percent', 'now_cost']]

    # Build dataframe containing info (id, team, web_name)
    f1 = open("csv/players_raw.csv", "r")
    raw_player_df = pd.read_csv(f1)
    raw_player_df = raw_player_df[['id', 'team', 'web_name', 'form']]

    #Build dictionary containing info (team, team_name) / (team, team_abbr)
    teams_dict = {
        1: "Arsenal", 2: "Aston Villa", 3: "Bournemouth", 4: "Brighton",
        5: "Burnley", 6: "Chelsea", 7: "Crystal Palace", 8: "Everton",
        9: "Leicester", 10: "Liverpool", 11: "Man City", 12: "Man Utd",
        13: "Newcastle", 14: "Norwich", 15: "Sheffield Utd", 16: "Southampton",
        17: "Spurs", 18: "Watford", 19: "West Ham", 20: "Wolves" 
    }
    abbr_dict = {
        1: "ARS", 2: "AVL", 3: "BOU", 4: "BHA",
        5: "BUR", 6: "CHE", 7: "CRY", 8: "EVE",
        9: "LEI", 10: "LIV", 11: "MCI", 12: "MUN",
        13: "NEW", 14: "NOR", 15: "SHU", 16: "SOU",
        17: "TOT", 18: "WAT", 19: "WHU", 20: "WOL" 
    }
    # JOIN TWO DFs AND ADD POSITION FROM 'data'
    frames = [player_stats_df, raw_player_df]
    player_fpl_df = pd.concat(frames, axis=1)

    # CONVERT 'now_cost' from int64 with no decimals to float64 with decimal
    player_fpl_df['cost'] = player_fpl_df['now_cost'] / 10.0

    player_fpl_df['position'] = 'NONE'
    for i in list(range(0, len(player_fpl_df))):
        web_name = player_fpl_df.at[i, 'web_name']
        team_id = player_fpl_df.at[i, 'team']
        team_name = teams_dict[team_id]
        team_abbr = abbr_dict[team_id]
        points = player_fpl_df.at[i, 'total_points']
        player_fpl_df.at[i, 'team_name'] = team_name
        player_fpl_df.at[i, 'team_abbr'] = team_abbr
        player_fpl_df.at[i, 'position'] = position_data[(web_name, team_name, str(points))]

    player_fpl_df.to_csv('csv/player_fpl.csv', index = False)
#%%
# Build FPL_PLAYER dataframe from fpl_player.csv 
def fpl_player():
    f = open("csv/player_fpl.csv", "r")
    fpl_players_df = pd.read_csv(f)
    fpl_players_df = fpl_players_df[['web_name', 'id', 'goals_scored', 'assists', 'total_points', 'minutes',
    'goals_conceded', 'clean_sheets', 'red_cards', 'yellow_cards', 'selected_by_percent', 'form','cost', 'bonus', 'position', 'team', 'team_name', 'team_abbr']]

    # MAKE 'web_name' column distinct for plotting purposes
    indices = list(np.where(fpl_players_df['web_name'].duplicated(keep=False))[0])
    for i in indices:
        name = fpl_players_df.iloc[i]['web_name']
        team_abbr = fpl_players_df.iloc[i]['team_abbr']
        fpl_players_df.at[i, 'web_name'] = name + ' (' + team_abbr + ')'
    return fpl_players_df

#--------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------




#%%
# BUILD FIXTURE DATAFRAME containing info ('event', 'id', 'stats', 'team_a', 'team_a_difficulty', 'team_a_score', 'team_h', 
# 'team_h_difficulty', 'team_h_score')
def get_fixtures():
    f = open("csv/fixtures.csv", "r")
    fixtures_df = pd.read_csv(f)
    abbr_dict = {
        1: "ARS", 2: "AVL", 3: "BOU", 4: "BHA",
        5: "BUR", 6: "CHE", 7: "CRY", 8: "EVE",
        9: "LEI", 10: "LIV", 11: "MCI", 12: "MUN",
        13: "NEW", 14: "NOR", 15: "SHU", 16: "SOU",
        17: "TOT", 18: "WAT", 19: "WHU", 20: "WOL" 
    }
    fixtures_df = fixtures_df[['event', 'finished', 'id', 'stats', 'team_h', 'team_h_difficulty', 'team_h_score',
    'team_a', 'team_a_difficulty', 'team_a_score']]
    fixtures_df['home_team_name'] = fixtures_df['team_h'].map(abbr_dict)
    fixtures_df['away_team_name'] = fixtures_df['team_a'].map(abbr_dict)
    return fixtures_df

# Add team rating to fixture dataframe to assess strength of teams throughout season
def team_rating(fixtures):
    temp_df = fixtures.loc[fixtures['finished'] == True]
    team_rating_df = pd.DataFrame()
    for row in temp_df.iterrows():
        row = row[1]
        team_rating_df = team_rating_df.append({
            'GW': row['event'],
            'team': row['team_h'],
            'opponent': row['team_a'],
            'team_name': row['home_team_name'],
            'opponent_name': row['away_team_name'],
            'GF': row['team_h_score'],
            'GA': row['team_a_score'],
            'was_home': 1,
            }, ignore_index=True)
        team_rating_df = team_rating_df.append({
            'GW': row['event'],
            'team': row['team_a'],
            'opponent': row['team_h'],
            'team_name': row['away_team_name'],
            'opponent_name': row['home_team_name'],
            'GF': row['team_a_score'],
            'GA': row['team_h_score'],
            'was_home': 0,
            }, ignore_index=True)
    def get_pts_won(x):
        if x['GF'] > x['GA']:
            return 3
        elif x['GF'] < x['GA']:
            return 0 
        else:
            return 1

    team_rating_df['pts_won'] = team_rating_df.apply(lambda x : get_pts_won(x), axis=1)
    team_rating_df['GA'] = team_rating_df.GA.astype(int)
    team_rating_df['GF'] = team_rating_df.GF.astype(int)
    team_rating_df['GW'] = team_rating_df.GW.astype(int)
    team_rating_df['opponent'] = team_rating_df.opponent.astype(int)
    team_rating_df['team'] = team_rating_df.team.astype(int)
    team_rating_df['was_home'] = team_rating_df.was_home.astype(int)
    team_rating_df = team_rating_df.sort_values(['team', 'GW'], ascending=[True, True])
    team_rating_df['pts_total'] = team_rating_df['pts_won']

    #ADD 'pts_total' column to dataframe
    helper_pts_total = []
    groups = team_rating_df.groupby(['team'])
    for group in groups:
        group[1]['pts_total'] = group[1]['pts_won'].cumsum()
        group[1]['GF'] = group[1]['GF'].cumsum()
        group[1]['GA'] = group[1]['GA'].cumsum()
        helper_pts_total.append(group[1])
    team_fixtures_df = pd.DataFrame()
    for team in helper_pts_total:
        team_fixtures_df = pd.concat([team_fixtures_df, team])
    team_fixtures_df['rating'] = team_fixtures_df['pts_total'] + team_fixtures_df['GF'] - team_fixtures_df['GA']

    #Add standardized rating to dataframe
    agg_df = team_fixtures_df.groupby('GW')
    helper_rating = []
    for group in agg_df:
        group[1]['rating_standardized'] = (group[1]['rating']- group[1]['rating'].mean()) / group[1]['rating'].std()
        helper_rating.append(group[1])
    final_team_fixtures_df = pd.DataFrame()
    for team in helper_rating:
        final_team_fixtures_df = pd.concat([final_team_fixtures_df, team])

    #Bin teams by rating (add bin to df_column 'binned_rating')
    def bin_rating(score):
        if score <= -1.0:
            return 1
        elif score <= -0.5:
            return 2
        elif score <= 0:
            return 3
        elif score <= 0.5:
            return 4
        elif score <= 1:
            return 5
        else:
            return 6
    final_team_fixtures_df['binned_rating'] = final_team_fixtures_df['rating_standardized'].apply(lambda x : bin_rating(x))
    
    final_team_fixtures_df.to_csv('csv/team_ratings.csv', index = False)

    return final_team_fixtures_df

# Read team_ratings.csv --> return team_ratings df (to reduce computation at runtime)
def get_team_ratings():
    f = open("csv/team_ratings.csv", "r")
    ratings_df = pd.read_csv(f)
    return ratings_df
#--------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------



#%%
# BUILD GAMEWEEK DATAFRAME containing info ('name', 'id', 'assists', 'bonus', 'bps', 'clean_sheets', 'fixture', 
# 'goals_conceded', 'goals_scored', 'minutes', 'opponent_team', 'saves', 'team_a_score', 'team_h_score', 
# 'total_points', 'was_home', 'GW', 'web_name', 'position')
def get_gws():
    player_fpl_df = fpl_player()
    f = open("csv/merged_gw.csv", "r")
    gws_df = pd.read_csv(f)
    gws_df = gws_df[['name', 'element', 'assists', 'bonus', 'bps', 'clean_sheets', 'fixture', 'goals_conceded', 'goals_scored', 
    'minutes', 'opponent_team', 'saves', 'team_a_score', 'team_h_score', 'value', 'transfers_balance', 'total_points', 'was_home', 'GW']]

    #Create 'web_name' column by matching ids in player_fpl_df
    gws_df['element'] = gws_df['element'].apply(lambda x: int(x))
    ids = pd.Series(gws_df['element'])
    name_dict = {}
    for i in range(0, len(ids)):
        player_name = player_fpl_df.loc[player_fpl_df['id'] == ids[i]]['web_name'].values
        name_dict[ids[i]] = player_name[0]
    gws_df['web_name'] = gws_df['element'].map(name_dict)

    # Create 'position' column by grabbing row in player_fpl_df with corresponding id
    position_dict = {}
    for i in range(0, len(gws_df)):
        player_id = gws_df.at[i, 'element']
        player_position = player_fpl_df.loc[player_fpl_df['id'] == player_id]['position'].values
        position_dict[player_id] = player_position[0]
    gws_df['position'] = gws_df['element'].map(position_dict)
    
    gws_df = gws_df.rename(columns={"element": "id"})
    return gws_df

#GENERATE CSV FOR GKP HOME/AWAY PLOT
def gkps_home_away_csv():
    players = fpl_player()
    players_gkp = players.loc[players['position'] == 'GKP']

    #GKP----------------------------------------------------------------------------------------------------------
    #home--get subsets of GW dataframe and format dataframe accordingly
    gws = get_gws()
    gws_home = gws.loc[gws['was_home'] == 1]
    gws_home = gws_home.loc[gws['position'] == 'GKP']
    gws_home = gws_home[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_home = gws_home.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_home = gws_by_player_home.reset_index()
    gws_by_player_home['id'] = gws_by_player_home.id.astype(int)
    players_gkp_home = players_gkp[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_home = pd.merge(gws_by_player_home, players_gkp_home, on='id', how='left')
    gws_by_player_home = gws_by_player_home[gws_by_player_home['minutes'] > ((1/2)* 90.0)]
    gws_by_player_home = gws_by_player_home.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    #away--get subsets of GW dataframe and format dataframe accordingly
    gws_away = gws.loc[gws['was_home'] == 0]
    gws_away = gws_away.loc[gws['position'] == 'GKP']
    gws_away = gws_away[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_away = gws_away.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_away = gws_by_player_away.reset_index()
    gws_by_player_away['id'] = gws_by_player_away.id.astype(int)
    players_gkp_away = players_gkp[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_away = pd.merge(gws_by_player_away, players_gkp_away, on='id', how='left')
    gws_by_player_away = gws_by_player_away[gws_by_player_away['minutes'] > ((1/2)* 90.0)]
    gws_by_player_away = gws_by_player_away.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    def color(c):
        if c < 4.5:
            return ["darkgreen", "Less than 4.5"]
        elif c < 5.0:
            return ["lime", "4.5 to 4.9"]
        elif c < 5.5:
            return ["gold", "5.0 to 5.4"]
        elif c < 6.0:
            return ["orange", "5.5 to 5.9"]
        else: return ["red", "6.0 and over"]
    
    gws_by_player_home["color"] = gws_by_player_home["cost"].apply(lambda c: color(c)[0])
    gws_by_player_home["range"] = gws_by_player_home["cost"].apply(lambda c: color(c)[1])
    gws_by_player_home["cost"] = gws_by_player_home["cost"].apply(lambda c: round(c, 1))
    gws_by_player_away["color"] = gws_by_player_away["cost"].apply(lambda c: color(c)[0])
    gws_by_player_away["range"] = gws_by_player_away["cost"].apply(lambda c: color(c)[1])
    gws_by_player_away["cost"] = gws_by_player_away["cost"].apply(lambda c: round(c, 1))

    gws_by_player_home.to_csv('csv/gkps_home.csv', index = False)
    gws_by_player_away.to_csv('csv/gkps_away.csv', index = False)
    return 

#GRAB GKP DF needed for home/away plot on gkps.html
def get_gkps_home_away():
    f_home = open('csv/gkps_home.csv')
    gkps_home = pd.read_csv(f_home)
    f_away = open('csv/gkps_away.csv')
    gkps_away = pd.read_csv(f_away)

    return [gkps_home, gkps_away]

#GENERATE CSV FOR DEF HOME/AWAY PLOT
def defs_home_away_csv():
    players = fpl_player()
    players_def = players.loc[players['position'] == 'DEF']

    #home--get subsets of GW dataframe and format dataframe accordingly
    gws = get_gws()
    gws_home = gws.loc[gws['was_home'] == 1]
    gws_home = gws_home.loc[gws['position'] == 'DEF']
    gws_home = gws_home[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_home = gws_home.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_home = gws_by_player_home.reset_index()
    gws_by_player_home['id'] = gws_by_player_home.id.astype(int)
    players_def_home = players_def[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_home = pd.merge(gws_by_player_home, players_def_home, on='id', how='left')
    gws_by_player_home = gws_by_player_home[gws_by_player_home['minutes'] > ((1/2)* 90.0)]
    gws_by_player_home = gws_by_player_home.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    #away--get subsets of GW dataframe and format dataframe accordingly
    gws_away = gws.loc[gws['was_home'] == 0]
    gws_away = gws_away.loc[gws['position'] == 'DEF']
    gws_away = gws_away[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_away = gws_away.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_away = gws_by_player_away.reset_index()
    gws_by_player_away['id'] = gws_by_player_away.id.astype(int)
    players_def_away = players_def[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_away = pd.merge(gws_by_player_away, players_def_away, on='id', how='left')
    gws_by_player_away = gws_by_player_away[gws_by_player_away['minutes'] > ((1/2)* 90.0)]
    gws_by_player_away = gws_by_player_away.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    def color(c):
        if c < 4.3:
            return ["darkgreen", "Less than 4.3"]
        elif c < 4.8:
            return ["green", "4.3 to 4.7"]
        elif c < 5.3:
            return ["greenyellow", "4.8 to 5.2"]
        elif c < 5.8:
            return ["gold", "5.3 to 5.7"]
        elif c < 6.3:
            return ["orange", "5.8 to 6.2"]
        elif c < 6.8:
            return ["darkorange", "6.3 to 6.7"]
        elif c < 7.3:
            return ["orangered", "6.8 to 7.2"]
        else: return ["red", "7.3 and over"]
    
    gws_by_player_home["color"] = gws_by_player_home["cost"].apply(lambda c: color(c)[0])
    gws_by_player_home["range"] = gws_by_player_home["cost"].apply(lambda c: color(c)[1])
    gws_by_player_home["cost"] = gws_by_player_home["cost"].apply(lambda c: round(c, 1))
    gws_by_player_away["color"] = gws_by_player_away["cost"].apply(lambda c: color(c)[0])
    gws_by_player_away["range"] = gws_by_player_away["cost"].apply(lambda c: color(c)[1])
    gws_by_player_away["cost"] = gws_by_player_away["cost"].apply(lambda c: round(c, 1))

    gws_by_player_home.to_csv('csv/defs_home.csv', index = False)
    gws_by_player_away.to_csv('csv/defs_away.csv', index = False)
    return

#GRAB DEFS DF needed for home/away plot on defs.html
def get_defs_home_away():
    f_home = open('csv/defs_home.csv')
    defs_home = pd.read_csv(f_home)
    f_away = open('csv/defs_away.csv')
    defs_away = pd.read_csv(f_away)
    return [defs_home, defs_away]

#GENERATE CSV FOR MID HOME/AWAY PLOT
def mids_home_away_csv():
    players = fpl_player()
    players_mid = players.loc[players['position'] == 'MID']

    #home--get subsets of GW dataframe and format dataframe accordingly
    gws = get_gws()
    gws_home = gws.loc[gws['was_home'] == 1]
    gws_home = gws_home.loc[gws['position'] == 'MID']
    gws_home = gws_home[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_home = gws_home.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_home = gws_by_player_home.reset_index()
    gws_by_player_home['id'] = gws_by_player_home.id.astype(int)
    players_mid_home = players_mid[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_home = pd.merge(gws_by_player_home, players_mid_home, on='id', how='left')
    gws_by_player_home = gws_by_player_home[gws_by_player_home['minutes'] > ((1/2)* 90.0)]
    gws_by_player_home = gws_by_player_home.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    #away--get subsets of GW dataframe and format dataframe accordingly
    gws_away = gws.loc[gws['was_home'] == 0]
    gws_away = gws_away.loc[gws['position'] == 'MID']
    gws_away = gws_away[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_away = gws_away.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_away = gws_by_player_away.reset_index()
    gws_by_player_away['id'] = gws_by_player_away.id.astype(int)
    players_mid_away = players_mid[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_away = pd.merge(gws_by_player_away, players_mid_away, on='id', how='left')
    gws_by_player_away = gws_by_player_away[gws_by_player_away['minutes'] > ((1/2)* 90.0)]
    gws_by_player_away = gws_by_player_away.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    def color(c):
        if c < 5.0:
            return ["darkgreen", "Less than 5.0"]
        elif c <6.0:
            return ["green", "5.0 to 5.9"]
        elif c < 7.0:
            return ["lime", "6.0 to 6.9"]
        elif c < 8.0:
            return ["greenyellow", "7.0 to 7.9"]
        elif c < 9.0:
            return ["gold", "8.0 to 8.9"]
        elif c < 10.0:
            return ["orange", "9.0 to 9.9"]
        elif c < 11.0:
            return ["darkorange", "10.0 to 10.9"]
        elif c < 12.0:
            return ["orangered", "11.0 to 11.9"]
        else: return ["red", "12.0 and over"]
    
    gws_by_player_home["color"] = gws_by_player_home["cost"].apply(lambda c: color(c)[0])
    gws_by_player_home["range"] = gws_by_player_home["cost"].apply(lambda c: color(c)[1])
    gws_by_player_home["cost"] = gws_by_player_home["cost"].apply(lambda c: round(c, 1))
    gws_by_player_away["color"] = gws_by_player_away["cost"].apply(lambda c: color(c)[0])
    gws_by_player_away["range"] = gws_by_player_away["cost"].apply(lambda c: color(c)[1])
    gws_by_player_away["cost"] = gws_by_player_away["cost"].apply(lambda c: round(c, 1))

    gws_by_player_home.to_csv('csv/mids_home.csv', index = False)
    gws_by_player_away.to_csv('csv/mids_away.csv', index = False)
    return

#GRAB MIDS DF needed for home/away plot on mids.html
def get_mids_home_away():
    f_home = open('csv/mids_home.csv')
    mids_home = pd.read_csv(f_home)
    f_away = open('csv/mids_away.csv')
    mids_away = pd.read_csv(f_away)
    return [mids_home, mids_away]

#GENERATE CSV FOR FWD HOME/AWAY PLOT
def fwds_home_away_csv():
    players = fpl_player()
    players_fwd = players.loc[players['position'] == 'FWD']

    #home--get subsets of GW dataframe and format dataframe accordingly
    gws = get_gws()
    gws_home = gws.loc[gws['was_home'] == 1]
    gws_home = gws_home.loc[gws['position'] == 'FWD']
    gws_home = gws_home[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_home = gws_home.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_home = gws_by_player_home.reset_index()
    gws_by_player_home['id'] = gws_by_player_home.id.astype(int)
    players_fwd_home = players_fwd[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_home = pd.merge(gws_by_player_home, players_fwd_home, on='id', how='left')
    gws_by_player_home = gws_by_player_home[gws_by_player_home['minutes'] > ((1/2)* 90.0)]
    gws_by_player_home = gws_by_player_home.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    #away--get subsets of GW dataframe and format dataframe accordingly
    gws_away = gws.loc[gws['was_home'] == 0]
    gws_away = gws_away.loc[gws['position'] == 'FWD']
    gws_away = gws_away[['id', 'minutes', 'total_points', 'web_name']]
    gws_by_player_away = gws_away.groupby('web_name')['id', 'minutes','total_points'].mean()
    gws_by_player_away = gws_by_player_away.reset_index()
    gws_by_player_away['id'] = gws_by_player_away.id.astype(int)
    players_fwd_away = players_fwd[['id','team_name', 'cost', 'selected_by_percent']]
    gws_by_player_away = pd.merge(gws_by_player_away, players_fwd_away, on='id', how='left')
    gws_by_player_away = gws_by_player_away[gws_by_player_away['minutes'] > ((1/2)* 90.0)]
    gws_by_player_away = gws_by_player_away.rename(columns={"minutes":"avg_minutes", "total_points":"avg_points"})

    def color(c):
        if c < 5.0:
            return ["darkgreen", "Less than 5.0"]
        elif c <6.0:
            return ["green", "5.0 to 5.9"]
        elif c < 7.0:
            return ["lime", "6.0 to 6.9"]
        elif c < 8.0:
            return ["greenyellow", "7.0 to 7.9"]
        elif c < 9.0:
            return ["gold", "8.0 to 8.9"]
        elif c < 10.0:
            return ["orange", "9.0 to 9.9"]
        elif c < 11.0:
            return ["darkorange", "10.0 to 10.9"]
        elif c < 12.0:
            return ["orangered", "11.0 to 11.9"]
        else: return ["red", "12.0 and over"]
    
    gws_by_player_home["color"] = gws_by_player_home["cost"].apply(lambda c: color(c)[0])
    gws_by_player_home["range"] = gws_by_player_home["cost"].apply(lambda c: color(c)[1])
    gws_by_player_home["cost"] = gws_by_player_home["cost"].apply(lambda c: round(c, 1))
    gws_by_player_away["color"] = gws_by_player_away["cost"].apply(lambda c: color(c)[0])
    gws_by_player_away["range"] = gws_by_player_away["cost"].apply(lambda c: color(c)[1])
    gws_by_player_away["cost"] = gws_by_player_away["cost"].apply(lambda c: round(c, 1))

    gws_by_player_home.to_csv('csv/fwds_home.csv', index = False)
    gws_by_player_away.to_csv('csv/fwds_away.csv', index = False)
    return

#GRAB FWDS DF needed for home/away plot on fwds.html
def get_fwds_home_away():
    f_home = open('csv/fwds_home.csv')
    fwds_home = pd.read_csv(f_home)
    f_away = open('csv/fwds_away.csv')
    fwds_away = pd.read_csv(f_away)
    return [fwds_home, fwds_away]

#GENERATE CSV FOR FORM PLOTS
def form_csv(position):
    gws = get_gws()
    players = fpl_player()
    ratings = get_team_ratings()
    ratings = ratings[['GW', 'team', 'team_name','rating_standardized']]
    current_gw = ratings['GW'].max()

    #IN FORM-------------------------------------------------------------------
    GKPs = players.loc[players['position'] == position]
    GKPs = GKPs[['id', 'selected_by_percent']]
    gws_form_GKP = gws.loc[gws['position']== position]
    gws_form_GKP = gws_form_GKP.loc[gws['GW'].isin([current_gw-2, current_gw-1, current_gw]) ]
    gws_form_GKP = gws_form_GKP[['id', 'web_name', 'GW', 'position', 'minutes', 'opponent_team', 'total_points', 'was_home']]
    gws_form_GKP = pd.merge(GKPs, gws_form_GKP, on='id', how = 'right')
    gws_form_GKP = gws_form_GKP.dropna()
    form_player_avgs = gws_form_GKP.groupby('web_name')['minutes','total_points', 'selected_by_percent'].mean()
    if position == 'GKP':
        top20_form = form_player_avgs.nlargest(5, 'total_points')
    elif position in ['DEF', 'MID']:
        top20_form = form_player_avgs.nlargest(20, 'total_points')
    else:
        top20_form = form_player_avgs.nlargest(15, 'total_points')
    top20_form = top20_form.reset_index()

    #OUT OF FORM-------------------------------------------------------------------
    form_player_avgs = form_player_avgs.loc[form_player_avgs['selected_by_percent'] > 1.5]
    form_player_avgs = form_player_avgs.loc[form_player_avgs['minutes'] > 45]
    if position == 'GKP':
        bot20_form = form_player_avgs.nsmallest(5, 'total_points')
    elif position in ['DEF', 'MID']:
        bot20_form = form_player_avgs.nsmallest(20, 'total_points')
    else:
        bot20_form = form_player_avgs.nsmallest(15, 'total_points')
    bot20_form = bot20_form.reset_index()

    top20_form.to_csv('csv/%s_in_form.csv' % position, index = False)
    bot20_form.to_csv('csv/%s_out_form.csv' % position, index = False)
    return

#GRAB DF needed for form plot on gkps/defs/mids/fwds.html
def get_form(position):
    f_in = open('csv/%s_in_form.csv' % position)
    in_form = pd.read_csv(f_in)
    f_out = open('csv/%s_out_form.csv' % position)
    out_form = pd.read_csv(f_out)

    return [in_form, out_form]



def strong_weak_csv(position):
    #STRONG-------------------------------------------------------------------
    #Generate GW dataframe with opponent team rating column
    gws = get_gws()
    ratings = get_team_ratings()
    ratings = ratings[['GW', 'team', 'team_name','rating_standardized']]
    current_gw = ratings['GW'].max()
    gws_ratings = gws.loc[gws['GW'] < current_gw]
    gws_ratings = gws_ratings[['id', 'web_name', 'GW', 'position', 'minutes', 'opponent_team', 'total_points', 'was_home']]
    gws_ratings = pd.merge(ratings, gws_ratings, left_on = ['team', 'GW'], right_on=['opponent_team', 'GW'], how = 'right')
    gws_ratings = gws_ratings.rename(columns={"team_name": "opponent_name", "rating_standardized": "opp_rating"})
    gws_ratings = gws_ratings.drop(columns = ['team']) 
    gws_strong_def = gws_ratings.loc[gws_ratings['position']== position]
    gws_strong_def = gws_strong_def.loc[gws_strong_def['opp_rating'] > 0.5]
    gws_strong_def = gws_strong_def.loc[gws_strong_def['minutes'] > 0]
    strong_player_avgs = gws_strong_def.groupby("web_name")["id"].count().reset_index(name="games")
    strong_player_avgs = pd.merge(strong_player_avgs, gws_strong_def, on = 'web_name', how = 'left')
    strong_player_avgs = strong_player_avgs.groupby('web_name')['total_points', 'minutes', 'games'].mean()

    #WEAK-------------------------------------------------------------------
    #Generate GW dataframe with opponent team rating column
    gws_weak_def = gws_ratings.loc[gws_ratings['position']== position]
    gws_weak_def = gws_weak_def.loc[gws_weak_def['opp_rating'] < -0.5]
    gws_weak_def = gws_weak_def.loc[gws_weak_def['minutes'] > 0]
    weak_player_avgs = gws_weak_def.groupby("web_name")["id"].count().reset_index(name="games")
    weak_player_avgs = pd.merge(weak_player_avgs, gws_weak_def, on = 'web_name', how = 'left')
    weak_player_avgs = weak_player_avgs.groupby('web_name')['total_points', 'minutes', 'games'].mean()
    if position == 'GKP':
        top20_strong = strong_player_avgs.nlargest(10, 'total_points')
        top20_weak = weak_player_avgs.nlargest(10, 'total_points')
    elif position in ['DEF', 'MID']:
        top20_strong = strong_player_avgs.nlargest(20, 'total_points')
        top20_weak = weak_player_avgs.nlargest(20, 'total_points')
    else:
        top20_strong = strong_player_avgs.nlargest(15, 'total_points')
        top20_weak = weak_player_avgs.nlargest(15, 'total_points')
    top20_strong = top20_strong.reset_index()
    top20_weak = top20_weak.reset_index()

    top20_strong.to_csv('csv/%s_strong.csv' % position, index = False)
    top20_weak.to_csv('csv/%s_weak.csv' % position, index = False)
    return

#GRAB DF needed for strong/weak plot on gkps/defs/mids/fwds.html
def get_strong_weak(position):
    f_strong = open('csv/%s_strong.csv' % position)
    strong = pd.read_csv(f_strong)
    f_weak = open('csv/%s_weak.csv' % position)
    weak = pd.read_csv(f_weak)
    return [strong, weak]

#--------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------






#%%
# Grab advanced player data from whoscored (BY SECTION: 'summary', 'defensive', 'offensive', 'passing') 
# and create corresponding csv
def whoscored_all_players_to_csv(section):
    chromedriver = "/Users/ajanimotta/Downloads/chromedriver"
    driver = webdriver.Chrome(chromedriver)
    driver.get('https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/7811/Stages/17590/PlayerStatistics/England-Premier-League-2019-2020')

    count_dict = {'summary': 0, 'defensive': 1, 'offensive': 1, 'passing': 1}

    section_df = pd.DataFrame()
    time.sleep(3)
    driver.find_element_by_xpath('//*[@id="stage-top-player-stats-options"]').find_element_by_link_text(section.capitalize()).click() 
    time.sleep(3)
    all_players = driver.find_element_by_link_text('All players')
    all_players.click() 
    while True:
        while driver.find_element_by_xpath('//*[@id="statistics-table-%s"]' % section).get_attribute('class') == 'is-updating':  # string formatting on the xpath to change for each section that is iterated over
            time.sleep(1)

        table = driver.find_element_by_xpath('//*[@id="statistics-table-%s"]' % section)  # string formatting on the xpath to change for each section that is iterated over
        table_html = table.get_attribute('innerHTML')
        df = pd.read_html(table_html)[0]
        section_df = pd.concat([section_df, df])
        next_link = driver.find_elements_by_xpath('//*[@id="next"]')[count_dict[section]]  # makes sure it's selecting the correct index of 'next' items 
        if 'disabled' in next_link.get_attribute('class'):
            break
        time.sleep(5)
        next_link.click()
    section_df.to_csv('csv/%s_players.csv' % section, index = False)
    return section_df

#%%
#Create whoscored player stats dataframe containing info () from WHOSCORED csv's
def whoscored_player():
    f_summary = open("csv/summary_players.csv", "r")
    summary_df = pd.read_csv(f_summary)
    summary_df = summary_df[['Player', 'SpG', 'PS%']]

    f_offensive = open("csv/offensive_players.csv", "r")
    offensive_df = pd.read_csv(f_offensive)
    offensive_df = offensive_df[['KeyP', 'Drb']]

    #f_defensive = open("defensive.csv", "r")
    #defensive_df = pd.read_csv(f_defensive)

    f_passing = open("csv/passing_players.csv", "r")
    passing_df = pd.read_csv(f_passing)
    passing_df = passing_df[['AvgP', 'Crosses', 'ThrB']]

    advanced_player_df = pd.concat([summary_df, offensive_df, passing_df], axis=1)

    # Get rid of '-' entries in dataframe
    advanced_player_df.loc[(advanced_player_df['SpG'] == '-'), 'SpG'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['PS%'] == '-'), 'PS%'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['KeyP'] == '-'), 'KeyP'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['Drb'] == '-'), 'Drb'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['AvgP'] == '-'), 'AvgP'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['Crosses'] == '-'), 'Crosses'] = float(0.0)
    advanced_player_df.loc[(advanced_player_df['ThrB'] == '-'), 'ThrB'] = float(0.0)

    # Rid player column of age and position information/add team column
    def rid_team(player_team):
        player_team_arr = player_team.split()
        teams = {
            "Arsenal", "Aston", "Bournemouth", "Brighton",
            "Burnley", "Chelsea", "Crystal", "Everton",
            "Leicester", "Liverpool", "Manchester",
            "Newcastle", "Norwich", "Sheffield", "Southampton",
            "Tottenham", "Watford", "West", "Wolverhampton" 
        }
        for i in range(0, len(player_team_arr)):
            if player_team_arr[i] in teams:
                player = " ".join(player_team_arr[0:i])
                team = " ".join(player_team_arr[i:])
                break
        return [player, team]

    player_team = advanced_player_df['Player'].apply(lambda x: x.split(',')[0])
    advanced_player_df['Player'] = player_team.apply(lambda x: rid_team(x)[0])
    advanced_player_df = advanced_player_df.rename(columns={"Player": "player_name"})
    return advanced_player_df


#Load UNDERSTAT dataframe including ('games', 'goals', 'key_passes', 'xG', 'xA')
def understat_player():
    f1 = open('csv/player_idlist.csv', "r")
    ids_df = pd.read_csv(f1)
    ids_df['player_name'] = ids_df['first_name'] + ' ' + ids_df['second_name']
    f2 = open('csv/understat_player.csv', "r", encoding = 'ISO-8859-1')
    understat_player_df = pd.read_csv(f2)
    understat_player_df = understat_player_df[['player_name', 'games', 'goals', 'key_passes', 'xG', 'xA']]
    understat_player_df = pd.merge(understat_player_df, ids_df, on = 'player_name', how = 'left')

    # ADD FPL PLAYER IDs to understat_player_df (using fpl_id_helper.csv)
    f = open('csv/fpl_id_helper.csv', 'r')
    id_filler_df = pd.read_csv(f)
    id_filler_df = id_filler_df[['player_name', 'id']]  
    understat_player_df = pd.merge(understat_player_df, id_filler_df, on = 'player_name', how = 'left')
    #print(understat_player_df.isnull().sum())
    #print(len(understat_player_df[understat_player_df['id_x'].isnull()]))
    #print(understat_player_df[understat_player_df['id_x'].isnull()])
    understat_player_df['id_x'] = understat_player_df['id_x'].mask(understat_player_df['id_x'].isnull(), understat_player_df['id_y'])
    understat_player_df = understat_player_df.rename(columns={"id_x": "id"})
    understat_player_df['id'] = understat_player_df['id'].apply(lambda x: int(x))
    understat_player_df = understat_player_df.drop(columns = ['id_y', 'first_name', 'second_name'])  
    return understat_player_df

# Merge WHOSCORED AND UNDERSTAT DFs --> output result into advanced_player.csv 
# --> input missing data resulting from discrepancy in 'player_name' USING 'advanced_player_helper.csv'
def merge_advanced_player():
    whoscored_player_df = whoscored_player()
    understat_player_df = understat_player()

    #Maps discrepant player names to match that of whoscored 'player_name' --for clean merging purposes
    discrepant_understat_names = [
        'Rodri', 'Caglar Söyüncü', 'N&#039;Golo Kanté', 'Johann Berg Gudmundsson', 'Nicolas Pepe', 'Jack O&#039;Connell',
        'Tanguy NDombele Alvaro', 'Djibril Sidibe', 'Angelino', 'Ezri Konsa Ngoyo', 'Seamus Coleman', 'Romain Saiss',
        'Alex Oxlade-Chamberlain', 'Eric Garcia', 'Ahmed Elmohamady', 'Kepa', 'Joseph Gomez'
    ]
    discrepant_names_dict = {
        'Rodri': 'Rodrigo', 'Caglar Söyüncü': 'Çaglar Söyüncü', 'N&#039;Golo Kanté': "N'Golo Kanté", 
        'Johann Berg Gudmundsson': 'Johann Gudmundsson', 'Nicolas Pepe': 'Nicolas Pépé', 'Jack O&#039;Connell': "Jack O'Connell",
        'Tanguy NDombele Alvaro': "Tanguy Ndombele", 'Djibril Sidibe': "Djibril Sidibé", 'Angelino': "Angeliño", 
        'Ezri Konsa Ngoyo': "Ezri Konsa", 'Seamus Coleman': "Séamus Coleman", 'Romain Saiss': "Romain Saïss",
        'Alex Oxlade-Chamberlain': "Alex Oxlade Chamberlain", 'Eric Garcia': "Eric García", 
        'Ahmed Elmohamady': "Ahmed El Mohamady", 'Kepa': "Kepa Arrizabalaga", 'Joseph Gomez': "Joe Gomez"
    }
    understat_player_df.loc[understat_player_df.player_name.isin(discrepant_understat_names), 'player_name'] = understat_player_df['player_name'].map(discrepant_names_dict)
    advanced_player_df = pd.merge(understat_player_df, whoscored_player_df, on = 'player_name', how = 'right')
    return advanced_player_df

def get_players():
    players = fpl_player()
    understat_player_df = understat_player()
    players = pd.merge(players, understat_player_df, on= 'id', how = 'inner')
    players['ppg'] = round((players['total_points'] / players['games']), 1)
    players['mpg'] = round((players['minutes'] / players['games']), 1)
    players['gpg'] = round((players['goals_scored'] / players['games']), 1)
    players['gcpg'] = round((players['goals_conceded'] / players['games']), 1)
    players['apg'] = round((players['assists'] / players['games']), 1)
    players['cspg'] = round((players['clean_sheets'] / players['games']), 1)
    players['bppg'] = round((players['bonus'] / players['games']), 1)
    return players

#--------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------






#%%
# Grab advanced team data from whoscored (3 tabs: summary, defensive, offensive) and create corresponding csv's
def whoscored_team_to_csv(gametype):
    chromedriver = "/Users/ajanimotta/Downloads/chromedriver"
    driver = webdriver.Chrome(chromedriver)
    driver.get('https://www.whoscored.com/Regions/252/Tournaments/2/Seasons/7811/Stages/17590/TeamStatistics/England-Premier-League-2019-2020')

    statistics = {  # this is a list of all the tabs on the page
        'summary': DataFrame(),
        'defensive': DataFrame(),
        'offensive': DataFrame(),
    }

    count = 0
    time.sleep(3)
    tabs = driver.find_element_by_xpath('//*[@id="stage-team-stats-options"]').find_elements_by_tag_name('li')  # this pulls all the tab elements
    for tab in tabs[:-1]:  # iterate over the different tab sections
        print("tab text: ", tab.text)
        section = tab.text.lower()
        print("section: ", section, "section title: ", section.title())
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="stage-team-stats-options"]').find_element_by_link_text(section.title()).click()  # clicks the actual tab by using the dictionary's key (.proper() makes the first character in the string uppercase)
        time.sleep(3)
        while driver.find_element_by_xpath('//*[@id="statistics-team-table-%s"]' % section).get_attribute('class') == 'is-updating':  # string formatting on the xpath to change for each section that is iterated over
            time.sleep(1)
        view = driver.find_element_by_link_text(gametype)
        view.click() 
        time.sleep(3)
        table = driver.find_element_by_xpath('//*[@id="statistics-team-table-%s"]' % section)  # string formatting on the xpath to change for each section that is iterated over
        table_html = table.get_attribute('innerHTML')
        df = pd.read_html(table_html)[0]
        statistics[section] = pd.concat([statistics[section], df])
        count += 1

    statistics['summary'].to_csv('csv/summary_team_%s.csv' % gametype, index = False)
    statistics['defensive'].to_csv('csv/defensive_team_%s.csv' % gametype, index = False)
    statistics['offensive'].to_csv('csv/offensive_team_%s.csv' % gametype, index = False)
    return statistics
#%%
def whoscored_team_table_to_csv():
    chromedriver = "/Users/ajanimotta/Downloads/chromedriver"
    driver = webdriver.Chrome(chromedriver)
    driver.get('https://www.whoscored.com/Regions/252/Tournaments/2/England-Premier-League')

    table_df = pd.DataFrame()
    time.sleep(5)
    wide = driver.find_element_by_link_text('Wide')
    wide.click()
    time.sleep(3) 
    table = driver.find_element_by_xpath('//*[@id="standings-17590"]')
    table_html = table.get_attribute('innerHTML')
    df = pd.read_html(table_html)[0]
    table_df = pd.concat([table_df, df])
    time.sleep(5)
    table_df.to_csv('csv/team_table.csv', index = False)
    return table_df
#%%
def advanced_team():
    team_stats = {
        'overall': pd.DataFrame(),
        'home': pd.DataFrame(),
        'away': pd.DataFrame()
    }

    f = open("csv/teams.csv", "r")
    fpl_team_df = pd.read_csv(f)
    fpl_team_df = fpl_team_df[['id', 'name', 'short_name']]

    sum_ov = open('csv/summary_team_Overall.csv', "r")
    sum_ov_df = pd.read_csv(sum_ov)
    sum_ov_df = sum_ov_df [['Team', 'Goals', 'Shots pg', 'Possession%']]
    sum_ov_df = sum_ov_df.rename(columns={"Team": "name", "Goals": "total_goals", "Shots pg": "spg", "Possession%": "poss"})
    team_stats['overall'] = pd.concat([team_stats['overall'], sum_ov_df], axis=1)

    sum_home = open('csv/summary_team_Home.csv', "r")
    sum_home_df = pd.read_csv(sum_home)
    sum_home_df = sum_home_df [['Team', 'Goals', 'Shots pg', 'Possession%']]
    sum_home_df = sum_home_df.rename(columns={"Team": "name", "Goals": "goals_home", "Shots pg": "spg_home", "Possession%": "poss_home"})
    team_stats['home'] = pd.concat([team_stats['home'], sum_home_df], axis=1)

    sum_away = open('csv/summary_team_Away.csv', "r")
    sum_away_df = pd.read_csv(sum_away)
    sum_away_df = sum_away_df [['Team', 'Goals', 'Shots pg', 'Possession%']]
    sum_away_df = sum_away_df.rename(columns={"Team": "name", "Goals": "goals_away", "Shots pg": "spg_away", "Possession%": "poss_away"})
    team_stats['away'] = pd.concat([team_stats['away'], sum_away_df], axis=1)
    
    def_ov = open('csv/defensive_team_Overall.csv', "r")
    def_ov_df = pd.read_csv(def_ov)
    def_ov_df = def_ov_df[['Shots pg']]
    def_ov_df = def_ov_df.rename(columns={"Shots pg": "scpg"})
    team_stats['overall'] = pd.concat([team_stats['overall'], def_ov_df], axis=1)

    def_home = open('csv/defensive_team_Home.csv', "r")
    def_home_df = pd.read_csv(def_home)
    def_home_df = def_home_df[['Shots pg']]
    def_home_df = def_home_df.rename(columns={"Shots pg": "scpg_home"})
    team_stats['home'] = pd.concat([team_stats['home'], def_home_df], axis=1)

    def_away = open('csv/defensive_team_Away.csv', "r")
    def_away_df = pd.read_csv(def_away)
    def_away_df = def_away_df[['Shots pg']]
    def_away_df = def_away_df.rename(columns={"Shots pg": "scpg_away"})
    team_stats['away'] = pd.concat([team_stats['away'], def_away_df], axis=1)

    off_ov = open("csv/offensive_team_Overall.csv", "r")
    off_ov_df = pd.read_csv(off_ov)
    off_ov_df = off_ov_df[['Shots OT pg']]
    off_ov_df = off_ov_df.rename(columns={"Shots OT pg": "sot"})
    team_stats['overall'] = pd.concat([team_stats['overall'], off_ov_df], axis=1)

    off_home = open("csv/offensive_team_Home.csv", "r")
    off_home_df = pd.read_csv(off_home)
    off_home_df = off_home_df[['Shots OT pg']]
    off_home_df = off_home_df.rename(columns={"Shots OT pg": "sot_home"})
    team_stats['home'] = pd.concat([team_stats['home'], off_home_df], axis=1)

    off_away = open("csv/offensive_team_Away.csv", "r")
    off_away_df = pd.read_csv(off_away)
    off_away_df = off_away_df[['Shots OT pg']]
    off_away_df = off_away_df.rename(columns={"Shots OT pg": "sot_away"})
    team_stats['away'] = pd.concat([team_stats['away'], off_away_df], axis=1)

    f4 = open("csv/team_table.csv", "r")
    table_df = pd.read_csv(f4)
    table_df = table_df.rename(columns={'R': 'rank', "Team": "name"})

    teams_df = pd.merge(team_stats['overall'], team_stats['home'], on='name')
    teams_df = pd.merge(teams_df, team_stats['away'], on='name')
    teams_df = pd.merge(teams_df, table_df, on='name')
    team_names = {
        "Manchester City": "Man City", "Leicester": "Leicester", "Liverpool": "Liverpool", "Chelsea":"Chelsea",
        "Aston Villa":"Aston Villa", "Burnley":"Burnley", "Wolverhampton Wanderers":"Wolves", "Sheffield United":"Sheffield Utd",
         "Bournemouth":"Bournemouth", "Arsenal":"Arsenal", "Tottenham":"Spurs", "Manchester United":"Man Utd", 
         "West Ham":"West Ham", "Brighton":"Brighton", "Crystal Palace":"Crystal Palace",
          "Newcastle United":"Newcastle", "Everton":"Everton", "Norwich":"Norwich",
           "Watford":"Watford", "Southampton":"Southampton"
    }
    teams_df['name'] = teams_df['name'].map(team_names)
    teams_df = pd.merge(fpl_team_df,teams_df, on='name')
    
    return teams_df


#%%
#UPDATE FPL_PLAYER DF (download new 'cleaned_players.csv', 'players_raw.csv') --> RUN fpl_player_to_csv() --> fpl_player

#UPDATE GAMEWEEK/FIXTURE DFs (download new 'merged_gw.csv' , 'fixtures.csv') --> RUN get_gws/fixtures

#UPDATE UNDERSTAT PLAYER DATA (download new 'understat_player.csv') --> RUN understat_player()

#UPDATE WHOSCORED PLAYER DATA --> RUN 'whoscored_all_players_to_csv('section')' for 4 sections (summary, defensive, offensive, passing)

#Update WHOSCORED TEAM DATA --> RUN 'whoscored_team_to_csv('section')' for 3 sections (Overall, Home, Away))
# --> Get team table metrics (GF, GA, wins, pts, etc.) --> RUN whoscored_team_table_to_csv()

#GET PLAYER DATAFRAME with all fpl, understat, and whoscored data
#players = get_players()

#GET TEAM DATAFRAME with fpl, whoscored data
# team_stats = advanced_team()

#UPDATE TEAM_RATINGS_DF --> then call get_team_ratings
#fixtures = get_fixtures()
#ratings = team_rating(fixtures)

#PLOTS-----CREATE CSVs FOR EACH HOME/AWAY,STRONG/WEAK,FORM PLOT (for gkps,defs,mids,fwds.html)
#gkps_home_away_csv()
#strong_weak_csv('GKP')
#form_csv('GKP')
#defs_home_away_csv()
#strong_weak_csv('DEF')
#form_csv('DEF')
#mids_home_away_csv()
#strong_weak_csv('MID')
#form_csv('MID')
#fwds_home_away_csv()
#strong_weak_csv('FWD')
#form_csv('FWD')