from flask import Flask, render_template, redirect, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.schema import PrimaryKeyConstraint
import random

from my_module import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///match.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Team1(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  player_name = db.Column(db.String(100), nullable=False)


class Team2(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  player_name = db.Column(db.String(100), nullable=False)


class first_batting(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  runs = db.Column(db.Integer)
  balls = db.Column(db.Integer)
  fours = db.Column(db.Integer)
  sixes = db.Column(db.Integer)
  wicket_type = db.Column(db.String(50))


class first_bowling(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  maidens = db.Column(db.Integer)
  overs = db.Column(db.Float)
  runs = db.Column(db.Integer)
  wickets = db.Column(db.Integer)


class second_batting(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  runs = db.Column(db.Integer)
  balls = db.Column(db.Integer)
  fours = db.Column(db.Integer)
  sixes = db.Column(db.Integer)
  wicket_type = db.Column(db.String(50))


class second_bowling(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(50))
  maidens = db.Column(db.Integer)
  overs = db.Column(db.Float)
  runs = db.Column(db.Integer)
  wickets = db.Column(db.Integer)


with app.app_context():
  db.create_all()


@app.route('/')
def index():
  return render_template("index.html")


############################################################


@app.route('/new_match', methods=['GET', 'POST'])
def new_match():
  if request.method == 'POST':
    team1 = request.form['team1']
    team2 = request.form['team2']
    venue = request.form['venue']
    overs = request.form['overs']
    create_match_details_file()
    modify_line_in_file("match_details.txt", 1, team1)
    modify_line_in_file("match_details.txt", 2, team2)
    modify_line_in_file("match_details.txt", 3, venue)
    modify_line_in_file("match_details.txt", 4, overs)

    return redirect("/select_teams")
  empty_txt_files()
  empty_database(db, Team1, Team2, first_batting, first_bowling, second_batting, second_bowling)
  return render_template("new_match.html")


############################################################


@app.route('/select_teams', methods=['GET', 'POST'])
def select_teams():
  if request.method == "POST":
    team1_players = [request.form[f'team1_player_{i}'] for i in range(1, 12)]
    team2_players = [request.form[f'team2_player_{i}'] for i in range(1, 12)]
    save_players_to_db(db, Team1, team1_players)
    save_players_to_db(db, Team2, team2_players)
    return redirect("/toss")
  team1_name = read_match_details()['team1_name']
  team2_name = read_match_details()['team2_name']
  return render_template("select_teams.html", team1_name=team1_name, team2_name=team2_name)


############################################################
@app.route('/toss', methods=['GET', 'POST'])
def toss():
  if request.method == 'POST':
    form_type = request.form['form_type']
    if form_type == 'toss_the_coin':
      team1 = read_match_details()["team1_name"]
      team2 = read_match_details()["team2_name"]
      toss_winner = random.choice([team1,team2])
      modify_line_in_file("match_details.txt", 5, toss_winner)
      toss_state = 1
    elif form_type == 'decision_time':
      toss_decision = request.form['decision']
      modify_line_in_file("match_details.txt", 6, toss_decision)
      toss_state = 2
  else:
    toss_state = 0
  toss_winner = read_match_details()["toss_winner"]
  toss_decision = read_match_details()["toss_decision"]
  return render_template("toss.html", toss_state=toss_state, toss_winner=toss_winner, toss_decision=toss_decision)
############################################################

@app.route('/first_innings', methods=['GET', 'POST'])
def first_innings():
  if request.method == 'POST':
    form_type = request.form['form_type']
    if form_type == 'select_openers':
      opener1 = request.form['opener1']
      opener2 = request.form['opener2']
      bowler = request.form['bowler']
      save_batsman_to_db(db, first_batting, opener1)
      save_batsman_to_db(db, first_batting, opener2)
      save_bowler_to_db(db, first_bowling, bowler)
      modify_line_in_file("match_details.txt", 7, opener1)
      modify_line_in_file("match_details.txt", 8, opener2)
      modify_line_in_file("match_details.txt", 9, bowler)
      f = open("inning_started.txt", "w")
      f.write("1")
      f.close()

      current_ball = None
      current_ball_dict = ""
      wicket_fallen = False
      over_is_done = False

    
    elif form_type in ["play_risky", "play_normal", "play_safe"]:
      striker = read_match_details()['striker']
      non_striker = read_match_details()['non_striker']
      bowler = read_match_details()['bowler']

      with open("free_hit.txt", 'r') as file:
        free_hit = file.read()
      batx = first_batting.query.filter_by(name=striker).first()
      xr = batx.runs
      xb = batx.balls
      x = (xr - xb)/20
      
      bowlx = first_bowling.query.filter_by(name=bowler).first()
      yo = bowlx.overs
      a = int(yo)
      b = 10*(yo-a)
      yb = int(6*a+b)
      yw = bowlx.wickets
      yr = bowlx.runs
      y = (yb*(yw+1) - yr)/25
      current_ball = through_ball(free_hit,x,y,form_type)
      current_ball_dict = current_ball.get_dict()
      f = open("last_ball.txt", "w")
      f.write(str(current_ball.bat_runs))
      f.close()
      
      update_scoreboard(current_ball)
      update_freehit(current_ball)
      update_striker(db, first_batting, striker, current_ball, bowler)
      update_non_striker(db, first_batting, non_striker, current_ball)
      update_strike(current_ball, striker, non_striker)
      update_bowler(db, first_bowling, bowler, current_ball)
      
      wicket_fallen = bool(current_ball.wicket_type is not None and current_ball.noball is None)
      overs = read_scoreboard()['overs']
      over_is_done = over_ended(overs, current_ball)
      f = open("over_ended.txt","w")
      if over_is_done:
        f.write("1")
      else:
        f.write("")
      f.close()
      
      
      
    elif form_type == 'select_new_batsman':
      who_is_out = request.form['who_is_out']
      new_batsman = request.form['new_batsman']
      save_batsman_to_db(db ,first_batting, new_batsman)
      f = open("last_ball.txt", "r")
      last_ball = f.read()
      last_ball = int(last_ball)
      f.close()
      if not is_odd(last_ball):
        if who_is_out == "striker":
          modify_line_in_file("match_details.txt", 7, new_batsman)
        elif who_is_out == "non_striker":
          modify_line_in_file("match_details.txt", 8, new_batsman)
      elif is_odd(last_ball):
        if who_is_out == "striker":
          modify_line_in_file("match_details.txt", 8, new_batsman)
        elif who_is_out == "non_striker":
          modify_line_in_file("match_details.txt", 7, new_batsman)
      
      

      current_ball = None
      current_ball_dict = ""
      wicket_fallen = False
      overs = read_scoreboard()['overs']
      f = open("over_ended.txt","r")
      over_is_done = bool(f.read())
      f.close()
    
    elif form_type == 'select_new_bowler':
      new_bowler = request.form['new_bowler']
      save_bowler_to_db(db, first_bowling, new_bowler)
      modify_line_in_file("match_details.txt", 9, new_bowler)
      striker = read_match_details()['striker']
      non_striker = read_match_details()['non_striker']
      modify_line_in_file("match_details.txt", 7, non_striker)
      modify_line_in_file("match_details.txt", 8, striker)

      current_ball = None
      current_ball_dict = ""
      wicket_fallen = False
      over_is_done = False
    
  else:
    current_ball = None
    current_ball_dict = ""
    wicket_fallen = False
    over_is_done = False
  
  with open("inning_started.txt", 'r') as file:
    inning_started = file.read()
  batting_team_name = toss_details(Team1,Team2)['batting_1st_name']
  if not inning_started:
    initiate_scoreboard(batting_team_name, target=0)
    initiate_freehit()
    initiate_last_ball()
    initiate_over_ended()
  inning_ended = inning_ended_func(wicket_fallen, over_is_done)
  if inning_ended:
    empty_this_file("inning_started.txt")
    target = read_scoreboard()['runs'] + 1
    f = open("target.txt", "w")
    f.write(str(target))
    f.close()
  
  if wicket_fallen:
    if current_ball.wicket_type in ["bold","catch","lbw", "stumped","striker-runnout"]:
      who_is_out = "striker"
    elif current_ball.wicket_type == "non-striker-runnout":
      who_is_out = "non_striker"
  else:
    who_is_out = None

  

  
  batting_1st_class = toss_details(Team1,Team2)['batting_1st_class']
  batting_2nd_class = toss_details(Team1,Team2)['batting_2nd_class']
  batting_1st_players = batting_1st_class.query.with_entities(batting_1st_class.player_name).all()
  batting_1st = [player.player_name for player in batting_1st_players]
  batting_2nd_players = batting_2nd_class.query.with_entities(batting_2nd_class.player_name).all()
  batting_2nd = [player.player_name for player in batting_2nd_players]

  batting_data = first_batting.query.all()
  bowling_data = first_bowling.query.all()
  batting_done = [player.name for player in batting_data]
  batting_left = subtract_lists(batting_1st, batting_done)

  striker_name = read_match_details()['striker']
  non_striker_name = read_match_details()['non_striker']
  bowler_name = read_match_details()['bowler']
  if striker_name != "":
    striker_data = first_batting.query.filter_by(name=striker_name).first()
    non_striker_data = first_batting.query.filter_by(name=non_striker_name).first()
    bowler_data = first_bowling.query.filter_by(name=bowler_name).first()
    striker_list = [striker_name, striker_data.runs, striker_data.balls, "*"]
    non_striker_list = [non_striker_name, non_striker_data.runs, non_striker_data.balls, ""]
    bowler_list = [bowler_name, bowler_data.wickets, bowler_data.runs, bowler_data.overs]
  else:
    striker_list = None
    non_striker_list = None
    bowler_list = None
  return render_template("first_innings.html", inning_started=inning_started,inning_ended=inning_ended,batting_1st=batting_1st, batting_2nd=batting_2nd,wicket_fallen=wicket_fallen,over_is_done=over_is_done,current_ball_dict=current_ball_dict,read_scoreboard=read_scoreboard(), batting_data=batting_data, bowling_data=bowling_data,batting_left=batting_left,who_is_out=who_is_out,striker_list=striker_list,non_striker_list=non_striker_list,bowler_list=bowler_list)



@app.route('/second_innings', methods=['GET', 'POST'])
def second_innings():
  if request.method == 'POST':
    form_type = request.form['form_type']
    if form_type == 'select_openers':
      opener1 = request.form['opener1']
      opener2 = request.form['opener2']
      bowler = request.form['bowler']
      save_batsman_to_db(db, second_batting, opener1)
      save_batsman_to_db(db, second_batting, opener2)
      save_bowler_to_db(db, second_bowling, bowler)
      modify_line_in_file("match_details.txt", 7, opener1)
      modify_line_in_file("match_details.txt", 8, opener2)
      modify_line_in_file("match_details.txt", 9, bowler)
      f = open("inning_started.txt", "w")
      f.write("1")
      f.close()

      current_ball = None
      current_ball_dict = ""
      wicket_fallen = False
      over_is_done = False


    elif form_type in ["play_risky", "play_normal", "play_safe"]:
      striker = read_match_details()['striker']
      non_striker = read_match_details()['non_striker']
      bowler = read_match_details()['bowler']

      with open("free_hit.txt", 'r') as file:
        free_hit = file.read()
      batx = second_batting.query.filter_by(name=striker).first()
      xr = batx.runs
      xb = batx.balls
      x = (xr - xb)/20

      bowlx = second_bowling.query.filter_by(name=bowler).first()
      yo = bowlx.overs
      a = int(yo)
      b = 10*(yo-a)
      yb = int(6*a+b)
      yw = bowlx.wickets
      yr = bowlx.runs
      y = (yb*(yw+1) - yr)/25
      current_ball = through_ball(free_hit,x,y,form_type)
      current_ball_dict = current_ball.get_dict()
      f = open("last_ball.txt", "w")
      f.write(str(current_ball.bat_runs))
      f.close()

      update_scoreboard(current_ball)
      update_freehit(current_ball)
      update_striker(db, second_batting, striker, current_ball, bowler)
      update_non_striker(db, second_batting, non_striker, current_ball)
      update_strike(current_ball, striker, non_striker)
      update_bowler(db, second_bowling, bowler, current_ball)

      wicket_fallen = bool(current_ball.wicket_type is not None)
      overs = read_scoreboard()['overs']
      over_is_done = over_ended(overs, current_ball)
      f = open("over_ended.txt","w")
      if over_is_done:
        f.write("1")
      else:
        f.write("")
      f.close()



    elif form_type == 'select_new_batsman':
      who_is_out = request.form['who_is_out']
      new_batsman = request.form['new_batsman']
      save_batsman_to_db(db ,second_batting, new_batsman)
      f = open("last_ball.txt", "r")
      last_ball = f.read()
      last_ball = int(last_ball)
      f.close()
      if not is_odd(last_ball):
        if who_is_out == "striker":
          modify_line_in_file("match_details.txt", 7, new_batsman)
        elif who_is_out == "non_striker":
          modify_line_in_file("match_details.txt", 8, new_batsman)
      elif is_odd(last_ball):
        if who_is_out == "striker":
          modify_line_in_file("match_details.txt", 8, new_batsman)
        elif who_is_out == "non_striker":
          modify_line_in_file("match_details.txt", 7, new_batsman)



      current_ball = None
      current_ball_dict = ""
      wicket_fallen = False
      overs = read_scoreboard()['overs']
      f = open("over_ended.txt","r")
      over_is_done = bool(f.read())
      f.close()

    elif form_type == 'select_new_bowler':
      new_bowler = request.form['new_bowler']
      save_bowler_to_db(db, second_bowling, new_bowler)
      modify_line_in_file("match_details.txt", 9, new_bowler)
      striker = read_match_details()['striker']
      non_striker = read_match_details()['non_striker']
      modify_line_in_file("match_details.txt", 7, non_striker)
      modify_line_in_file("match_details.txt", 8, striker)

      current_ball = None
      current_ball_dict = ""
      wicket_fallen = False
      over_is_done = False

  else:
    current_ball = None
    current_ball_dict = ""
    wicket_fallen = False
    over_is_done = False

  with open("inning_started.txt", 'r') as file:
    inning_started = file.read()
  batting_team_name = toss_details(Team1,Team2)['batting_2nd_name']
  f = open("target.txt", "r")
  target = f.read()
  f.close()
  if not inning_started:
    initiate_scoreboard(batting_team_name, target)
    initiate_freehit()
    initiate_last_ball()
    initiate_over_ended()
    modify_line_in_file("match_details.txt", 7, "")
    modify_line_in_file("match_details.txt", 8, "")
    modify_line_in_file("match_details.txt", 9, "")
  match_ended = match_ended_func(wicket_fallen, over_is_done)
  match_winner = None
  won_by = None
  match_tie = None
  if match_ended:
    batting_1stteam_name = toss_details(Team1,Team2)['batting_1st_name']
    batting_2ndteam_name = toss_details(Team1,Team2)['batting_2nd_name']
    chasing_team_score = int(read_scoreboard()['runs'])
    target = int(read_scoreboard()['target'])
    if chasing_team_score>=target:
      match_winner = batting_2ndteam_name
      won_by = str(10 - read_scoreboard()['wickets']) + " wickets"
      match_tie = False
    elif chasing_team_score == target-1:
      match_winner = None
      won_by = None
      match_tie = True
    else:
      match_winner = batting_1stteam_name
      won_by = str(target - 1 - chasing_team_score) + " runs"
      match_tie = False
    

  if wicket_fallen:
    if current_ball.wicket_type in ["bold","catch","lbw", "stumped","striker-runnout"]:
      who_is_out = "striker"
    elif current_ball.wicket_type == "non-striker-runnout":
      who_is_out = "non_striker"
  else:
    who_is_out = None




  batting_1st_class = toss_details(Team1,Team2)['batting_1st_class']
  batting_2nd_class = toss_details(Team1,Team2)['batting_2nd_class']
  batting_1st_players = batting_1st_class.query.with_entities(batting_1st_class.player_name).all()
  batting_1st = [player.player_name for player in batting_1st_players]
  batting_2nd_players = batting_2nd_class.query.with_entities(batting_2nd_class.player_name).all()
  batting_2nd = [player.player_name for player in batting_2nd_players]

  batting_data = second_batting.query.all()
  bowling_data = second_bowling.query.all()
  batting_done = [player.name for player in batting_data]
  batting_left = subtract_lists(batting_2nd, batting_done)

  striker_name = read_match_details()['striker']
  non_striker_name = read_match_details()['non_striker']
  bowler_name = read_match_details()['bowler']
  if striker_name != "":
    striker_data = second_batting.query.filter_by(name=striker_name).first()
    non_striker_data = second_batting.query.filter_by(name=non_striker_name).first()
    bowler_data = second_bowling.query.filter_by(name=bowler_name).first()
    striker_list = [striker_name, striker_data.runs, striker_data.balls, "*"]
    non_striker_list = [non_striker_name, non_striker_data.runs, non_striker_data.balls, ""]
    bowler_list = [bowler_name, bowler_data.wickets, bowler_data.runs, bowler_data.overs]
  else:
    striker_list = None
    non_striker_list = None
    bowler_list = None
  return render_template("second_innings.html", inning_started=inning_started,match_ended=match_ended, batting_1st=batting_1st, batting_2nd=batting_2nd,wicket_fallen=wicket_fallen,over_is_done=over_is_done,current_ball_dict=current_ball_dict,read_scoreboard=read_scoreboard(), batting_data=batting_data, bowling_data=bowling_data,batting_left=batting_left,who_is_out=who_is_out, match_winner=match_winner, won_by=won_by, match_tie=match_tie,striker_list=striker_list,non_striker_list=non_striker_list,bowler_list=bowler_list)

  

############################################################
if __name__ == "__main__":
  app.run(host='0.0.0.0', port=5000, debug=True)
