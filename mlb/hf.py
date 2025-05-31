import random

class Player:
    def __init__(self, name, position, team):
        self.name = name
        self.position = position
        self.team = team
        self.stats = {
            'AB': 0, 'H': 0, '1B': 0, '2B': 0, '3B': 0, 'HR': 0,
            'R': 0, 'RBI': 0, 'BB': 0, 'HBP': 0, 'SO': 0, 'SB': 0, 'CS': 0
        }
        # Probabilities for this player
        self.walk_chance = random.uniform(0.06, 0.10)
        self.hit_chance = random.uniform(0.22, 0.28)
        self.single_rate = 0.7
        self.double_rate = 0.2
        self.triple_rate = 0.05
        self.hr_rate = 0.05
        self.hbp_chance = 0.008
        self.fantasy_points = 0

    def calculate_fantasy_points(self):
        self.fantasy_points = (
            self.stats['1B'] * 1 +
            self.stats['2B'] * 2 +
            self.stats['3B'] * 3 +
            self.stats['HR'] * 4 +
            self.stats['BB'] * 0.5 +
            self.stats['HBP'] * 0.5 +
            self.stats['R'] * 1 +
            self.stats['RBI'] * 1 +
            self.stats['SB'] * 1 +
            self.stats['CS'] * (-0.5)
        )
        return self.fantasy_points

class Team:
    def __init__(self, name, players):
        self.name = name
        self.players = players
        self.current_batter_index = 0
        self.score = 0

    def get_current_batter(self):
        return self.players[self.current_batter_index]

    def rotate_batting_order(self):
        self.current_batter_index = (self.current_batter_index + 1) % 9

