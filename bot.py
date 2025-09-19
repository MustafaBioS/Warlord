import os
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler


env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = App(token=os.environ["BOT_TOKEN"],)

@app.command('/wl-help')
def help(ack, respond, command):
    ack()
    respond('Test')


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["APP_TOKEN"])
    handler.start()