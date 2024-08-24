from abc import abstractclassmethod
import random
# creating new files

def create_match_details_file():
  f = open("match_details.txt", "w")
  f.write("" + "\n")
  f.write("" + "\n")
  f.write("" + "\n")
  f.write("" + "\n")
  f.write("" + "\n")
  f.write("" + "\n")
  f.write("" + "\n")
  f.write("" + "\n")
  f.write("" + "\n")
  f.close()

####################################################################

# deleting old data

def empty_database(db, Team1, Team2, first_batting, first_bowling, second_batting, second_bowling):
  db.session.query(Team1).delete()
  db.session.query(Team2).delete()
  db.session.query(first_batting).delete()
  db.session.query(first_bowling).delete()
  db.session.query(second_batting).delete()
  db.session.query(second_bowling).delete()
  db.session.commit()
  
def empty_txt_files():
  empty_this_file("match_details.txt")
  empty_this_file("inning_started.txt")
  empty_this_file("free_hit.txt")
  empty_this_file("scoreboard.txt")
  empty_this_file("last_ball.txt")

def empty_this_file(file_name):
  f = open(file_name, "w")
  f.write("")
  f.close()

####################################################################

# functions for match_details.txt

def read_match_details():
  with open('match_details.txt', 'r') as file:
    data = file.readlines()
    match_details = {
        'team1_name': data[0].strip(),
        'team2_name': data[1].strip(),
        'venue': data[2].strip(),
        'overs': data[3].strip(),
        'toss_winner': data[4].strip(),
        'toss_decision': data[5].strip(),
        'striker' : data[6].strip(),
        'non_striker' : data[7].strip(),
        'bowler' : data[8].strip()
    }
  return match_details

def modify_line_in_file(filename, line_number, new_content):
  with open(filename, 'r') as file:
      lines = file.readlines()

  if 1 <= line_number <= len(lines):
      lines[line_number - 1] = new_content + '\n'

      with open(filename, 'w') as file:
          file.writelines(lines)

############################################################

def save_players_to_db(db, Model, players):
  for player in players:
    if player:  # Check if the player name is not empty
      db.session.add(Model(player_name=player))
  db.session.commit()

def save_batsman_to_db(db, Model, batsman):
  db.session.add(Model(name=batsman,runs=0,balls=0,fours=0,sixes=0,wicket_type="not out"))
  db.session.commit()

def save_bowler_to_db(db, Model, bowler):
  existing_bowler = Model.query.filter_by(name=bowler).first()
  if not existing_bowler:
    db.session.add(Model(name=bowler,maidens=0,overs=0 ,runs=0 ,wickets=0))
    db.session.commit()
#############################################################

def toss_details(Team1, Team2):
  toss_winner = read_match_details()['toss_winner']
  toss_decision = read_match_details()['toss_decision']
  if toss_winner == read_match_details()['team1_name']:
    toss_loser = read_match_details()['team2_name']
  else:
    toss_loser = read_match_details()['team1_name']

  batting_1st_name = toss_winner if toss_decision=='bat' else toss_loser
  batting_2nd_name = toss_winner if toss_decision=='field' else toss_loser
  if batting_1st_name == read_match_details()['team1_name']:
    batting_1st_class = Team1
    batting_2nd_class = Team2
  else:
    batting_1st_class = Team2
    batting_2nd_class = Team1
  toss_dict = {
    'batting_1st_name' : batting_1st_name,
    'batting_2nd_name' : batting_2nd_name,
    'batting_1st_class' : batting_1st_class,
    'batting_2nd_class' : batting_2nd_class
  }
  return toss_dict

###########################################################
class delivery():
  def __init__(self,bat_runs,extras,wicket_type,wide,bye,noball,runnout):
    self.bat_runs = bat_runs
    self.extras = extras
    self.wicket_type = wicket_type
    self.wide = wide
    self.bye = bye
    self.noball = noball
    self.runnout = runnout
    self.dict = [self.bat_runs, self.extras, self.wicket_type, self.wide, self.bye, self.noball, self.runnout]
    self.dict = {
      "bat_runs": bat_runs,
      "extras": extras,
      "wicket_type": wicket_type ,
      "wide": wide ,
      "bye": bye ,
      "noball": noball ,
      "runnout": runnout
    }

  def get_dict(self):
    return self.dict

