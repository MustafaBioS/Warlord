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
    inventory = Column(MutableDict.as_mutable(JSON),  default=lambda: {"Rusty Sword": 1, "Small Health Potion": 2})
    xp = Column(Integer, default=0)
    kills = Column(Integer, default=0)
    sieges = Column(Integer, default=0)

Base.metadata.create_all(engine)

Items = {
    "Shield": {"unique": True}, 
    "Small Health Potion": {"unique": False},
    "Rusty Sword": {"unique": True, "damage": 10},
}

Weapons = {
    "Rusty Sword": {"unique": True, "damage": 10},
}

Healable = {
    "Small Health Potion": {"unique": False, "heal": 20}
}

Armor = {
    "Rusty Armor": {"unique": False, "shield": 20}
}

Opponents = {

    # Very Low Tier

    "Peasant": {"health": 20, "shield": 0, "level": 'verylow', "damage": 10},
    "Militia": {"health": 15, "shield": 0, "level": 'verylow', "damage": 5},
    "Bandit": {"health": 15, "shield": 0, "level": 'verylow', "damage": 7},
    "Thief": {"health": 15, "shield": 2, "level": 'verylow', "damage": 10},
    "Squire": {"health": 20, "shield": 3, "level": 'verylow', "damage": 12},

    # Low Tier

    "Footman": {"health": 30, "shield": 0, "level": 'low', "damage": 20},
    "Spearman": {"health": 35,"shield": 5, "level": 'low', "damage": 16},
    "Scout": {"health": 25, "shield": 5, "level": 'low', "damage": 17},
    "Skirmisher": {"health": 30, "shield": 0, "level": 'low', "damage": 22},
    "Rookie": {"health": 25, "shield": 5, "level": 'low', "damage": 25},

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

raid_Opponents = {

    # Very Low Tier

    "Timid Villager": {"health": 20, "shield": 0, "level": 'verylow', "damage": 10},
    "Scared Farmhand": {"health": 15, "shield": 0, "level": 'verylow', "damage": 7},
    "Scrawny Herdsman": {"health": 15, "shield": 0, "level": 'verylow', "damage": 5},
    "Knife-Wielding Peasant": {"health": 20, "shield": 2, "level": 'verylow', "damage": 10},
    "Village Scavenger": {"health": 15, "shield": 1, "level": 'verylow', "damage": 8},

    # Low Tier

    "Village Guard": {"health": 30, "shield": 5, "level": 'low', "damage": 18},
    "Torchbearer Villager": {"health": 28, "shield": 0, "level": 'low', "damage": 16},
    "Village Scout": {"health": 25, "shield": 5, "level": 'low', "damage": 17},
    "Brawler Villager": {"health": 30, "shield": 0, "level": 'low', "damage": 22},
    "Young Hunter": {"health": 28, "shield": 3, "level": 'low', "damage": 20},

    # Middle Tier

    "Armored Villager": {"health": 40, "shield": 10, "level": 'mid', "damage": 30},
    "Village Protector": {"health": 50, "shield": 5, "level": 'mid', "damage": 25},
    "Blade Villager": {"health": 45, "shield": 10, "level": 'mid', "damage": 35},
    "Hardened Guard": {"health": 55, "shield": 15, "level": 'mid', "damage": 35},
    "Shield Villager": {"health": 50, "shield": 10, "level": 'mid', "damage": 40},

    # High Tier

    "Captain of the Guard": {"health": 75, "shield": 70, "level": 'high', "damage": 75},
    "Elite Villager Fighter": {"health": 80, "shield": 50, "level": 'high', "damage": 70},
    "Blade Commander Guard": {"health": 90, "shield": 75, "level": 'high', "damage": 70},
    "Fierce Watcher Villager": {"health": 100, "shield": 20, "level": 'high', "damage": 80},
    "Iron Castellan Guard": {"health": 85, "shield": 40, "level": 'high', "damage": 70},

    # Very High Tier

    "Shadow Marshal Guard": {"health": 100, "shield": 85, "level": 'veryhigh', "damage": 90},
    "Protector of the Hall Villager": {"health": 100, "shield": 100, "level": 'veryhigh', "damage": 85},
    "Master Duelist Guard": {"health": 100, "shield": 95, "level": 'veryhigh', "damage": 95},
    "Silent Conqueror Villager": {"health": 100, "shield": 100, "level": 'veryhigh', "damage": 100},
    "Blood Harbinger Guard": {"health": 100, "shield": 100, "level": 'veryhigh', "damage": 100},
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
> */satchel* → View the items you currently carry.
> */rank (user)* → Check your rank, or mention a user to see theirs.
> */coffers (user)* → See how many coffers you hold, or mention a user to see theirs.
> */siege* → March with your army into a siege. (Available once every 12 hours, Slight chance to get ambushed if you're a high rank)
> */exit-siege* → Withdraw from your current siege. (Still triggers the siege cooldown)
> */siege-count (user)* → Shows how many sieges you've taken part in, or mention a user to see theirs.
> */attack (weapon)* → Strike your foe with a chosen weapon.
> */kill-count (user)* → Display your kill count, or mention a user to see theirs.
> */raid* → Raid a village with your army. (A smaller siege with a smaller cooldown but less valuable rewards, Slight chance to get ambushed if you're a high rank)
""")

@app.command('/satchel')
def satchel(ack, respond, command):
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
                items.append(f"*{name} (x{qty})*")
            else:
                items.append(f"*{name}*")
        respond("Your Satchel contains: \n\n" + "\n".join(items))

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


siege_stages = [

    # FIRST

"""*You Have Defeated The First Opponent, 
                            
*The clash of steel and cries of battle echo around you as your army relentlessly pushes forward. Each step is hard-won,*
*each swing of the blade a fight for survival.*
                
*Heidi moves with unwavering determination, striking with precision,* 
*while Orpheus wades through the chaos, carving a path through the enemy ranks.*
                
*Bodies fall and walls tremble under the weight of war, yet your forces press on, battered but unbroken.*
*You press deeper into the castle, victory almost within reach...*
                
*Inside the castle's halls, you search for spoils.*
*Your eyes catch a chest gleaming in the torchlight... but as you reach for it, the air shifts.*
*From the shadows, a new opponent emerges, it's...*""",

    # SECOND

"""*Smoke and screams fill the courtyard, the air thick with ash and steel.*  
*Arrows rain from the battlements, clattering against shields and biting into the earth around you.*  
                
*Heidi raises her shield high, pushing through the storm, each step forward a defiance of death itself.*  
*Orpheus darts between shadows, his blade flashing like lightning as he fells archers before they can loose another shot.*  
                
*The clash of armies surges around you, but your path remains clear, carved by their unyielding strength.*  
*The defenders cry out in desperation, their walls trembling beneath your relentless assault.*  
                
*As you reach the heart of the courtyard, silence falls for but a moment.*  
*The smoke parts... and another foe steps forth to challenge you, it's...*""",

    # THIRD

"""*The halls of the keep stretch before you, torches guttering against stone walls as shadows twist and stretch.*  
*Your boots strike the bloodstained floor in rhythm with the drum of battle beyond the walls.*  
                
*Heidi holds the narrow passage, her shield bracing against spears that strike in vain, each clang echoing in the darkness.*  
*Orpheus slips past defenders with deadly precision, his strikes so swift the enemy crumbles before they even realize their fate.*  
                
*The air grows thick with smoke, the cries of the dying mingling with the groan of straining stone.*  
*Victory feels close, yet danger coils tighter with every step deeper into the fortress.*  
                
*At the corridor's end, where the flicker of torchlight dies, a lone figure waits.*  
*Their blade glimmers faintly in the gloom... it's...*""",

    # FOURTH
    
"""*With a thunderous crash, the throne room doors burst open, their iron hinges screaming in protest.*  
*Your army halts at the threshold, the roar of battle muffled as silence consumes the chamber.*  
                
*Heidi, bloodied but steadfast, steadies her shield at your side, her breath ragged but her resolve unbroken.*  
*Orpheus twirls his sword with a predator's calm, his eyes burning with anticipation as he whispers, "This ends here."*  
                
*The grand chamber looms vast and cold, its gilded banners torn and blackened by war.*  
*Each step toward the throne resounds like thunder, the weight of destiny pressing down upon you all.*  
                
*And there, before the throne of the broken keep, the final challenger steps forward, their presence filling the room like a storm.*  
*The last battle begins—it's...*""",

    # WIN

"""*and for the first time, the battlefield grows quiet.*  
*Orpheus wipes his blade, Heidi steadies her breath, and your army bloodied but unbroken, raises a cheer of triumph.*  

*Together, you march back through the smoke and ruin, the castle behind you left in ashes.*
*The gates of the Warlord's camp open wide as your forces return, weary yet victorious.*

*The Warlord regards you with a hard gaze, his expression unreadable. Then, a rare smile breaks across his face.*  
*"Another siege claimed... perhaps you are worthy after all."*"""

]

raid_stages = [

    # FIRST

    """*The village square opens up. Torches flicker, casting long shadows over overturned carts and scattered goods.*  
*Villagers run for cover, their cries mixing with the clang of metal and distant alarm bells.*  

*Heidi dives behind a barrel, creating a small diversion. Orpheus moves like a shadow, striking silently, taking enemies before they can react.*  
*You push forward, careful with every step. Every sound could give your position away.*  

*A new opponent steps out, cautious but ready, eyes darting and blade raised. It's...*""",

    # SECOND

"""*You push through narrow alleys and jump over fences, the air thick with smoke, dirt, and the tang of livestock.*  
*Heidi slams doors open to clear your path, shield flashing with every movement. Orpheus darts through chaos, cutting down anyone who gets too close.*  

*The village feels different here—tense, silent in bursts, as if the streets themselves are holding their breath.*  
*Every shadow seems to move, every creak of the floor or rustle of cloth warning of what's ahead.*  

*As you round the corner, the streets widen into a small square. Moonlight glints off a chest set against a broken cart, its lock rusted but stubborn.*  
*Heidi pauses, eyes narrowing, sensing danger. Orpheus crouches low, blades ready.*  

*Two opponents step forward together, blocking your path, their weapons gleaming sharply in the flickering torchlight.*  
*The chest waits behind them, silent and tempting, a reward for whoever survives the coming clash.*  
*The air hangs heavy with tension, every second stretching longer. It's...*"""

]

@app.command('/use')
def use(ack, respond, command):
    ack()

    text = (command.get("text") or "").strip()
    item_name = text.title()
    slack_user_id = command['user_id']

    user = session.query(User).filter_by(slack_id=slack_user_id).first()

    if slack_user_id in active_siege:
        container = active_siege
        stages = siege_stages
        battle_type = "siege"

    elif slack_user_id in active_raid:
        container = active_raid     
        stages = raid_stages
        battle_type = "raid"

    else:
        respond("You're Not In The Middle of Any Battle Right Now.")
        return

    if not user:
        user = User(slack_id=slack_user_id)
        session.add(user)
        session.commit()

    else:

        if item_name not in user.inventory:
            respond(f"You Don't Have a *{item_name}* In Your Satchel, Use /satchel To Check Your Items.")
            return
        
        healable = Healable.get(item_name)
        armor = Armor.get(item_name)

        if healable:
            user.health = min(user.health + healable['heal'], 100)

        elif armor:
            user.shield = min(user.shield + armor['shield'], 100)

        else:
            respond(f"*{text}* Is Not a Usable Item.")
            return

        if user.inventory.get(item_name, 0) > 0:
            user.inventory[item_name] -= 1
            if user.inventory[item_name] == 0:
                del user.inventory[item_name]

            session.commit()

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

    elif slack_user_id in active_raid:
        respond("You're Still In The Midst of a Raid, Finish It Before Starting a Siege.")

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
        "Recruit": "verylow",
        "Footman": "verylow",
        "Soldier": "low",
        "Raider": "low",
        "Veteran": "mid",
        "Champion": "mid",
        "Knight": "high",
        "Commander": "high",
        "General": "veryhigh",
        "Conqueror": "veryhigh",
        }

        rank = Ranks.get(user.rank, "verylow")

        randomopp = [name for name, data in Opponents.items() if data["level"] == rank]

        num_opponents = random.randint(3, 5)
        num_opponents = min(num_opponents, max(1, len(randomopp)))

        sampled_names = random.sample(randomopp, num_opponents)

        opponents_list = [
        {"name": name,
        "hp": Opponents[name]["health"],
        "shield": Opponents[name]["shield"],
        "damage": Opponents[name]["damage"],
        "level": Opponents[name]["level"]}
        for name in sampled_names
        ]

        active_siege[slack_user_id] = {
        "opponents": opponents_list,
        "current": 0
        }

        first_opponent = opponents_list[0]

        user.health = 100
        user.shield = user.shield
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
           
*{first_opponent['name']}*

{first_opponent['hp']} HP | {first_opponent['shield']} Shield | {first_opponent['damage']} Damage | {first_opponent['level'].capitalize()} Tier

*Use /attack To FIGHT!*
""")

active_raid = {}
raid_cds = {}
raid_cd_seconds = 3 * 60 * 60

@app.command('/raid')
def raid(ack, respond, command):
    ack()

    slack_user_id = command['user_id']
    now = time.time()

    user = session.query(User).filter_by(slack_id=slack_user_id).first()
    if not user:
        user = User(slack_id=slack_user_id) 
        session.add(user)
        session.commit()  

    if slack_user_id in active_siege:
        respond("You're Still In The Midst of a Siege. Finish It Before Starting a Raid.")

    elif slack_user_id in active_raid:
        respond("You're Already In a Raid. Use *'/attack'* To Continue Fighting!")

    elif slack_user_id in raid_cds:
        elapsed = now - raid_cds[slack_user_id]
        if elapsed < raid_cd_seconds:
            remaining_seconds = int(raid_cd_seconds - elapsed)
            remaininghrs = remaining_seconds // 3600
            remainingmins = (remaining_seconds % 3600) // 60
            if remaininghrs > 0:
                respond(f"You Must Rest Before Doing Another Raid. Please Wait *{remaininghrs}h {remainingmins}m.*")
            else:
                respond(f"You Must Rest Before Doing Another Raid. Please Wait *{remainingmins}m.*")

    else:

        Ranks = {
        "Recruit": "verylow",
        "Footman": "verylow",
        "Soldier": "low",
        "Raider": "low",
        "Veteran": "mid",
        "Champion": "mid",
        "Knight": "high",
        "Commander": "high",
        "General": "veryhigh",
        "Conqueror": "veryhigh",
        }

        rank = Ranks.get(user.rank, "verylow")

        randomopp = [name for name, data in raid_Opponents.items() if data["level"] == rank]

        num_opponents = random.randint(1, 3)
        num_opponents = min(num_opponents, max(1, len(randomopp)))

        sampled_names = random.sample(randomopp, num_opponents)

        opponents_list = [
        {"name": name,
        "hp": raid_Opponents[name]["health"],
        "shield": raid_Opponents[name]["shield"],
        "damage": raid_Opponents[name]["damage"],
        "level": raid_Opponents[name]["level"]}
        for name in sampled_names
        ]

        active_raid[slack_user_id] = {
        "opponents": opponents_list,
        "current": 0
        }

        first_opponent = opponents_list[0]

        user.health = 100
        user.shield = user.shield
        session.commit()

        raid_cds[slack_user_id] = now
        last_attack.pop(slack_user_id, None)

        respond(f"""*You Have Started a Raid...*
                

*You move silently through the village outskirts. Shadows cling to the walls, moonlight glinting off your weapons.*  
*The quiet is broken only by distant dogs and the shuffle of your boots on gravel.*  

*Heidi signals with a nod, moving quickly and deliberately. Orpheus slips between shadows, scanning the area ahead.*  
*Huts and carts line the path, each corner could hide a guard or a trap.*  

*Suddenly, a lone guard appears from the shadows, weapon raised and eyes wide. You hold your breath. It's...*

*{first_opponent['name']}*

{first_opponent['hp']} HP | {first_opponent['shield']} Shield | {first_opponent['damage']} Damage | {first_opponent['level'].capitalize()} Tier""")

        


@app.command('/attack')
def attack(ack, respond, command):
    ack()
    global active_siege, last_attack, siege_stages, active_raid, raid_stages
    

    min_time = 3
    max_time = 8

    text = (command.get("text") or "").strip().title()

    slack_user_id = command['user_id']

    user = session.query(User).filter_by(slack_id=slack_user_id).first()

    if slack_user_id in active_siege:
        container = active_siege
        stages = siege_stages
        battle_type = "siege"

    elif slack_user_id in active_raid:
        container = active_raid     
        stages = raid_stages
        battle_type = "raid"

    else:
        respond("You're Not In The Middle of Any Battle Right Now.")
        return

    active = container[slack_user_id]      

    if not user or not user.inventory:
        respond("You Have No Items To Fight With, Use /satchel To Check Your Inventory.")
        return
    
    if not text:
        respond("Choose a Weapon To Attack With.")
        return

    if text not in user.inventory:
        respond(f"You Don't Have a *{text}* In Your Satchel, Use /satchel To Check Your Items.")
        return
    
    weapon = Weapons.get(text)
    if not weapon:
        respond(f'*{text}* Is Not a Valid Weapon')
        return

    now = time.time()
    last_time = last_attack.get(slack_user_id)
    opponent = active['opponents'][active['current']]

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
                del container[slack_user_id]
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
                del container[slack_user_id]
                respond(f"You Hesitated Too Long... *{opponent['name']}* Struck And Killed You!")
                return
            else:
                respond(f"""You Hesitated! *{opponent['name']}* Strikes First.
                        
You Now have: 
{user.health} HP | {user.shield} Shield""")
                return

    # Opponent Being Hit

    dmg = weapon['damage']

    if opponent['shield'] > 0:
        dmgtaken = min(dmg, opponent['shield'])
        opponent['shield'] -= dmgtaken
        dmg -= dmgtaken

    if dmg > 0:
        opponent['hp'] -= dmg

    last_attack[slack_user_id] = now
    session.commit()

    if opponent['hp'] <= 0:
        user.kills += 1
        session.commit()

        active["current"] += 1
        if active["current"] >= len(active["opponents"]):
            del container[slack_user_id]
            user.xp += 10
            user.coffers += 15
            if battle_type == 'siege':
                user.sieges += 1
            session.commit()
            stage_text = stages[-1] if stages else ""
            respond(f"""*{opponent['name']} falls before your blade.*         
{stage_text}

*You Have Gained 10 XP, And 15 Coffers.*""")

            return
        else:

            total = len(active["opponents"])
            fraction = active['current'] / float(max(1, total - 1))
            stage_index = int(fraction * (len(stages) - 1))
            stage_index = max(0, min(stage_index, len(stages) -1 ))
                
            next_opponent = active["opponents"][active["current"]] 
            stage_text = stages[stage_index] if stages else ""
            respond(f"""*You Have Defeated {opponent['name']}*

{stage_text}

*{next_opponent['name']}*
{next_opponent['hp']} HP | {next_opponent['shield']} Shield | {next_opponent['damage']} Damage | {next_opponent['level'].capitalize()} Tier
                        
*Use /attack To FIGHT!*

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
            del container[slack_user_id]
            if user.xp > 5:
                user.xp -= 5
            else: 
                user.xp = 0
            
            if user.coffers > 10:
                user.coffers -= 10
            else:
                user.coffers = 0
            user.inventory = {}
            session.commit()

            if battle_type == "siege":
                lose_text = """*the battlefield fading into a haze of blood and smoke.*
*Just as the darkness closes in, two familiar figures break through the chaos—Heidi and Orpheus.*
                    
*With fierce determination, they lift your broken form and rush you to the healers' tents.*
*Their strength saves your life, but not the siege.*
*The fortress falls, your army retreats, You, Heidi and Orpheus all return to the Warlord's camp, burdened by defeat.*
                    
*The Warlord sneers as he faces you, saying... "Pathetic... perhaps I chose poorly."*"""

            elif battle_type == 'raid':
                lose_text = f""" testing """

            respond(f"""*{opponent['name']} has struck you down. Your vision blurs,*
                    
{lose_text}

*You Have Lost 5 XP, 10 Coffers, And Everything You Had In Your Satchel.*""")
            
        else:
            time.sleep(1.5)
            respond(f"""*{opponent['name']}* Has Attacked You. 
                    
You Now Have:
                    
{user.health} HP | {user.shield} Shield""")


@app.command('/exit')
def exit(ack, respond, command):
    ack()
    global active_siege, active_raid

    slack_user_id = command['user_id']

    if slack_user_id in active_siege:
        del active_siege[slack_user_id]
        respond ('*You Have Fled The Siege... Traitor.*')
    elif slack_user_id in active_raid:
        del active_raid[slack_user_id]
        respond ('*You Have Fled The Raid... Traitor.*')
    else:
        respond("You're Not In The Middle of Any Battle Right Now.")


@app.command('/kill-count')
def kill_count(ack, respond, command):
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
        respond(f"You Have Killed {user.kills} Enemies.")
    else:
        respond(f"<{slack_user_id}> Has Killed {user.kills} Enemies")


@app.command('/siege-count')
def siege_count(ack, respond, command):
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
        respond(f"You Have Won {user.sieges} Sieges.")
    else:
        respond(f"<{slack_user_id}> Has Won {user.sieges} Sieges")
        
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
        user.shield = 100
        session.commit()
        respond("Added Sword to your inventory!")
    else:
        respond("You already have a Sword!")

    session.commit()



if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["APP_TOKEN"])
    handler.start()