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
            print(board_state)
            nations:list[Nation] = Nation.query.filter(Nation.game_id == game.id).all()
            nation_owners = dict()
            for nation in nations:
                nation_owners.update({nation.user_id:nation.name[:3].lower()})
            orders:list[Orders] = Orders.query.filter(Orders.turn_id == turn.id).all()
            valid_attacks = []
            valid_supports = []
            valid_reinforcements = []
            valid_convoys = []
            holds = []
            if turn.phase == "spring":
                for order in orders:
                    order_parts = order.payload.split(" ")
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
                    if nation_owners[Orders.player_id] not in order_source[1]:
                        continue
                    if order_parts[2] == "h" or order_parts[2] == "holds":
                        holds.append(order)
                        continue
                    if order_parts[2] == "-" or order_parts[2] == "->":
                        if not check_adjacency(order_parts[1], order_parts[3], order_parts[0]):
                            continue
                        valid_attacks.append(order)
                    if len(order_parts) < 4:
                        continue
                    if order_parts[2] == "r" or order_parts[2] == "rei":
                        if not check_adjacency(order_parts[1], order_parts[4], order_parts[0]):
                            continue
                        valid_reinforcements.append(order)
                    if len(order_parts) < 5:
                        continue
                    if order_parts[2] == "s" or order_parts[2] == "sup":
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
                for attack in valid_attacks:
                    pass
            if turn.phase == "spring-disband":
                pass
            if turn.phase == "fall":
                for order in orders:
                    order_parts = order.payload.split(" ")
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
                    if nation_owners[Orders.player_id] not in order_source[1]:
                        continue
                    if order_parts[2] == "h" or order_parts[2] == "holds":
                        valid_orders.append(order)
                        continue
                    if order_parts[2] == "-" or order_parts[2] == "->":
                        if not check_adjacency(order_parts[1], order_parts[3], order_parts[0]):
                            continue
                        valid_orders.append(order)
                    if len(order_parts) < 4:
                        continue
                    if order_parts[2] == "r" or order_parts[2] == "rei":
                        if not check_adjacency(order_parts[1], order_parts[4], order_parts[0]):
                            continue
                        valid_orders.append(order)
                    if len(order_parts) < 5:
                        continue
                    if order_parts[2] == "s" or order_parts[2] == "sup":
                        if not check_adjacency(order_parts[1], order_parts[4], order_parts[0]):
                            continue
                        if not check_adjacency(order_parts[1], order_parts[5], order_parts[0]):
                            continue
                        if not check_adjacency(order_parts[4], order_parts[5], order_parts[3]):
                            continue
                        valid_orders.append(order)

                    if order_parts[2] == "c" or order_parts[2] == "con":
                        if not check_adjacency(order_parts[1], order_parts[4], order_parts[0]):
                            continue
                        if not check_adjacency(order_parts[1], order_parts[5], order_parts[0]):
                            continue
                        valid_orders.append(order)
            if turn.phase == "fall-disband":
                pass