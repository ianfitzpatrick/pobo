import json
import re
import requests
import urllib
from BeautifulSoup import BeautifulSoup

outputs = []

game_url = 'http://www.ifiction.org/games/playz.php?cat=2&game=3&mode=html'

game_dict = {
            'cat': 2,
            'game': 3,
            'mode': 'html',
            'command': None,
            'savegame': None,
            'submit': 'Do it' # Almost certainly can get rid of this
        }

def process_message(data):
    """
    Parse incoming message for play command
    """
    global game_dict

    if data['text'].startswith( ('pobo play', '!') ):

        # Get command
        try:
            cmd = re.split('pobo play|!', data['text'])[1].strip()
        
        except IndexError:
            error_msg = 'That is some kind of bogus command you passed me.'
            outputs.append(data['channel'], error_msg)

        # Set cmd here so it can be overwritten below if needed
        game_dict['command'] = cmd

        if cmd.startswith('load'):
            game_loaded = load_game(cmd)
            if game_loaded:
                outputs.append([data['channel'], 'SAVE GAME LOADED'])
            else:
                outputs.append([data['channel'], 'Hmmm...looks like a bougus save file.'])

        # Wipe savegame from memory and start game from scratch
        if cmd == 'restart':
            # Re-init game state
            game_dict['savegame'] = None


        # First time game loads, we don't have a save game state, so use GET request
        if not game_dict['savegame']:
            r = requests.get(game_url)
        else:
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

    soup = BeautifulSoup(request.text)

    # Get response from game server to our command
    response = soup.find('pre').text

    # Clean up response
    response = response.rstrip('&gt;')

    if game_dict['savegame']: 
        response = response.split('&gt;')[-1] # Only get latest response, not all history

    response = response.split('\n', 1)[1] # Get rid of previous command response
    response = response.rstrip()

    return response


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