def create_del(ball):
  noballs = ["noball", None]
  wides = [0,1,4,"stumped"]
  byes = [1, 2, 4]
  runnouts = ["striker-runnout","non-striker-runnout"]
  wickets = ["bold","catch","lbw", "stumped"]


  
  wide = random.choices(wides, weights=[91.99,3,5,0.01])[0] if ball == "Wide" else None
  bye = random.choices(byes, weights=[69,1,30])[0] if ball == "Bye" else None
  runnout = random.choices(runnouts, weights=[60,40])[0] if ball == "Runnout" else None
  
  wicket_type = random.choices(wickets, weights=[50,20,15,15])[0] if ball == "Wicket" else None
  if runnout is not None:
    wicket_type = runnout
  if ball == "Wide" and wide == "stumped":
    wicket_type = "stumped"


  if ball in [0,1,2,3,4,6]:
    bat_runs = ball
  elif ball == "Runnout":
    bat_runs = random.choices([0,1,2], weights=[40,50,10])[0]
  else:
    bat_runs = 0

  if ball == "Wide":
    extras = wide+1 if wide != "stumped" else 1
  elif ball == "Bye":
    extras = bye
  else:
    extras = 0

  noball = random.choices(noballs, weights=[0.5,99.5])[0]
  if noball == "noball":
    extras +=1

  current_del = delivery(bat_runs,extras,wicket_type,wide,bye,noball,runnout)
  return current_del

def through_ball(free_hit, x, y,form_type):
  if x<-1:
    x = -1
  if x>2.5:
    x = 2.5
  if y<-1:
    y = -1
  if y>2.5:
    y = 2.5
  
  if form_type == "play_risky":
    z = 1
  elif form_type == "play_normal":
    z = 0
  elif form_type == "play_safe":
      z = -1
  
  if not free_hit:
    my_list = [0, 1, 2, 3, 4, 6, "Wicket", "Wide", "Bye", "Runnout"]
    probs = [36.8-3.4*x+3*y-z*8.3 ,25+x-y-z*2.5 , 7.5+x-y+z*2.5 ,0.2+z*0.3 ,12.5+x-y+z*2.5 ,7.5+x-y+z*2.5 ,5-0.6*x+2*y+z*1.5 ,4-y ,1 ,0.5+z*0.5]
    
  else:
    my_list = [0, 1, 2, 3, 4, 6, "Wide", "Bye", "Runnout"]
    probs = [25, 25, 2.9, 0.1, 15, 25, 6, 0.5, 0.5]
  this_ball = random.choices(my_list, weights=probs)[0]
  # this_ball = "Runnout"
  current_del = create_del(this_ball)
  return current_del
############################################################

def is_odd(number):
  if not isinstance(number, int):
    return False
  return number % 2 != 0

def is_last_del(number):
  number = number*2
  str_num = str(number)
  num_list = str_num.split(".")
  if is_odd(int(num_list[0])) and num_list[1]=="0":
    return True
  else:
    return False

def over_ended(number,current_ball):
  str_num = str(number)
  num_list = str_num.split(".")
  if current_ball.wide is not None or current_ball.noball is not None:
    return False
  if num_list[0]!="0" and num_list[1]=="0":
    return True
  else:
    return False
  

############################################################

def initiate_scoreboard(team_name, target):
  f = open("scoreboard.txt","w")
  f.write(team_name+"\n")
  f.write("0"+"\n")
  f.write("0"+"\n")
  f.write("0"+"\n")
  f.write("0"+"\n")
  f.write(str(target)+"\n")
  f.close()

def read_scoreboard():
  with open('scoreboard.txt', 'r') as file:
    data = file.readlines()
    team_name = data[0].strip()
    runs = int(data[1].strip())
    wickets = int(data[2].strip())
    overs = float(data[3].strip())
    extras = int(data[4].strip())
    target = data[5].strip()
    scoreboard = {
        'team_name': team_name,
        'runs': runs,
        'wickets': wickets,
        'overs': overs,
        'extras': extras,
        'target': target
    }
  return scoreboard

def update_scoreboard(current_ball):
  runs = read_scoreboard()['runs']
  wickets = read_scoreboard()['wickets']
  overs = read_scoreboard()['overs']
  extras = read_scoreboard()['extras']
  
  runs += (current_ball.bat_runs + current_ball.extras)
  
  if (current_ball.wicket_type is not None and current_ball.noball is None):
    wickets += 1
  
  if current_ball.wide is None and current_ball.noball is None:
    overs = overs+0.5 if is_last_del(overs) else overs+0.1
  overs = round(overs, 1)

  extras += current_ball.extras
    
  
  modify_line_in_file("scoreboard.txt", 2, str(runs))
  modify_line_in_file("scoreboard.txt", 3, str(wickets))
  modify_line_in_file("scoreboard.txt", 4, str(overs))
  modify_line_in_file("scoreboard.txt", 5, str(extras))


