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
import time

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
    shield = Column(Integer, default=0)
    coffers = Column(Integer, default=0)
    rank = Column(String,default='Recruit')
    inventory = Column(MutableDict.as_mutable(JSON), default=dict)
    kills = Column(Integer, default=0)
    sieges = Column(Integer, default=0)

Base.metadata.create_all(engine)

Items = {
    "Shield": {"unique": True}, 
    "Potion": {"unique": False}
}

Weapons = {
    "Sword": {"unique": True, "damage": 10},
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
    item_def = Items.get(item_name, {"unique": False})

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
> */siege* -> Starts a Siege That The Warlord Will Give You.
> */kill-count* -> Shows The Kill Count.
> */exit-siege* -> Exits From The Current Siege
> */siege-count* -> Shows How Many Sieges You've Done.
> */attack* -> Attacks Your Opponent.
> */admin* -> SALEH USE THIS TO GET A SWORD TO ATTACK WITH.
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

active_siege = {}
cds = {}
siege_cd_seconds = 12 * 60 * 60
last_attack = {}

@app.command('/siege')
def siege(ack, respond, command):
    ack()

    slack_user_id = command['user_id']
    now = time.time()

    user = session.query(User).filter_by(slack_id=slack_user_id).first()
    if not user:
        user = User(slack_id=slack_user_id) 
        session.add(user)
        session.commit()  

    if slack_user_id in active_siege:
        respond("You're Already In a Siege. Use *'/attack'* To Continue Fighting!")


    elif slack_user_id in cds:
        elapsed = now - cds[slack_user_id]
        if elapsed < siege_cd_seconds:
            remaining_seconds = int(siege_cd_seconds - elapsed)
            remaininghrs = remaining_seconds // 3600
            remainingmins = (remaining_seconds % 3600) // 60
            if remaininghrs > 0:
                respond(f"You Must Rest Before Doing Another Siege. Please Wait *{remaininghrs}h {remainingmins}m.*")
            else:
                respond(f"You Must Rest Before Doing Another Siege. Please Wait *{remainingmins}m.*")

    else:

        Ranks = {
        'Recruit': "low",
        'Raider': 'mid',
        'Champion': 'high',
        'Warchief': 'veryhigh',
        }

        rank = Ranks.get(user.rank, "low")

        randomopp = [name for name, data in Opponents.items() if data["level"] == rank]

        opponent_name = random.choice(randomopp)
        opponent_name2 = random.choice(randomopp)
        opponent = Opponents[opponent_name]
        opponent2 = Opponents[opponent_name2]

        active_siege[slack_user_id] = {
            "name": opponent_name,
            "hp": opponent["health"],
            "shield": opponent["shield"],
            "damage": opponent["damage"],
            "level": opponent["level"],
        }

        user.health = 100
        user.shield = 0
        session.commit()

        cds[slack_user_id] = now
        last_attack.pop(slack_user_id, None)

        respond(f"""*You Have Started a Siege...*

*The ground trembles beneath your march as your banners rise high against the dusk.*
*Drums thunder. Torches blaze.*

*Your army of steel and fury surrounds the enemy's stronghold, their walls looming in the dying light.*
*From atop the battlements, shadows gather — archers nocking arrows, captains barking orders.*

*A chilling silence falls.*
*The defenders wait.*
*Your soldiers breathe heavy, gripping spear and shield.*

*You Stand There, Holding Your Ground, As You Spot An Opponent, It's...*
           
*{opponent_name}*  
{opponent['health']} HP | {opponent['shield']} Shield | {opponent['damage']} Damage | {opponent['level'].capitalize()} Tier

*Use /attack To FIGHT!*
""")
        
@app.command('/exit-siege')
def exit(ack, respond, command):
    ack()
    global active_siege

    slack_user_id = command['user_id']

    if slack_user_id in active_siege:
        del active_siege[slack_user_id]
        respond ('*You Have Fled The Siege... Traitor.*')
    else:
        respond("You're Not In a Siege Right Now.")

@app.command('/attack')
def attack(ack, respond, command):
    ack()
    global active_siege, last_attack
    

    min_time = 3
    max_time = 8

    text = (command.get("text") or "").strip().title()

    slack_user_id = command['user_id']

    user = session.query(User).filter_by(slack_id=slack_user_id).first()

    if slack_user_id not in active_siege:
        respond("You're Not In a Siege Right Now.")
        return

    if not user or not user.inventory:
        respond("You Have No Items To Fight With, Use /satchel To Check Your Inventory.")
        return
    
    if not text:
        respond("Choose a Weapon To Attack With.")
        return
    
    if text == "":
        return

    if text not in user.inventory:
        respond(f"You Don't Have a *{text}* In Your Satchel, Use /satchel To Check Your Items.")
        return
    
    weapon = Weapons.get(text)
    if not weapon:
        respond(f'*{text}* Is Not A Valid Weapon')
        return

    now = time.time()
    last_time = last_attack.get(slack_user_id)
    opponent = active_siege[slack_user_id]

    if last_time is not None:
        atime = now - last_time

        if atime < min_time:
            dmg = opponent['damage']
            blocked = min(dmg, user.shield)
            user.shield -= blocked
            dmg -= blocked
            if dmg > 0:
                user.health -= dmg
            session.commit()
            last_attack[slack_user_id] = now

            if user.health <= 0:
                respond(f"You Attacked Too Fast... *{opponent['name']}* Parried And Killed You!")
                return
            else:
                respond(f"""You Attacked Too Fast... *{opponent['name']}* Parried.
You Now have:
{user.health} HP | {user.shield} Shield""")
                return

        elif atime > max_time:
            dmg = opponent['damage']
            blocked = min(dmg, user.shield)
            user.shield -= blocked
            dmg -= blocked
            if dmg > 0:
                user.health -= dmg
            session.commit()
            last_attack[slack_user_id] = now

            if user.health <= 0:
                respond(f"You Hesitated Too Long... *{opponent['name']}* struck and killed you!")
                return
            else:
                respond(f"""You Hesitated! *{opponent['name']}* Strikes First.
You Now have: 
{user.health} HP | {user.shield} Shield""")
                return

    # Opponent Being Hit
    ack()
    dmg = weapon['damage']

    if opponent['shield'] > 0:
        dmgtaken = min(dmg, opponent['shield'])
        opponent['shield'] -= dmgtaken

    if dmg > 0:
        opponent['hp'] -= dmg

    last_attack[slack_user_id] = now

    if opponent['hp'] <= 0:
        Ranks = {
            'Recruit': "low",
            'Raider': 'mid',
            'Champion': 'high',
            'Warchief': 'veryhigh',
        }
        rank = Ranks.get(user.rank, "low")
        randomopp = [name for name, data in Opponents.items() if data["level"] == rank]
        opponent2_name = random.choice(randomopp)
        opponent2 = Opponents[opponent2_name]
        del active_siege[slack_user_id]
        user.kills += 1
        session.commit()
        respond(f"""You Have Defeated *{opponent['name']}*, 
                            
*The clash of steel and cries of battle echo around you as your army relentlessly pushes forward. Each step is hard-won,*
*each swing of the blade a fight for survival.*
                
*Heidi moves with unwavering determination, striking with precision,* 
*while Orpheus wades through the chaos, carving a path through the enemy ranks.*
                
*Bodies fall and walls tremble under the weight of war, yet your forces press on, battered but unbroken.*
*Finally, after a grueling advance, you reach the castle gates, the air thick with smoke and the taste of iron.*
                
*And there, as if waiting for this very moment, emerges a new opponent...*
                
""")        

        return
    else:
        respond(f"""You Strike With Your *{text}*
*{opponent['name']}* Now Has:
{opponent['hp']} HP | {opponent['shield']} Shield""")

        # Player Being Hit

        dmg_to_player = opponent['damage']
        blocked = min(dmg_to_player, user.shield)
        user.shield -= blocked
        dmg_to_player -= blocked
        if dmg_to_player > 0:
            user.health -= dmg_to_player

        session.commit()

        if user.health <= 0:
            time.sleep(1.5)
            respond("You Died.")
        else:
            time.sleep(1.5)
            respond(f"""*{opponent['name']}* Has Attacked You. 
You Now Have:
{user.health} HP | {user.shield} Shield""")
            



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

    if add_item(user, "Sword"):
        session.commit()
        respond("Added Sword to your inventory!")
    else:
        respond("You already have a Sword!")

    session.commit()



if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["APP_TOKEN"])
    handler.start()



# Problem when i try to kill the opponent.