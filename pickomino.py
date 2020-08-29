import os
import random
import itertools

class KeepingPlayer:
    def __init__(self, name=""):
        self.name = name
        if not name:
            self.name = "KeepingPlayer"

    def get_name(self):
        return self.name

    def choose_die_to_keep(self, rolled_dice, kept_dice, tiles, players_dic, current_player):
        to_keep = max([x for x in rolled_dice if x not in kept_dice])
        return to_keep

    def continue_rolling(self, kept_dice, tiles, players_dic, current_player):
        return random.choice([True, False])


class RandomPlayer:
    def __init__(self, name=""):
        self.name = name
        if not name:
            self.name = "RandomPlayer"

    def get_name(self):
        return self.name

    def choose_die_to_keep(self, rolled_dice, kept_dice, tiles, players_dic, current_player):
        to_keep = random.choice([x for x in rolled_dice if x not in kept_dice])
        return to_keep

    def continue_rolling(self, kept_dice, tiles, players_dic, current_player):
        return random.choice([True, False])

class InteractivePlayer:
    def __init__(self, name):
        self.name = name
        if not name:
            self.name = "InteractivePlayer"
        self.clear_screen_cmd = "clear"
        if os.name == "nt":
            self.clear_screen_cmd = "cls"

    def clear_screen(self):  
        os.system(self.clear_screen_cmd) 

    def display_current_status(self, tiles, players_dic):
        for t in tiles:
            print("|"+str(t[0])+"| ", end="")
        print()
        for t in tiles:
            print("| "+str(t[1])+"| ", end="")
        print()
        print()
        if players_dic[self.name]['taken']:
            print("My Tiles:", players_dic[self.name]['taken'])
        else:
            print("I Have no tiles.")

        for p in players_dic.keys():
            if p != self.name:
                if players_dic[p]['taken']:
                    print(p, "Shows", players_dic[p]['taken'][0], "(+%d more tiles)" % (len(players_dic[p]['taken'])-1))
                else:
                    print(p, "Has no tiles.")

    def get_name(self):
        return self.name

    def choose_die_to_keep(self, rolled_dice, kept_dice, tiles, players_dic, current_player):
        self.clear_screen()
        self.display_current_status(tiles, players_dic)
        print("Kept Dice:", kept_dice, "(%d)" % (sum(kept_dice)))        
        print("Dice:", rolled_dice)
        to_keep = input("Die to keep (1-6)?")
        if to_keep and to_keep in "123456" and int(to_keep) in rolled_dice:
            return int(to_keep)
        return 0

    def continue_rolling(self, kept_dice, tiles, players_dic, current_player):
        while True:
            continue_rolling = input("Continue rolling (Y/N)?")
            if continue_rolling.lower().startswith("y"):
                return True
            elif continue_rolling.lower().startswith("n"):
                return False

