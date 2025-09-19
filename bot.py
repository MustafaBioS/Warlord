import os
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.mutable import MutableDict

# Initialization

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = App(token=os.environ["BOT_TOKEN"],)

engine = create_engine("sqlite:///warlord.db", echo=True)
Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()

# DB Models

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    slack_id = Column(String, unique=True)
    gold = Column(Integer, default=0)
    rank = Column(String,default='Recruit')
    inventory = Column(JSON, default={})

Base.metadata.create_all(engine)

# Events/Commands

@app.command('/wl-help')
def help(ack, respond, command):
    ack()
    respond("""All Available Commands:\n
/satchel -> Opens Your Satchel To View Your Items.   
/rank -> Shows Your Current Rank.         
            """)

@app.command('/satchel')
def help(ack, respond, command):
    ack()
    slack_user_id = command['user_id']

    user = session.query(User).filter_by(slack_id=slack_user_id).first()
    if not user:
        user = User(slack_id=slack_user_id)
        session.add(user)
        session.commit()

    if not user.inventory:
        respond("Your Satchel is empty.")
    else:
        items = ", ".join(user.inventory.keys())
        respond(f"Your Satchel contains: {items}")

@app.command('/rank')
def rank(ack, respond, command):
    ack()

    text = command.get('text', '').strip()

    if text.startswith('<@') and text.endswith('>'):
        slack_user_id = text[2:-1].split('|')[0]
        is_self = slack_user_id == command['user_id']
    else:
        slack_user_id = command['user_id']
        is_self = True

    user = session.query(User).filter_by(slack_id=slack_user_id).first()
    if not user:
        user = User(slack_id=slack_user_id)
        session.add(user)
        session.commit()
    
    if is_self:
        respond(f"Your Current Rank Is: {user.rank}")
    else:
        respond(f"<@{slack_user_id}>'s Current Rank Is: {user.rank}")


if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["APP_TOKEN"])
    handler.start()