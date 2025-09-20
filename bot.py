import os
from pathlib import Path
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.mutable import MutableDict
import random

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
    health = Column(Integer, default=100)
    armor = Column(Integer, default=0)
    coffers = Column(Integer, default=0)
    rank = Column(String,default='Recruit')
    inventory = Column(MutableDict.as_mutable(JSON), default=dict)
    kills = Column(Integer, default=0)
    sieges = Column(Integer, default=0)

Base.metadata.create_all(engine)

ITEMS = {
    "Sword": {"unique": True},
    "Shield": {"unique": True}, 
    "Potion": {"unique": False}
}

Opponents = {

    # Low Tier

    "Footman": {"health": 15, "shield": 0, "level": 'low', "damage": 10},
    "Spearman": {"health": 15,"shield": 5, "level": 'low', "damage": 10},
    "Scout": {"health": 20, "shield": 5, "level": 'low', "damage": 5},
    "Skirmisher": {"health": 20, "shield": 0, "level": 'low', "damage": 5},
    "Spearman": {"health": 25, "shield": 5, "level": 'low', "damage": 10},

    # Middle Tier

    "Vanguard": {"health": 40, "shield": 10, "level": 'mid', "damage": 30},
    "Berserker": {"health": 50, "shield": 5, "level": 'mid', "damage": 25},
    "Duelist": {"health": 45, "shield": 10, "level": 'mid', "damage": 35},
    "Executioner": {"health": 55, "shield": 15, "level": 'mid', "damage": 35},
    "Shieldbearer": {"health": 50, "shield": 10, "level": 'mid', "damage": 40},

    # High Tier

    "Captain": {"health": 75, "shield": 70, "level": 'high', "damage": 75},
    "Champion": {"health": 80, "shield": 50, "level": 'high', "damage": 70},
    "Knight-Commander": {"health": 90, "shield": 75, "level": 'high', "damage": 70},
    "Warmaster": {"health": 100, "shield": 20, "level": 'high', "damage": 80},
    "Castellan": {"health": 85, "shield": 40, "level": 'high', "damage": 70},

    # Very High Tier

    "High Marshal": {"health": 100, "shield": 85, "level": 'veryhigh', "damage": 90},
    "Lord Protector": {"health": 100, "shield": 100, "level": 'veryhigh', "damage": 85},
    "Grandmaster": {"health": 100, "shield": 95, "level": 'veryhigh', "damage": 95},
    "Conqueror": {"health": 100, "shield": 100, "level": 'veryhigh', "damage": 100},
    "The Harbinger": {"health": 100, "shield": 100, "level": 'veryhigh', "damage": 100},
}

def add_item(user, item_name):
    item_def = ITEMS.get(item_name, {"unique": False})

    if user.inventory is None:
        user.inventory = {}

    if item_def["unique"]:
        if item_name in user.inventory:
            return False
        user.inventory[item_name] = 1
    else:
        user.inventory[item_name] = user.inventory.get(item_name, 0) + 1

    return True

# Events/Commands

@app.command('/wl-help')
def help(ack, respond, command):
    ack()
    respond("""> *All Available Commands:*
> 
> */satchel* -> Opens Your Satchel To View Your Items.   
> */rank ->* Shows Your/A Tagged User's Current Rank.   
> */coffers* -> Shows How Many Coffers You/A Tagged User Has.
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
        items = []
        for name, qty in user.inventory.items():
            if qty > 1:
                items.append(f"{name} x{qty}")
            else:
                items.append(name)
        respond("Your Satchel contains: " + ", ".join(items))

@app.command('/rank')
def rank(ack, respond, command):
    ack()

    text = (command.get("text") or "").strip()

    if text.startswith('@'):
        slack_user_id = text
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
        respond(f"<{slack_user_id}>'s Current Rank Is: {user.rank}")

@app.command('/coffers')
def coffers(ack, respond, command):
    ack()

    text = (command.get("text") or "").strip()

    if text.startswith('@'):
        slack_user_id = text
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
        respond(f"You Have {user.coffers} Coffers.")
    else:
        respond(f"<{slack_user_id}> Has {user.coffers} Coffers")

@app.command('/siege')
def siege(ack, respond, command):
    ack()

    slack_user_id = command['user_id']

    user = session.query(User).filter_by(slack_id=slack_user_id).first()
    if not user:
        user = User(slack_id=slack_user_id) 
        session.add(user)
        session.commit()  

    Ranks = {
    'Recruit': "low",
    'Raider': 'mid',
    'Champion': 'high',
    'Warchief': 'veryhigh',
    }

    rank = Ranks.get(user.rank, "low")

    randomopp = [name for name, data in Opponents.items() if data["level"] == rank]

    opponent_name = random.choice(randomopp)
    opponent = Opponents[opponent_name]


    respond(f"""*You Have Started a Siege...*

The ground trembles beneath your march as your banners rise high against the dusk.
Drums thunder. Torches blaze.

Your army of steel and fury surrounds the enemy's stronghold, their walls looming in the dying light.
From atop the battlements, shadows gather — archers nocking arrows, captains barking orders.

A chilling silence falls.
The defenders wait.
Your soldiers breathe heavy, gripping spear and shield.

You Stand There, Holding Your Ground, As You Spot An Opponent, It's... 
            
*{opponent_name}*  
{opponent['health']} HP | {opponent['shield']} Shield | {opponent['damage']} Damage | {opponent['level'].capitalize()} Tier
""")
    

@app.command('/admin')
def admin(ack, respond, command):
    ack()
    slack_user_id = command['user_id']

    user = session.query(User).filter_by(slack_id=slack_user_id).first()
    if not user:
        user = User(slack_id=slack_user_id) 
        session.add(user)
        session.commit()  

    user.rank = 'Raider'

    if add_item(user, "Potion"):
        session.commit()
        respond("Added Sword to your inventory!")
    else:
        respond("You already have a Sword!")

    session.commit()



if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["APP_TOKEN"])
    handler.start()