class Game:
    def __init__(self, away_team, home_team):
        self.away_team = away_team
        self.home_team = home_team
        self.current_inning = 1
        self.half_inning = 'top'
        self.bases = [None, None, None]  # First, Second, Third
        self.outs = 0
        self.current_batting_team = away_team
        self.game_over = False

    def simulate(self):
        while not self.game_over:
            self.simulate_half_inning()
            if self.half_inning == 'top':
                self.half_inning = 'bottom'
                self.current_batting_team = self.home_team
            else:
                self.current_inning += 1
                self.half_inning = 'top'
                self.current_batting_team = self.away_team
                
            if self.current_inning > 9 and self.half_inning == 'top':
                if self.home_team.score > self.away_team.score:
                    self.game_over = True
            
            if self.current_inning > 9 and self.away_team.score > self.home_team.score:
                self.game_over = True
                
            if self.current_inning > 12:
                self.game_over = True

        self.display_results()

    def simulate_half_inning(self):
        self.bases = [None, None, None]
        self.outs = 0
        
        while self.outs < 3:
            batter = self.current_batting_team.get_current_batter()
            self.simulate_plate_appearance(batter)
            self.current_batting_team.rotate_batting_order()
            
            # Check for extra innings and game end conditions
            if self.current_inning > 9 and self.current_batting_team == self.home_team and self.home_team.score > self.away_team.score:
                self.game_over = True
                break

    def simulate_plate_appearance(self, batter):
        batter.stats['AB'] += 1
        outcome = random.random()
        
        if outcome < batter.walk_chance:
            self.handle_walk(batter)
        elif outcome < batter.walk_chance + batter.hbp_chance:
            self.handle_hit_by_pitch(batter)
        elif outcome < batter.walk_chance + batter.hbp_chance + batter.hit_chance:
            hit_roll = random.random()
            batter.stats['AB'] += 1
            batter.stats['H'] += 1
            
            if hit_roll < batter.single_rate:
                batter.stats['1B'] += 1
                self.handle_single(batter)
            elif hit_roll < batter.single_rate + batter.double_rate:
                batter.stats['2B'] += 1
                self.handle_double(batter)
            elif hit_roll < batter.single_rate + batter.double_rate + batter.triple_rate:
                batter.stats['3B'] += 1
                self.handle_triple(batter)
            else:
                batter.stats['HR'] += 1
                self.handle_home_run(batter)
        else:
            batter.stats['SO'] += 1
            self.handle_out(batter)
        
        batter.calculate_fantasy_points()

    def handle_walk(self, batter):
        batter.stats['BB'] += 1
        batter.stats['AB'] -= 1  # Remove the at-bat
        runs = 0
        old_first, old_second, old_third = self.bases
        
        if old_third is not None:
            runs += 1
            old_third.stats['R'] += 1
            old_third.calculate_fantasy_points()
        
        self.bases = [batter, old_first, old_second if old_first else None]
        self.current_batting_team.score += runs
        
        batter.stats['RBI'] += runs
        batter.calculate_fantasy_points()

    def handle_hit_by_pitch(self, batter):
        batter.stats['HBP'] += 1
        batter.stats['AB'] -= 1  # Remove the at-bat
        self.handle_walk(batter)

    def handle_single(self, batter):
        runs = 0
        old_first, old_second, old_third = self.bases
        
        if old_third is not None:
            runs += 1
            old_third.stats['R'] += 1
            old_third.calculate_fantasy_points()
        
        self.bases = [batter, old_first, old_second]
        self.current_batting_team.score += runs
        
        batter.stats['RBI'] += runs
        batter.calculate_fantasy_points()

    def handle_double(self, batter):
        runs = 0
        old_first, old_second, old_third = self.bases
        
        if old_second is not None:
            runs += 1
            old_second.stats['R'] += 1
            old_second.calculate_fantasy_points()
        
        if old_third is not None:
            runs += 1
            old_third.stats['R'] += 1
            old_third.calculate_fantasy_points()
        
        self.bases = [None, batter, old_first]
        self.current_batting_team.score += runs
        
        batter.stats['RBI'] += runs
        batter.calculate_fantasy_points()

    def handle_triple(self, batter):
        runs = 0
        old_first, old_second, old_third = self.bases
        
        if old_first is not None:
            runs += 1
            old_first.stats['R'] += 1
            old_first.calculate_fantasy_points()
        
        if old_second is not None:
            runs += 1
            old_second.stats['R'] += 1
            old_second.calculate_fantasy_points()
        
        if old_third is not None:
            runs += 1
            old_third.stats['R'] += 1
            old_third.calculate_fantasy_points()
        
        self.bases = [None, None, batter]
        self.current_batting_team.score += runs
        
        batter.stats['RBI'] += runs
        batter.calculate_fantasy_points()

    def handle_home_run(self, batter):
        runs = 0
        old_first, old_second, old_third = self.bases
        
        if old_first is not None:
            runs += 1
            old_first.stats['R'] += 1
            old_first.calculate_fantasy_points()
        
        if old_second is not None:
            runs += 1
            old_second.stats['R'] += 1
            old_second.calculate_fantasy_points()
        
        if old_third is not None:
            runs += 1
            old_third.stats['R'] += 1
            old_third.calculate_fantasy_points()
        
        runs += 1  # Batter's run
        batter.stats['R'] += 1
        batter.calculate_fantasy_points()
        
        self.bases = [None, None, None]
        self.current_batting_team.score += runs
        
        batter.stats['RBI'] += runs
        batter.calculate_fantasy_points()

    def handle_out(self, batter):
        self.outs += 1
        batter.stats['SO'] += 1

    def display_results(self):
        print("Final Game Simulation:")
        print(f"{self.away_team.name}: {self.away_team.score}")
        print(f"{self.home_team.name}: {self.home_team.score}")
        
        print("\nFantasy Points:")
        all_players = self.away_team.players + self.home_team.players
        for player in sorted(all_players, key=lambda p: p.fantasy_points, reverse=True):
            print(f"{player.name} ({player.team.name}): {player.fantasy_points:.2f} FP")

def create_sample_teams():
    positions = ['C', '1B', '2B', 'SS', '3B', 'LF', 'CF', 'RF', 'DH']
    away_players = [Player(f"Away Player {i+1}", positions[i], "Away Team") for i in range(9)]
    home_players = [Player(f"Home Player {i+1}", positions[i], "Home Team") for i in range(9)]
    
    return Team("Away Team", away_players), Team("Home Team", home_players)

if __name__ == "__main__":
    away_team, home_team = create_sample_teams()
    game = Game(away_team, home_team)
    game.simulate()