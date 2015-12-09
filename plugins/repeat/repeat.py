import time
crontable = []
outputs = []
msg = None

def process_message(data):
    if 'text' in data.keys() and data['text'].startswith('pobo say'):

        global msg
        if msg:
            msg = msg + ' ' + data['text'].split('pobo say')[1].strip()
        else:
            msg = data['text'].split('pobo say')[1].strip()

        outputs.append([data['channel'], msg])
