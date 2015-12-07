import re
import requests
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


def process_message(data, debug=False):
    """
    Parse incoming message for play command
    """
    global game_dict

    if data['channel'].startswith("C0FVCH2KU"):
        
        # Execute Move Command  
        if data['text'].startswith( ('pobo play', '!') ):

            if 
            try:
                cmd = re.split('pobo play|!', data['text'])[1].strip()

            except IndexError:
                error_msg = 'That is some kind of bogus command you passed me.'
                outputs.append([data['channel'], error_msg])


                if cmd == 'restart':
                    # Re-init game state
                    game_dict['savegame'] = None

                if cmd.startswith('load'):
                    savefile = cmd.split('load')[1]
                    



                game_dict['command'] = cmd

                # First time game loads, we don't have a save game state, so use GET request
                if not game_dict['savegame']:
                    r = requests.get(game_url)
                else:
                    r = requests.post(game_url, data=game_dict)

                soup = BeautifulSoup(r.text)

                # Get response from game server to our command
                output = soup.find('pre').text


                # Clean up output
                output = output.rstrip('&gt;')

                if game_dict['savegame']: 
                    output = output.split('&gt;')[-1] # Only get latest output, not all history

                output = output.split('\n', 1)[1] # Get rid of previous command output
                output = output.rstrip()

                if debug:
                    print output
                else:
                    outputs.append([data['channel'], output])

                # Update global save game state for next time
                game_dict['savegame'] = soup.find('input', {'name': 'savegame'}).get('value').rstrip('\n') # Soup adding line feed?

