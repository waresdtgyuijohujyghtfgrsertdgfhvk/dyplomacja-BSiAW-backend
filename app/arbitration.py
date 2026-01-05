import csv
from datetime import datetime

from app import scheduler
from app.models import Game, Turn, Orders, Nation
from csv import reader


@scheduler.task('interval', id='auto_arbitrate', seconds=10, misfire_grace_time=900)
def auto_arbitration():
    with scheduler.app.app_context():
        games = Game.query.filter(Game.ends_at < datetime.now())
        turns_to_arbitrate = []
        # search for ended turns
        for game in games:
            turns_to_arbitrate.append(Turn.query.filter(Turn.game_id == game.id).order_by(Turn.id.desc()).first())
        if len(turns_to_arbitrate) == 0:
            return
        print(turns_to_arbitrate)
        adjacencies = {"adr":[("ven","f"),("tri","f"),("ven","f"),("alb","f"),("ion","f"),("apu","f")],
"aeg":[("gre","f"),("bul","f"),("con","f"),("smy","f"),("eas","f"),("ion","f")]}
        def check_adjacency(src,dst,type):
            possible_destinations = adjacencies.get(src)
            if possible_destinations is None:
                return False
            for dest,route_type in possible_destinations:
                if dest == dst and route_type == type:
                    return True
            return False
        for turn in turns_to_arbitrate:
            # game state load
            board_state_reader = csv.reader(turn.state.splitlines(), delimiter=',')
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
            nation_owners = dict()
            for nation in nations:
                nation_owners.update({nation.id:nation.name[:3].lower()})
            orders:list[Orders] = Orders.query.filter(Orders.turn_id == turn.id).all()
            valid_attacks = []
            valid_supports = []
            valid_reinforcements = []
            valid_convoys = []
            holds = []
            if turn.phase == "spring":
                for order in orders:
                    order_parts = order.payload.split(" ")
                    print(order_parts)
                    # invalid order checks
                    if len(order_parts) < 3:
                        continue
                    if order_parts[0] == "B":
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
                                new_state = {province:(state[0],board_state[candidate[0]][1]),candidate[0]:(board_state[candidate[0]][1],"")}
                                board_state.update(new_state)


            if turn.phase == "spring-disband":
                pass
            if turn.phase == "fall":
                pass
            if turn.phase == "fall-disband":
                pass