import os
import json
import re
import requests
import urllib
from bs4 import BeautifulSoup

outputs = []

game_url = 'http://www.ifiction.org/games/playz.php'

game_dict = {
            'cat': None,
            'game': None,
            'mode': 'html',
            'command': None,
            'savegame': None,
            'submit': 'Do it' # Almost certainly can get rid of this
        }

last_command = None

game_list = json.loads( open(os.getcwd() + '/plugins/play/games.json').read() )

def process_message(data):
    """
    Parse incoming message for play command
    """
    global game_dict
    global last_command 

    if data['text'].startswith( ('pobo play', '!') ):

        # Get command
        try:
            cmd = re.split('pobo play|!', data['text'])[1].strip()
        
        except IndexError:
            error_msg = 'That is some kind of bogus command you passed me.'
            outputs.append(data['channel'], error_msg)

        # Set cmd here so it can be overwritten below if needed
        game_dict['command'] = cmd
        last_command = cmd

        # Start a new game
        if cmd.startswith('start'):
            r = start_game(cmd)


        # Get list of games available to play
        if cmd.startswith('list games'):
            if cmd.split('list games')[1]:
                cat_num = int(cmd.split('list games')[1].strip())
                cat_games = game_list['categories'][cat_num - 1]
                output = '*Category:* %s\n\n```' % cat_games['category']
                
                for game in cat_games['games']:
                    output += '%d) %s\n' % (game['game_id'], game['game_title'])
                    output += '    %s\n\n' % game['game_desc']

                output += '```\n_Type_ `pobo play start <game number>` _to begin playing_'

            else:                
                output = '*CATEGORIES*\n```' 
                for idx, item in enumerate(game_list['categories'], 1):
                    output += '%d) %s\n' % (idx, item['category'])
                output += '```\n_Type_ `pobo play list games <category number>` _to get a list of games_'

            return outputs.append([data['channel'], output])            

        # Load an existing game
        if cmd.startswith('load'):
            game_loaded = load_game(cmd)
            if game_loaded:
                outputs.append([data['channel'], '*SAVE GAME LOADED*'])
            else:
                outputs.append([data['channel'], 'Hmmm...looks like a bougus save file.'])

        # Save current game
        if cmd == 'save':
            savegame_gist = save_game()
            return outputs.append([data['channel'], '*GAME SAVED*\nGame ID: %s (%s)' % (savegame_gist['id'], savegame_gist['url'])])

        # Restart current game
        if cmd == 'restart':
            # Re-init game state
            game_dict['savegame'] = None

        # First time game loads, we don't have a save game state, so use GET request
        try:
            if not game_dict['savegame'] and not r:
                    return outputs.append([data['channel'], '_Please *start* a game first.\nFor a list of games, type:_ `pobo play list games`'])
            elif game_dict['savegame']:
                r = requests.post(game_url, data=game_dict)
        except NameError:
            r = requests.post(game_url, data=game_dict)

        # Update global save game state for next time
        soup = BeautifulSoup(r.text)
        game_dict['savegame'] = soup.find('input', {'name': 'savegame'}).get('value').rstrip('\n') # Soup adding line feed?

        # Final response
        response = format_response(r)
        outputs.append([data['channel'], response])


def format_response(request):
    """
    Given a python requests object, trim and clean response
    """
    global last_command

    soup = BeautifulSoup(request.text, 'html5lib')

    # Get response from game server to our command
    response = soup.find('pre').text

    # Get rid of last input line
    response = response.rstrip().rstrip('>').rstrip()

    if game_dict['savegame']: 
        response = response.split('>')[-1] # Only get latest response, not all history

    response = response.strip(last_command) # Get rid of previous command
    response = response.strip().rstrip()
    response = '```\n%s\n```' % response

    return response


def start_game(cmd):
    """
    Start a new game given game id
    """
    global game_dict
    
    game_id = cmd.split('start')[1].strip()
    
    # Assign game ID, re-initialize all other game dict settings
    game_dict['cat'] = None
    game_dict['game'] = game_id
    game_dict['savegame'] = None
    game_dict['cat'] = None



    url = '%s?game=%s' % (game_url, game_id)
    r = requests.get(url)
    return r

        

def load_game(cmd):
    """
    Load a saved game state from an external github gist.
    Formatted as JSON.
    """
    global game_dict

    try:
        # Retrieve and convert save game to JSON data
        save_id = cmd.split('load')[1].strip()
        r = requests.get('https://api.github.com/gists/%s' % save_id)
        gist_dict = r.json()
        raw_json = gist_dict['files']['savegame.txt']['content']
        saved_game_dict = json.loads(raw_json)

        # Assign save game data to global game dict
        game_dict['cat'] = saved_game_dict['cat']
        game_dict['game'] = saved_game_dict['game']
        game_dict['savegame'] = urllib.unquote(saved_game_dict['savegame'])
        game_dict['command'] = 'look'
        return True
        
    except IndexError:
        return False

def save_game():
    """
    Save game state to an external github gist.
    Formatted as JSON.
    """
    global game_dict
    saved_game_dict = {
                        'cat': game_dict['cat'],
                        'game': game_dict['game'],
                        'savegame': game_dict['savegame']
                      }

    post_dict = {
                    'description': 'Save Game File',
                    'public': True,
                    'files': {'savegame.txt': {'content': json.dumps(saved_game_dict) }}

                }
    r = requests.post('https://api.github.com/gists', data=json.dumps(post_dict))
    r = r.json()
    return r