def initiate_last_ball():
  f = open("last_ball.txt","w")
  f.write("")
  f.close()

def initiate_over_ended():
  f = open("over_ended.txt","w")
  f.write("")
  f.close()

def initiate_freehit():
  f = open("free_hit.txt","w")
  f.write("")
  f.close()

def update_freehit(current_ball):
  f = open("free_hit.txt","w")
  if current_ball.noball is not None:
    f.write("1")
  else:
    f.write("")
  f.close()

def update_striker(db, first_batting, striker, current_ball, bowler):
  batsman = first_batting.query.filter_by(name=striker).first()
  
  batsman.runs += current_ball.bat_runs
  if current_ball.wide is None:
    batsman.balls += 1
  if current_ball.bat_runs == 4:
    batsman.fours += 1
  if current_ball.bat_runs == 6:
    batsman.sixes += 1
  match current_ball.wicket_type:
    case "bold":
      wicket_type = "b " + bowler
    case "catch":
      wicket_type = "c fielder b " + bowler
    case "lbw":
      wicket_type = "lbw b " + bowler
    case "stumped":
      wicket_type = "st keeper b " + bowler
    case "striker-runnout":
      wicket_type = "runnout"
    case _:
      wicket_type = "not out"
  if current_ball.noball is not None:
    wicket_type = "not out"
  batsman.wicket_type = wicket_type
  db.session.commit()

def update_non_striker(db, first_batting, non_striker, current_ball):
  batsman = first_batting.query.filter_by(name=non_striker).first()
  wicket_type = "runnout" if current_ball.wicket_type == "non-striker-runnout" else "not out"
  batsman.wicket_type = wicket_type
  db.session.commit()

def update_strike(current_ball, striker, non_striker):
  if is_odd(current_ball.bat_runs) or is_odd(current_ball.wide) or is_odd(current_ball.bye):
    modify_line_in_file("match_details.txt", 7, non_striker)
    modify_line_in_file("match_details.txt", 8, striker)
    striker = read_match_details()['striker']
    non_striker = read_match_details()['non_striker']

def update_bowler(db, first_bowling, bowler, current_ball):
  current_bowler = first_bowling.query.filter_by(name=bowler).first()
  current_bowler.maidens = current_bowler.maidens
  if current_ball.wide is None and current_ball.noball is None:
    current_bowler.overs = current_bowler.overs+0.5 if is_last_del(current_bowler.overs) else current_bowler.overs+0.1
    current_bowler.overs = round(current_bowler.overs, 1)
  current_bowler.runs += (current_ball.bat_runs + current_ball.extras)
  if current_ball.wicket_type in ["bold","catch","lbw", "stumped"] and current_ball.noball is None:
    current_bowler.wickets += 1
  db.session.commit()


def inning_ended_func(wicket_fallen, over_is_done):
  inning_ended = False
  overs = read_scoreboard()['overs']
  overs = int(overs)
  total_overs = read_match_details()['overs']
  total_overs = int(total_overs)
  wickets_fallen = read_scoreboard()['wickets']
  wickets_fallen = int(wickets_fallen)
  if over_is_done and overs == total_overs:
    inning_ended = True
  if wicket_fallen and wickets_fallen == 10:
    inning_ended = True
  return inning_ended

def match_ended_func(wicket_fallen, over_is_done):
  match_ended = False
  overs = read_scoreboard()['overs']
  overs = int(overs)
  total_overs = read_match_details()['overs']
  total_overs = int(total_overs)
  wickets_fallen = read_scoreboard()['wickets']
  wickets_fallen = int(wickets_fallen)
  chasing_team_score = int(read_scoreboard()['runs'])
  target = int(read_scoreboard()['target'])
  if over_is_done and overs == total_overs:
    match_ended = True
  if wicket_fallen and wickets_fallen == 10:
    match_ended = True
  if chasing_team_score>=target:
    match_ended = True
  return match_ended

def subtract_lists(list_a, list_b):
  return [item for item in list_a if item not in list_b]