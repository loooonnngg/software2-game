from flask import Flask,jsonify
from flask_cors import CORS
from airport import airports
from player import Player
from saving import *

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

player=None
leaderboard=False
used_seed=None
save_id=None  #Saving the player id to be saved later
@app.route('/mainScreen/<option>')
def main_screen(option):
    if option=='leaderboard':       #view the leaderboard
        return jsonify({'status':'leaderboard','content':view_leaderboard()})
    elif option=='personal':        #view the personal saves
        return jsonify({'status':'personal','content':personal_load()})
@app.route('/loadSave/<player_id>')
def load_save(player_id):   #load the selected saves
    global player
    global save_id
    save_id=player_id
    player=saves_load(personal_load()[player_id])
    return jsonify({
        'Name':player.information()[0],
        'Difficulty':player.information()[1],
        'Money':player.information()[2],
        'Airports': player.information()[3],
        'Position': player.information()[5],
        'Fuel':player.information()[6],
        'Hints':player.information()[7],
        'Co2':player.information()[8],
        'Points':player.calculate_points(),
    })
@app.route('/loadLeaderboard/<name>/<difficulty>/<player_id>')
def load_leaderboard(name,difficulty,player_id):    #load the selected leaderboard item with name and difficulty input
    global player
    global leaderboard
    global used_seed
    global save_id
    save_id=None
    leaderboard=True
    used_seed=view_leaderboard()[int(player_id)-1][3]
    ap_list=leaderboard_load(view_leaderboard()[int(player_id)-1][2].split(','))
    player=Player(name,int(difficulty),1000*(4-int(difficulty)),ap_list)
    return jsonify({
        'Name':player.information()[0],
        'Difficulty':player.information()[1],
        'Money':player.information()[2],
        'Airports': player.information()[3],
        'Position': player.information()[5],
        'Fuel':player.information()[6],
        'Hints':player.information()[7],
        'Co2':player.information()[8],
        'Points':player.calculate_points(),
    })
@app.route('/mainGame/<name>/<difficulty>')
def main_game(name,difficulty):     #start the main game without loading previous saves
    global player
    global save_id
    save_id = None
    player=Player(name,int(difficulty),1000*(4-int(difficulty)),airports(12))
    return jsonify({
        'Name':player.information()[0],
        'Difficulty':player.information()[1],
        'Money':player.information()[2],
        'Airports': player.information()[3],
        'Position': player.information()[5],
        'Fuel':player.information()[6],
        'Hints':player.information()[7],
        'Co2':player.information()[8],
        'Points':player.calculate_points(),
    })
@app.route('/flyTo/<airport_id>')
def fly_to(airport_id):     #innitiate flying to airport, id refer to key of airport inside dictionary
    global player
    distance=player.fly(airport_id)
    points=player.calculate_points()
    remaining=player.remaining_airports()
    fuel=player.fuel_left()
    packet={
        'Distance':round(distance,2),
        'Points':round(points,2),
        'Remaining':remaining,
        'Fuel':round(fuel,2),
        'Co2':round(player.co2_emitted(),2),
        'Position':player.player_position()
    }
    return jsonify(packet)
@app.route('/shop/<item>')
def shop(item):     #let player buy hints or fuel
    global player
    if item=='hints':
        player.buy_hints()
    elif item=='fuel':
        player.buy_fuel()
    return jsonify({
        'balance':player.show_balance(),
        'fuel':round(player.fuel_left(),2),
        'hints':player.hints_left()
    })
@app.route('/hint')
def hint():     #give player hints about the closest airport
    global player
    nearest_airport={
        'nearest':player.use_hint()[0],
        'hints': player.hints_left()
    }
    return jsonify(nearest_airport)

@app.route('/quit/<status>')
def game_stop(status): #status have 2 states, saving to leaderboard or saving to personal progress
    global player
    global leaderboard
    global used_seed
    global save_id
    stop_status=None
    if status=='leaderboard':
        if leaderboard:
            stop_status=leaderboard_save_used(player,used_seed)
        else:
            stop_status=leaderboard_save(player)
    elif status=='personal':
        stop_status = personal_save(player,save_id)
    return jsonify({'status':stop_status})
if __name__ == '__main__':
    app.run(use_reloader=True, host='127.0.0.1', port=8000)