class Pickomino:
    def __init__(self):
        pass

    def create_tiles(self):
        tiles = []
        for i in range(16):
            worms = (i) // 4 + 1
            tiles.append([i+21, worms])
        return tiles

    def start_game(self, players):
        self.players = players
        self.players_dic = {}
        for p in players:
            self.players_dic[p] = {'taken':[]}

        self.tiles = self.create_tiles()
        self.current_player = 0

    def handle_dice_rolling(self, player, kept_dice):
        live_dice_number = 8 - len(kept_dice)
        rolled_dice = []
        for i in range(live_dice_number):
            rolled_dice.append(random.choice([x+1 for x in range(6)]))
        rolled_dice.sort()
        live_dice = [x for x in rolled_dice if x not in kept_dice]
        number_to_keep = 0
        if live_dice:
            while number_to_keep==0 or number_to_keep in kept_dice:
                number_to_keep = player.choose_die_to_keep(rolled_dice, kept_dice, self.tiles, 
                                                           self.players_dic,  self.current_player)
        else:
            pass
        return number_to_keep, rolled_dice

    def handle_take_from_tiles(self, kept_dice_total):
        available_tiles = [x[0] for x in self.tiles]
        if kept_dice_total in available_tiles:
            tile_taken = kept_dice_total
        else:
            tile_taken = max([x for x in available_tiles if x < kept_dice_total])
        index = available_tiles.index(tile_taken)
        player_name = self.players[self.current_player]
        player_obj = self.players_dic[player_name]
        player_obj["taken"] = [self.tiles[index]] + player_obj["taken"]
        self.tiles = self.tiles[:index]+self.tiles[index+1:]
        return

    def handle_busted(self):
        player_name = self.players[self.current_player]
        player_obj = self.players_dic[player_name]
        tile_to_return = None
        if player_obj["taken"]:
            tile_to_return = player_obj["taken"][0]
            player_obj["taken"] = player_obj["taken"][1:]        

        if tile_to_return:
            for i in range(len(self.tiles)):
                if self.tiles[i][0]> tile_to_return[0]:
                    break
            self.tiles = self.tiles[:i]+[tile_to_return] + self.tiles[i:]
        if tile_to_return and i == len(self.tiles)-1:
            pass
        else:
            self.tiles = self.tiles[:-1]
        return

    def handle_take_from_player(self, kept_dice_total):
        for p in self.players_dic:
            if self.players_dic[p]["taken"] and self.players_dic[p]["taken"][0][0] == kept_dice_total:
                tile_to_take = self.players_dic[p]["taken"][0]
                self.players_dic[p]["taken"] = self.players_dic[p]["taken"][1:]
                break

        player_name = self.players[self.current_player]
        player_obj = self.players_dic[player_name]
        player_obj["taken"] = [tile_to_take] + player_obj["taken"]

    def get_available_values_to_steal(self):
        available = [p["taken"][0][0] for p in self.players_dic.values() if p["taken"]]
        player_name = self.players[self.current_player]
        if self.players_dic[player_name]["taken"]:
            available = [x for x in available if x!=self.players_dic[player_name]["taken"][0][0]]
        return available       

    def handle_play(self, player):
        if player.get_name() not in self.players_dic.keys():
            print("Player does not exist")
            return False

        values_to_steal = self.get_available_values_to_steal() 

        kept_dice = []
        keep_rolling = True
        while keep_rolling:
            number_to_keep, live_dice = self.handle_dice_rolling(player, kept_dice)
            if not number_to_keep:
                self.handle_busted()
                keep_rolling = False
            else:
                kept_dice = kept_dice + [x for x in live_dice if x == number_to_keep]
                if len(kept_dice) == 8:
                    keep_rolling = False
                else:
                    keep_rolling = player.continue_rolling(kept_dice, self.tiles, self.players_dic, self.current_player)

                if not keep_rolling:
                    kept_dice_total = sum(kept_dice)
                    if 6 not in kept_dice:
                        kept_dice_total = 0

                    if kept_dice_total in values_to_steal:
                        self.handle_take_from_player(kept_dice_total)
                    elif kept_dice_total in [x[0] for x in self.tiles]:
                        self.handle_take_from_tiles(kept_dice_total)
                    elif kept_dice_total >= self.tiles[0][0]:
                        self.handle_take_from_tiles(kept_dice_total)
                    else:
                        self.handle_busted()
        return 

    def switch_player(self):
        self.current_player = self.current_player+1
        if self.current_player == len(self.players):
            self.current_player = 0

    def identify_winner(self):
        winner = ""
        best_score = 0
        for p in self.players_dic.keys():
            score = sum([self.players_dic[p]['taken'][i][1] for i in range(len(self.players_dic[p]['taken']))])
            if score > best_score:
                winner = p
                best_score = score
        return winner, best_score

    def game_on(self):
        if self.tiles:
            return True
        return False

    def dump_state(self):
        state = {}
        state['tiles'] = self.cards
        state['players'] = self.players
        state['players_dic'] = self.players_dic
        state['current_player'] = self.current_player
        return state

    def load_state(self, state):
        self.tiles = state['tiles']
        self.players = state['players']
        self.players_dic = state['players_dic']
        self.current_player = state['current_player']
        return state

def game_manager(player1, player2):
    pickomino = Pickomino()
    pickomino.start_game([player1.get_name(), player2.get_name()])
    players = {player1.get_name(): player1, player2.get_name(): player2}

    while pickomino.game_on():
        player_name = pickomino.players[pickomino.current_player]
        pickomino.handle_play(players[player_name])
        pickomino.switch_player()
    
    winner, score = pickomino.identify_winner()
    return winner


if __name__ == "__main__":
    #player1 = InteractivePlayer("A")
    #player2 = RandomPlayer("B")
    #winner = game_manager(player1, player2)
    #print("The winner is", winner, "with", score, "points.")
    #1/0


    GAMES_TO_PLAY = 1000
    #players = [LowestCardPlayer(), HighestCardPlayer(), GreedyPlayer(), RandomPlayer(), GreedyPlayer2(), GreedyPlayer3(), GreedyPlayer4(), SimulationPlayer()]
    players = [RandomPlayer(),KeepingPlayer()]
    print("Final score after %s games: " % GAMES_TO_PLAY)

    allscores = {}
    for p in players:
        allscores[p.get_name()] = 0
    print(allscores)
    for couple in list(itertools.permutations(players, 2)):
        player1 = couple[0]
        player2 = couple[1]
        score = {player1.get_name():0, player2.get_name():0}
        for i in range(GAMES_TO_PLAY):
            winner = game_manager(player1, player2)
            if winner:
                score[winner] += 1
        print(score)
        allscores[player1.get_name()] += score[player1.get_name()]
        allscores[player2.get_name()] += score[player2.get_name()]

    #print(allscores)
    players.sort(key = lambda x: allscores[x.get_name()])
    for p in players:
        print("%30s | %d" % (p.get_name(), allscores[p.get_name()]))


