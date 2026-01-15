import logging
import random
from datetime import datetime, timedelta
from time import sleep

from app import scheduler,db
from app.models import Game, Turn, Orders, Nation
from csv import reader

@scheduler.task('interval', id='auto_arbitrate', seconds=60, misfire_grace_time=900)
def auto_arbitration():
    sleep(random.random()*10)
    with scheduler.app.app_context() as ctx:
        games = Game.query.filter(Game.ends_at < datetime.now())
        turns_to_arbitrate:list[Turn] = []
        # search for ended turns
        for game in games:
            if game.status != "active":
                continue
            turns_to_arbitrate.append(Turn.query.filter(Turn.game_id == game.id).order_by(Turn.id.desc()).first())
        if len(turns_to_arbitrate) == 0:
            return
        adjacencies = {"adr":[("ven","F"),("tri","F"),("alb","F"),("ion","F"),("apu","F")],
"aeg":[("gre","F"),("bul","F"),("con","F"),("smy","F"),("eas","F"),("ion","F")],
"alb":[("adr","F"),("tri","A"),("tri","F"),("ser","A"),("gre","A"),("gre","F"),("ion","F")],
"ank":[("con","A"),("con","F"),("bla","F"),("arm","F"),("arm","A"),("smy","A")],
"apu":[("adr","F"),("ion","F"),("nap","F"),("nap","A"),("rom","A"),("ven","A"),("ven","F")],
"arm":[("ank","F"),("ank","A"),("bla","F"),("sev","A"),("sev","F"),("syr","A"),("smy","A")],
"bal":[("kie","F"),("den","F"),("swe","F"),("gob","F"),("lvn","F"),("pru","F"),("ber","F")],
"bar":[("stp","F"),("nwy","F"),("nwg","F")],
"bel":[("eng","F"),("nth","F"),("hol","F"),("hol","A"),("ruh","A"),("bur","A"),("pic","A"),("pic","F")],
"ber":[("bal","F"),("pru","F"),("pru","A"),("sil","A"),("mun","A"),("kie","A"),("kie","F")],
"bla":[("rum","F"),("sev","F"),("arm","F"),("ank","F"),("con","F"),("bul","F")],
"boh":[("sil","A"),("gal","A"),("vie","A"),("trl","A"),("mun","A")],
"bre":[("mao","F"),("eng","F"),("pic","F"),("pic","A"),("par","A"),("gas","F"),("gas","A")],
"bud":[("vie","A"),("gal","A"),("rum","A"),("ser","A"),("tri","A")],
"bul":[("rum","F"),("rum","A"),("bla","F"),("con","A"),("con","F"),("aeg","F"),("gre","A"),("gre","F"),("ser","A")],
"bur":[("bel","A"),("ruh","A"),("mun","A"),("mar","A"),("gas","A"),("par","A"),("pic","A")],
"cly":[("nao","F"),("nwg","F"),("edi","A"),("edi","F"),("liv","A"),("liv","F")],
"con":[("bul","A"),("bul","F"),("bla","F"),("ank","A"),("ank","F"),("smy","A"),("smy","F"),("aeg","F")],
"den":[("hel","F"),("nth","F"),("ska","F"),("swe","A"),("swe","F"),("bal","F"),("kie","F"),("kie","A")],
"eas":[("ion","F"),("aeg","F"),("smy","F"),("syr","F")],
"edi":[("cly","F"),("cly","A"),("nwg","F"),("nth","F"),("yor","F"),("yor","A"),("lvp","A")],
"eng":[("iri","F"),("wal","F"),("lon","F"),("bel","F"),("pic","F"),("bre","F"),("mao","F")],
"fin":[("stp","F"),("stp","A"),("gob","F"),("swe","F"),("swe","A"),("nwy","F"),("nwy","A")],
"gal":[("war","A"),("ukr","A"),("rum","A"),("bud","A"),("vie","A"),("boh","A"),("sil","A")],
"gas":[("mao","F"),("bre","A"),("bre","F"),("par","A"),("bur","A"),("mar","A"),("spa","A"),("spa","F")],
"gre":[("ion","F"),("alb","A"),("alb","F"),("ser","A"),("bul","A"),("bul","F"),("aeg","F")],
"gol":[("spa","F"),("mar","F"),("pie","F"),("tus","F"),("tys","F"),("wes","F")],
"gob":[("swe","F"),("fin","F"),("sto","F"),("lvn","F"),("bal","F")],
"hel":[("nth","F"),("den","F"),("kie","F"),("hol","F")],
"hol":[("nth","F"),("hel","F"),("kie","F"),("kie","A"),("ruh","A"),("bel","F"),("bel","A")],
"ion":[("tun","F"),("tys","F"),("nap","F"),("apu","F"),("alb","F"),("gre","F"),("aeg","F"),("eas","F")],
"iri":[("nao","F"),("lvp","F"),("wal","F"),("eng","F"),("mao","F")],
"kie":[("nao","F"),("lvp","F"),("wal","F"),("eng","F"),("mao","F")],
"lvp":[("cly","F"),("cly","A"),("edi","A"),("yor","A"),("wal","F"),("wal","A"),("iri","F"),("nao","F")],
"lvn":[("bal","F"),("gob","F"),("stp","A"),("stp","F"),("mos","A"),("war","A"),("pru","F"),("pru","A")],
"lon":[("wal","F"),("wal","A"),("yor","A"),("yor","F"),("nth","F"),("eng","F")],
"mar":[("wal","F"),("wal","A"),("yor","A"),("yor","F"),("nth","F"),("eng","F")],
"mao":[("nao","F"),("iri","F"),("eng","F"),("bre","F"),("gas","F"),("spa","F"),("por","F"),("naf","F")],
"mos":[("war","A"),("lvn","A"),("stp","A"),("sev","A"),("ukr","A")],
"mun":[("ruh","A"),("kie","A"),("ber","A"),("sil","A"),("boh","A"),("trl","A"),("bur","A")],
"nap":[("rom","A"),("rom","F"),("apu","A"),("apu","F"),("ion","F"),("tys","F")],
"nao":[("nwg","F"),("cly","F"),("lvp","F"),("iri","F"),("mao","F")],
"naf":[("wes","F"),("tun","F"),("tun","A"),("mao","F")],
"nth":[("lon","F"),("yor","F"),("edi","F"),("nwg","F"),("nwy","F"),("ska","F"),("den","F"),("hel","F"),("hol","F"),("bel","F"),("eng","F")],
"nwy":[("nwg","F"),("bar","F"),("stp","A"),("stp","F"),("fin","A"),("swe","F"),("swe","A"),("ska","F"),("nth","F")],
"nwg":[("bar","F"),("nwy","F"),("nth","F"),("edi","F"),("cly","F"),("nao","F")],
"par":[("bre","A"),("pic","A"),("bur","A"),("gas","A")],
"pic":[("eng","F"),("bel","F"),("bel","A"),("bur","A"),("par","A"),("bre","F"),("bre","A")],
"pie":[("lyo","F"),("mar","F"),("mar","A"),("trl","A"),("ven","A"),("tus","F"),("tus","A")],
"por":[("spa","A"),("spa","F"),("mao","F")],
"pru":[("bal","F"),("lvn","F"),("lvn","A"),("war","A"),("sil","A"),("ber","F"),("ber","A")],
"rom":[("tys","F"),("tus","F"),("tus","A"),("ven","A"),("apu","A"),("nap","F"),("nap","A")],
"ruh":[("bel","A"),("hol","A"),("kie","A"),("mun","A"),("bur","A")],
"rum":[("bla","F"),("bul","F"),("bul","A"),("ser","A"),("bud","A"),("gal","A"),("ukr","A"),("sev","F"),("sev","A")],
"ser":[("tri","A"),("bud","A"),("rum","A"),("bul","A"),("gre","A"),("alb","A")],
"sev":[("bla","F"),("rum","F"),("rum","A"),("ukr","A"),("mos","A"),("arm","F"),("arm","A")],
"sil":[("mun","A"),("ber","A"),("pru","A"),("war","A"),("gal","A"),("boh","A")],
"ska":[("nwy","F"),("swe","F"),("den","F"),("nth","F")],
"smy":[("aeg","F"),("con","F"),("con","A"),("ank","A"),("arm","A"),("syr","F"),("syr","A"),("eas","F")],
"spa":[("mao","F"),("gas","F"),("gas","A"),("mar","A"),("mar","F"),("lyo","F"),("wes","F"),("por","F"),("por","A")],
"stp":[("bar","F"),("mos","A"),("lvn","F"),("lvn","A"),("bot","F"),("fin","F"),("fin","A"),("nwy","F"),("nwy","A")],
"swe":[("nwy","F"),("nwy","A"),("fin","F"),("fin","A"),("gob","F"),("bal","F"),("den","F"),("den","A"),("ska","F")],
"syr":[("eas","F"),("smy","F"),("smy","A"),("arm","A")],
"tri":[("adr","F"),("ven","F"),("ven","A"),("ven","A"),("trl","A"),("vie","F"),("bud","A"),("ser","F"),("alb","A")],
"tun":[("eas","F"),("smy","F"),("smy","A"),("arm","A")],
"tus":[("lyo","F"),("pie","F"),("pie","A"),("ven","A"),("rom","F"),("rom","A"),("tys","A")],
"trl":[("mun","A"),("boh","A"),("vie","A"),("tri","A"),("ven","A"),("pie","A")],
"tys":[("lyo","F"),("tus","F"),("rom","F"),("nap","F"),("ion","F"),("tun","F"),("wes","F")],
"ukr":[("war","A"),("mos","A"),("sev","A"),("rum","A"),("gal","A")],
"ven":[("adr","F"),("apu","F"),("apu","A"),("rom","A"),("tun","A"),("pie","A"),("trl","A"),("tri","F"),("tri","A")],
"vie":[("trl","A"),("boh","A"),("gal","A"),("bud","A"),("tri","A")],
"wal":[("iri","F"),("lvp","F"),("lvp","A"),("yor","A"),("lon","F"),("lon","A"),("eng","F")],
"war":[("pru","A"),("lvn","A"),("mos","A"),("ukr","A"),("gal","A"),("sil","A")],
"wes":[("spa","F"),("lyo","F"),("tys","F"),("tun","F"),("naf","F")],
"yor":[("nth","F"),("lon","F"),("lon","A"),("wal","A"),("lvp","A"),("edi","F"),("edi","A")],}
        def check_adjacency(src,dst,type):
            possible_destinations = adjacencies.get(src)
            if possible_destinations is None:
                return False
            for dest,route_type in possible_destinations:
                if dest == dst and route_type == type:
                    return True
            return False
        supply_provinces = ["ank","bel","ber","bre","bud","con","den","gre","hol","kie","lvp","lon","mar","mos","mun","nap","nwy","par","por","rom","rum","ser","sev","smy","spa","stp","swe","tri","tun","trl","ven","vie","war"]
        random.shuffle(turns_to_arbitrate)
        for turn in turns_to_arbitrate:
            # game state load
            print(turn.state)
            board_state_reader = reader(turn.state.splitlines(), delimiter=',')
            board_state = dict()
            for row in board_state_reader:
                if len(row) == 1:
                    board_state.update({row[0]: ('', '')})
                    continue
                if len(row) == 2:
                    board_state.update({row[0]: (row[1], '')})
                    continue
                board_state.update({row[0]: (row[1], row[2])})
            nations:list[Nation] = Nation.query.filter_by(game_id = turn.game_id).all()
            nation_owners:dict[int,str] = dict()
            for nation in nations:
                nation_owners.update({nation.id:nation.name[:3].lower()})
            orders:list[Orders] = Orders.query.filter(Orders.turn_id == turn.id).all()
            valid_attacks = []
            valid_supports = []
            valid_reinforcements = []
            valid_convoys = []
            holds = []
            new_turn = Turn()
            new_turn.game_id = turn.game_id
            new_turn.number = turn.number + 1
            if turn.phase == "spring":
                new_turn.phase = "spring-disband"
                for order in orders:
                    order_parts = order.payload.split(" ")
                    # general invalid order checks
                    if len(order_parts) < 3:
                        continue
                    if order_parts[0] != "F" and order_parts[0] != "A":
                        continue
                    order_source = board_state[order_parts[1]]
                    if order_source[1] == "":
                        continue
                    if order_source[1][0] == "f" and order_parts[0] == "A":
                        continue
                    if order_source[1][0] == "a" and order_parts[0] == "F":
                        continue
                    if nation_owners[order.player_id] not in order_source[1]:
                        continue
                    if order_parts[2] == "h" or order_parts[2] == "holds": # syntax: <unit type F/A> <source province> h
                        holds.append(order)
                        continue
                    if order_parts[2] == "-" or order_parts[2] == "->": # syntax: <unit type F/A> <source province> - <destination province>
                        if not check_adjacency(order_parts[1], order_parts[3], order_parts[0]):
                            continue
                        valid_attacks.append(order)
                    if len(order_parts) < 4:
                        continue
                    if order_parts[2] == "r" or order_parts[2] == "rei": # syntax: <unit type F/A> <source_province> r <reinforced unit type F/A> <reinforced province>
                        if not check_adjacency(order_parts[1], order_parts[4], order_parts[0]):
                            continue
                        valid_reinforcements.append(order)
                    if len(order_parts) < 5:
                        continue
                    if order_parts[2] == "s" or order_parts[2] == "sup": # syntax: <unit type F/A> <source province> s <supported unit type F/A> <supported unit source> <supported unit destination>
                        if not check_adjacency(order_parts[1], order_parts[4], order_parts[0]):
                            continue
                        if not check_adjacency(order_parts[1], order_parts[5], order_parts[0]):
                            continue
                        if not check_adjacency(order_parts[4], order_parts[5], order_parts[3]):
                            continue
                        valid_supports.append(order)

                    if order_parts[2] == "c" or order_parts[2] == "con":
                        if not check_adjacency(order_parts[1], order_parts[4], order_parts[0]):
                            continue
                        if not check_adjacency(order_parts[1], order_parts[5], order_parts[0]):
                            continue
                        valid_convoys.append(order)
                successful_supports = []
                for support in valid_supports:
                    support_order_parts:list[str] = support.payload.split(" ")
                    for attack in valid_attacks:
                        attack_order_parts:list[str] = attack.payload.split(" ")
                        if support_order_parts[1] == attack_order_parts[3]:
                            continue
                    successful_supports.append(support)
                successful_reinforcements = []
                for reinforcement in valid_reinforcements:
                    reinforcement_order_parts: list[str] = reinforcement.payload.split(" ")
                    for attack in valid_attacks:
                        attack_order_parts: list[str] = attack.payload.split(" ")
                        if reinforcement_order_parts[1] == attack_order_parts[3]:
                            continue
                    successful_reinforcements.append(support)
                # attack resolution
                while len(valid_attacks) > 0:
                    for province, state in board_state.items():
                        province_candidates:list[tuple[str,int]] = []
                        for attack in valid_attacks:
                            attack_order_parts:list[str] = attack.payload.split(" ")
                            if province == attack_order_parts[3]:
                                attack_strength = 1
                                defense_strength = 0
                                for support in successful_supports:
                                    support_order_parts: list[str] = support.split(" ")
                                    if support_order_parts[4] == attack_order_parts[1] and support_order_parts[5] == attack_order_parts[3]:
                                        attack_strength+=1
                                province_candidates.append((attack_order_parts[1],attack_strength))
                                valid_attacks.remove(attack)
                            if board_state[province][1] != "":
                                defense_strength = 1
                                for reinforcement in successful_reinforcements:
                                    reinforcement_order_parts: list[str] = reinforcement.payload.split(" ")
                                    if reinforcement_order_parts[4] == province:
                                        defense_strength+=1
                            province_candidates.append((province,defense_strength))
                        max_strength = max([x[1] for x in province_candidates])
                        if [x[1] for x in province_candidates].count(max_strength) > 1:
                            continue
                        for candidate in province_candidates:
                            if candidate[1] == max_strength:
                                if candidate[0] == province:
                                    break
                                if board_state[province][1] == "":
                                    new_state = {province:(state[0],board_state[candidate[0]][1]),candidate[0]:(board_state[candidate[0]][1],""),}
                                else:
                                    new_state = {province:(state[0],f"{board_state[candidate[0]][1]}-{state[1]}"),candidate[0]:(board_state[candidate[0]][1],""),} # retreating unit after -
                                board_state.update(new_state)
            if turn.phase == "spring-disband":
                new_turn.phase = "fall"
                for order in orders:
                    # retreat order checks
                    order_parts = order.payload.split(" ") # syntax: syntax: <unit type F/A> <source province> r <destination province>

                    if len(order_parts) != 4:
                        continue
                    order_source = board_state[order_parts[1]]
                    if order_source[1] == "":
                        continue
                    if order_source[1][0] == "f" and order_parts[0] == "A":
                        continue
                    if order_source[1][0] == "a" and order_parts[0] == "F":
                        continue
                    retreat_state = board_state[order_parts[1]][1].split("-")
                    if len(retreat_state) != 2:
                        continue
                    if nation_owners[order.player_id] not in retreat_state[1]:
                        continue
                    if board_state[order_parts[3]] != "":
                        continue
                    new_state = {order_parts[3]:(board_state[order_parts[3][1]],retreat_state[1],),order_parts[1]:(board_state[order_parts[1]],retreat_state[0])}
                    board_state.update(new_state)
                for province, state in board_state.items():
                    state = (state[0],state[1].split("-")[0])
                    board_state.update({province:state})
            if turn.phase == "fall":
                new_turn.phase = "fall-disband"
                for order in orders:
                    order_parts = order.payload.split(" ")
                    # general invalid order checks
                    if len(order_parts) < 3:
                        continue
                    if order_parts[0] != "F" and order_parts[0] != "A":
                        continue
                    order_source = board_state[order_parts[1]]
                    if order_source[1] == "":
                        continue
                    if order_source[1][0] == "f" and order_parts[0] == "A":
                        continue
                    if order_source[1][0] == "a" and order_parts[0] == "F":
                        continue
                    if nation_owners[order.player_id] not in order_source[1]:
                        continue
                    if order_parts[2] == "h" or order_parts[2] == "holds":
                        holds.append(order)
                        continue
                    if order_parts[2] == "-" or order_parts[2] == "->": # syntax: <unit type F/A> <source province> - <destination province>
                        if not check_adjacency(order_parts[1], order_parts[3], order_parts[0]):
                            continue
                        valid_attacks.append(order)
                    if len(order_parts) < 4:
                        continue
                    if order_parts[2] == "r" or order_parts[2] == "rei": # syntax: <unit type F/A> <source_province> r <reinforced unit type F/A> <reinforced province>
                        if not check_adjacency(order_parts[1], order_parts[4], order_parts[0]):
                            continue
                        valid_reinforcements.append(order)
                    if len(order_parts) < 5:
                        continue
                    if order_parts[2] == "s" or order_parts[2] == "sup": # syntax: <unit type F/A> <source province> s <supported unit type F/A> <supported unit source> <supported unit destination>
                        if not check_adjacency(order_parts[1], order_parts[4], order_parts[0]):
                            continue
                        if not check_adjacency(order_parts[1], order_parts[5], order_parts[0]):
                            continue
                        if not check_adjacency(order_parts[4], order_parts[5], order_parts[3]):
                            continue
                        valid_supports.append(order)

                    if order_parts[2] == "c" or order_parts[2] == "con":
                        if not check_adjacency(order_parts[1], order_parts[4], order_parts[0]):
                            continue
                        if not check_adjacency(order_parts[1], order_parts[5], order_parts[0]):
                            continue
                        valid_convoys.append(order)
                successful_supports = []
                for support in valid_supports:
                    support_order_parts:list[str] = support.payload.split(" ")
                    for attack in valid_attacks:
                        attack_order_parts:list[str] = attack.payload.split(" ")
                        if support_order_parts[1] == attack_order_parts[3]:
                            continue
                    successful_supports.append(support)
                successful_reinforcements = []
                for reinforcement in valid_reinforcements:
                    reinforcement_order_parts: list[str] = reinforcement.payload.split(" ")
                    for attack in valid_attacks:
                        attack_order_parts: list[str] = attack.payload.split(" ")
                        if reinforcement_order_parts[1] == attack_order_parts[3]:
                            continue
                    successful_reinforcements.append(support)
                # attack resolution
                while len(valid_attacks) > 0:
                    for province, state in board_state.items():
                        province_candidates:list[tuple[str,int]] = []
                        for attack in valid_attacks:
                            attack_order_parts:list[str] = attack.payload.split(" ")
                            if province == attack_order_parts[3]:
                                attack_strength = 1
                                defense_strength = 0
                                for support in successful_supports:
                                    support_order_parts: list[str] = support.split(" ")
                                    if support_order_parts[4] == attack_order_parts[1] and support_order_parts[5] == attack_order_parts[3]:
                                        attack_strength+=1
                                province_candidates.append((attack_order_parts[1],attack_strength))
                                valid_attacks.remove(attack)
                            if board_state[province][1] != "":
                                defense_strength = 1
                                for reinforcement in successful_reinforcements:
                                    reinforcement_order_parts: list[str] = reinforcement.payload.split(" ")
                                    if reinforcement_order_parts[4] == province:
                                        defense_strength+=1
                            province_candidates.append((province,defense_strength))
                        max_strength = max([x[1] for x in province_candidates])
                        if [x[1] for x in province_candidates].count(max_strength) > 1:
                            continue
                        for candidate in province_candidates:
                            if candidate[1] == max_strength:
                                if candidate[0] == province:
                                    break
                                new_state = {province:(state[0],board_state[candidate[0]][1]),candidate[0]:(board_state[candidate[0]][1],""),}
                                board_state.update(new_state)
            if turn.phase == "fall-disband":
                supply = {
                    "eng":0, "fra":0, "ger":0,
                    "ita":0, "aus":0, "rus":0, "tur":0
                }
                for province, state in board_state.items():
                    if state[1] != "":
                        state = (state[1][1:],state[1])
                        board_state.update({province:state})
                    if province in supply_provinces:
                        if state[0] != "":
                            supply[state[0][1:]] += 1
                if max(supply.values()) > (len(supply_provinces)/2):
                    game_win = True
                else:
                    new_turn.phase = "spring"
                    for province, state in board_state.items():
                        if province in supply_provinces:
                            if state[1] != "":
                                supply[state[0][1:]] -= 1
                    for order in orders:
                        order_parts:list[str] = order.payload.split(" ") # syntax: B <location> <unit type F/A>
                        if len(order_parts) != 3:
                            continue
                        if order_parts[0] != "B":
                            continue
                        order_source = board_state[order_parts[2]]
                        if order_source[1] != "":
                            continue
                        if order_parts[2] != "F" and order_parts[2] != "A":
                            continue
                        if supply[nation_owners[order.player_id]]> 0:
                            supply[nation_owners[order.player_id]] -= 1
                            board_state.update({order_parts[1]:(board_state[order_parts[1]],f"{order_parts[2].lower()}{nation_owners[order.player_id]}")})
                        else:
                            continue
            turn_state = ''
            for province, state in board_state.items():
                turn_state += f"{province},{state[0]},{state[1]}\n"
            new_turn.state = turn_state
            latest_turn = Turn.query.filter(Turn.game_id == game.id).order_by(Turn.id.desc()).first()
            if latest_turn.id!=turn.id:
                continue
            db.session.add(new_turn)
            g:Game = Game.query.filter(Game.id == game.id).first()
            if game_win:
                g.status = "finished"
            else:
                g.ends_at = datetime.now() + timedelta(days=1)
            db.session.add(g)
            logging.info(f"turn {turn.id} arbitration successful")
            db.session.commit()

@scheduler.task('interval', id='auto_start', seconds=60, misfire_grace_time=900)
def auto_start():
    with scheduler.app.app_context():
        games = Game.query.filter(Game.status == 'lobby').all()
        for game in games:
            if len(Nation.query.filter(Nation.game_id == game.id).filter(Nation.player_id is None).all()) == 0:
                game.status = "active"
                db.session.add(game)
        db.session.commit()