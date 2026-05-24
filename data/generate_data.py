import os
import random
import numpy as np
import pandas as pd

# Define players database with realistic parameters
PLAYERS = {
    'batsmen': {
        'Virat Kohli': {
            'hand': 'Right', 'style': 'Anchor', 'form': 0.92,
            'pace_skill': 0.90, 'spin_skill': 0.82,
            'weakness_lines': ['Outside Off'], 'weakness_lengths': ['Good Length'], 'weakness_paths': ['Out-swinger'],
            'preferred_shots': ['Drive', 'Glance', 'Defensive', 'Lofted Shot'],
            'shot_weights': [0.4, 0.2, 0.25, 0.15]
        },
        'Rohit Sharma': {
            'hand': 'Right', 'style': 'Aggressive', 'form': 0.82,
            'pace_skill': 0.88, 'spin_skill': 0.76,
            'weakness_lines': ['Middle Stump', 'Leg Stump'], 'weakness_lengths': ['Yorker', 'Good Length'], 'weakness_paths': ['In-swinger'],
            'preferred_shots': ['Pull/Hook', 'Drive', 'Slog', 'Defensive'],
            'shot_weights': [0.35, 0.3, 0.2, 0.15]
        },
        'MS Dhoni': {
            'hand': 'Right', 'style': 'Finisher', 'form': 0.86,
            'pace_skill': 0.78, 'spin_skill': 0.92,
            'weakness_lines': ['Outside Off'], 'weakness_lengths': ['Short', 'Good Length'], 'weakness_paths': ['Bouncer', 'Out-swinger'],
            'preferred_shots': ['Slog', 'Ramp/Scoop', 'Defensive', 'Drive'],
            'shot_weights': [0.3, 0.25, 0.3, 0.15]
        },
        'Suryakumar Yadav': {
            'hand': 'Right', 'style': 'Aggressive', 'form': 0.94,
            'pace_skill': 0.92, 'spin_skill': 0.90,
            'weakness_lines': ['Outside Off'], 'weakness_lengths': ['Short'], 'weakness_paths': ['Bouncer'],
            'preferred_shots': ['Ramp/Scoop', 'Sweep', 'Lofted Shot', 'Drive'],
            'shot_weights': [0.3, 0.3, 0.25, 0.15]
        },
        'Rishabh Pant': {
            'hand': 'Left', 'style': 'Aggressive', 'form': 0.78,
            'pace_skill': 0.80, 'spin_skill': 0.88,
            'weakness_lines': ['Outside Off'], 'weakness_lengths': ['Good Length'], 'weakness_paths': ['Out-swinger', 'Cutter'],
            'preferred_shots': ['Sweep', 'Lofted Shot', 'Slog', 'Defensive'],
            'shot_weights': [0.25, 0.3, 0.3, 0.15]
        },
        'Shubman Gill': {
            'hand': 'Right', 'style': 'Anchor', 'form': 0.85,
            'pace_skill': 0.88, 'spin_skill': 0.80,
            'weakness_lines': ['Middle Stump'], 'weakness_lengths': ['Short'], 'weakness_paths': ['Bouncer'],
            'preferred_shots': ['Drive', 'Pull/Hook', 'Glance', 'Defensive'],
            'shot_weights': [0.4, 0.2, 0.2, 0.2]
        }
    },
    'bowlers': {
        'Jasprit Bumrah': {
            'type': 'Fast', 'hand': 'Right', 'speed_min': 138, 'speed_max': 152, 'form': 0.96,
            'control': 0.94, 'variations': ['Yorker', 'Bouncer', 'In-swinger', 'Out-swinger', 'Cutter'],
            'var_weights': [0.3, 0.2, 0.2, 0.15, 0.15]
        },
        'Rashid Khan': {
            'type': 'LegSpin', 'hand': 'Right', 'speed_min': 92, 'speed_max': 102, 'form': 0.90,
            'control': 0.88, 'variations': ['Googly', 'Leg-break', 'Cutter'],
            'var_weights': [0.45, 0.45, 0.1]
        },
        'Mitchell Starc': {
            'type': 'LeftArmFast', 'hand': 'Left', 'speed_min': 136, 'speed_max': 148, 'form': 0.82,
            'control': 0.80, 'variations': ['In-swinger', 'Out-swinger', 'Yorker', 'Bouncer'],
            'var_weights': [0.35, 0.3, 0.2, 0.15]
        },
        'Yuzvendra Chahal': {
            'type': 'LegSpin', 'hand': 'Right', 'speed_min': 78, 'speed_max': 88, 'form': 0.78,
            'control': 0.78, 'variations': ['Leg-break', 'Googly', 'Normal'],
            'var_weights': [0.5, 0.3, 0.2]
        },
        'Ravindra Jadeja': {
            'type': 'Ortho', 'hand': 'Left', 'speed_min': 86, 'speed_max': 96, 'form': 0.86,
            'control': 0.92, 'variations': ['Normal', 'Cutter', 'Off-break'],
            'var_weights': [0.6, 0.3, 0.1]
        }
    }
}

# Extensive list of Indian grounds with specialized characteristics
VENUES = [
    'Wankhede Stadium (Mumbai)',
    'Eden Gardens (Kolkata)',
    'M. Chinnaswamy Stadium (Bengaluru)',
    'M. A. Chidambaram Stadium (Chennai)',
    'Narendra Modi Stadium (Ahmedabad)',
    'Rajiv Gandhi International Stadium (Hyderabad)',
    'Arun Jaitley Stadium (Delhi)',
    'HPCA Stadium (Dharamshala)'
]

WEATHER_CONDITIONS = ['Sunny', 'Humid', 'Overcast', 'Night (Dew)']
BALL_TYPES = ['White Kookaburra', 'SG Test', 'Pink Ball']
LINES = ['Outside Off', 'On the Off Stump', 'Middle Stump', 'Leg Stump', 'Outside Leg']
LENGTHS = ['Short', 'Good Length', 'Full', 'Yorker', 'Full Toss']

def generate_telemetry_data(num_samples=15000):
    np.random.seed(42)
    random.seed(42)
    
    data = []
    
    # Ground specific configurations (Par score, batting/bowling modifiers)
    GROUND_PROPERTIES = {
        'Wankhede Stadium (Mumbai)': {'par': 180, 'pace_bounce': 0.10, 'spin_turn': -0.05, 'dew_impact': 0.15, 'boundary_size': 0.0},
        'Eden Gardens (Kolkata)': {'par': 180, 'pace_bounce': 0.0, 'spin_turn': 0.0, 'dew_impact': 0.10, 'boundary_size': 0.0},
        'M. Chinnaswamy Stadium (Bengaluru)': {'par': 195, 'pace_bounce': -0.05, 'spin_turn': -0.15, 'dew_impact': 0.08, 'boundary_size': 0.25},
        'M. A. Chidambaram Stadium (Chennai)': {'par': 160, 'pace_bounce': -0.10, 'spin_turn': 0.25, 'dew_impact': 0.05, 'boundary_size': -0.10},
        'Narendra Modi Stadium (Ahmedabad)': {'par': 175, 'pace_bounce': 0.05, 'spin_turn': 0.05, 'dew_impact': 0.12, 'boundary_size': -0.05},
        'Rajiv Gandhi International Stadium (Hyderabad)': {'par': 175, 'pace_bounce': -0.02, 'spin_turn': -0.05, 'dew_impact': 0.08, 'boundary_size': 0.05},
        'Arun Jaitley Stadium (Delhi)': {'par': 170, 'pace_bounce': -0.05, 'spin_turn': 0.10, 'dew_impact': 0.08, 'boundary_size': 0.02},
        'HPCA Stadium (Dharamshala)': {'par': 165, 'pace_bounce': 0.15, 'spin_turn': -0.15, 'dew_impact': 0.02, 'boundary_size': 0.0}
    }
    
    for i in range(num_samples):
        # 1. Base Match State Context
        venue = random.choice(VENUES)
        weather = random.choice(WEATHER_CONDITIONS)
        ball_type = random.choice(BALL_TYPES)
        ground_props = GROUND_PROPERTIES[venue]
        
        inning = random.choice([1, 2])
        overs = round(random.uniform(0.1, 19.5), 1)
        # Fix overs decimal to valid cricket overs (.1 to .6)
        int_part = int(overs)
        dec_part = random.randint(1, 6)
        overs = float(f"{int_part}.{dec_part}")
        
        # Approximate wickets lost based on overs
        wick_prob = [0.75, 0.2, 0.04, 0.01] if overs < 6 else ([0.5, 0.3, 0.15, 0.05] if overs < 15 else [0.3, 0.4, 0.2, 0.1])
        wickets = min(9, int(np.random.choice([0, 1, 2, 3], p=wick_prob) + int(overs/2)))
        
        # Ball age correlates with overs
        ball_age = overs
        
        # Select players
        batsman_name = random.choice(list(PLAYERS['batsmen'].keys()))
        bowler_name = random.choice(list(PLAYERS['bowlers'].keys()))
        
        batsman_info = PLAYERS['batsmen'][batsman_name]
        bowler_info = PLAYERS['bowlers'][bowler_name]
        
        # 2. Inning specific targets and chase dynamics
        if inning == 2:
            target_runs = random.randint(ground_props['par'] - 25, ground_props['par'] + 25)
            # Current runs based on target and overs
            runs_ratio = (overs / 20.0) * random.uniform(0.7, 1.2)
            current_runs = min(target_runs - 1, int(target_runs * runs_ratio))
            runs_needed = target_runs - current_runs
            balls_remaining = 120 - int(int_part * 6 + dec_part)
            if balls_remaining <= 0:
                balls_remaining = 6
            required_run_rate = round((runs_needed / (balls_remaining / 6.0)), 2)
            current_run_rate = round((current_runs / (overs if overs > 0 else 0.1)), 2)
        else:
            target_runs = 0
            runs_needed = 0
            balls_remaining = 120 - int(int_part * 6 + dec_part)
            current_runs = int(overs * random.uniform(ground_props['par']/20 - 1.5, ground_props['par']/20 + 1.5))
            required_run_rate = 0.0
            current_run_rate = round((current_runs / (overs if overs > 0 else 0.1)), 2)

        # 3. Delivery Physics Simulation
        variation = np.random.choice(bowler_info['variations'], p=bowler_info['var_weights'])
        
        # Release speed based on bowler type and variation
        speed_base = random.uniform(bowler_info['speed_min'], bowler_info['speed_max'])
        if variation in ['Cutter', 'Slower ball']:
            speed_base -= random.uniform(15, 25) # slower variation
        elif variation == 'Yorker':
            speed_base += random.uniform(1, 3) # extra effort
        speed = round(speed_base, 1)
        
        # Determine pitch landing coordinates
        # Bowlers try to bowl specific lines/lengths based on variation
        if variation == 'Yorker':
            pitch_length = 'Yorker'
            pitch_line = np.random.choice(['On the Off Stump', 'Middle Stump', 'Outside Off'], p=[0.4, 0.4, 0.2])
        elif variation == 'Bouncer':
            pitch_length = 'Short'
            pitch_line = np.random.choice(['Middle Stump', 'Leg Stump', 'Outside Off'], p=[0.5, 0.3, 0.2])
        elif bowler_info['type'] in ['LegSpin', 'Ortho']:
            pitch_length = np.random.choice(['Good Length', 'Full', 'Short', 'Full Toss'], p=[0.5, 0.35, 0.12, 0.03])
            pitch_line = np.random.choice(LINES, p=[0.3, 0.3, 0.2, 0.15, 0.05])
        else:
            pitch_length = np.random.choice(['Good Length', 'Full', 'Short', 'Yorker', 'Full Toss'], p=[0.55, 0.25, 0.12, 0.06, 0.02])
            pitch_line = np.random.choice(LINES, p=[0.4, 0.3, 0.15, 0.10, 0.05])
            
        # 4. Batsman Reaction & Contact Mechanics
        # Batsman's shot selection depends on pitch line/length, and preferred shots
        is_weak_line = pitch_line in batsman_info['weakness_lines']
        is_weak_length = pitch_length in batsman_info['weakness_lengths']
        is_weak_path = variation in batsman_info['weakness_paths']
        
        # Shot decision rules based on ball trajectory
        if pitch_length == 'Short':
            reaction_prob = {'Pull/Hook': 0.5, 'Defensive': 0.2, 'Lofted Shot': 0.1, 'Slog': 0.1, 'Ramp/Scoop': 0.05, 'Glance': 0.05}
        elif pitch_length == 'Yorker':
            reaction_prob = {'Defensive': 0.5, 'Ramp/Scoop': 0.2, 'Drive': 0.1, 'Slog': 0.1, 'Glance': 0.1}
        elif pitch_length == 'Full Toss':
            reaction_prob = {'Slog': 0.4, 'Lofted Shot': 0.3, 'Drive': 0.2, 'Sweep': 0.1}
        elif pitch_line in ['Outside Off', 'On the Off Stump']:
            reaction_prob = {'Drive': 0.4, 'Defensive': 0.3, 'Lofted Shot': 0.15, 'Slog': 0.1, 'Ramp/Scoop': 0.05}
        else: # Leg/Middle stump good length or full
            reaction_prob = {'Sweep': 0.3, 'Glance': 0.3, 'Defensive': 0.2, 'Slog': 0.1, 'Drive': 0.1}
            
        # Filter reaction probabilities based on batsman's allowed/preferred shots
        batsman_shots = batsman_info['preferred_shots']
        valid_reactions = {}
        for shot, prob in reaction_prob.items():
            if shot in batsman_shots or shot == 'Defensive':
                # Boost if it is in preferred list
                weight = 1.8 if shot in batsman_shots else 0.8
                valid_reactions[shot] = prob * weight
                
        # Normalize
        total_weight = sum(valid_reactions.values())
        reactions = list(valid_reactions.keys())
        react_probs = [v / total_weight for v in valid_reactions.values()]
        reaction = np.random.choice(reactions, p=react_probs)

        # 5. Contact Quality Calculation
        # Quality depends on: batsman skill vs bowler skill, form, and weaknesses
        batsman_form = batsman_info['form']
        bowler_form = bowler_info['form']
        
        is_fast_bowler = bowler_info['type'] in ['Fast', 'LeftArmFast']
        skill_factor = batsman_info['pace_skill'] if is_fast_bowler else batsman_info['spin_skill']
        
        # Base skill difference
        skill_diff = skill_factor * batsman_form - bowler_info['control'] * bowler_form
        
        # Ground specific modifications:
        if is_fast_bowler:
            # Fast bowlers get control/bounce boosts at HPCA Dharamshala or Wankhede
            skill_diff -= ground_props['pace_bounce'] * 0.5
        else:
            # Spinners get turn boosts at Chepauk or Jaitley
            skill_diff -= ground_props['spin_turn'] * 0.5
            
        # Penalty for weaknesses
        penalty = 0.0
        if is_weak_line: penalty += 0.15
        if is_weak_length: penalty += 0.15
        if is_weak_path: penalty += 0.2
            
        # Environmental factors
        # Overcast/Humid increases swing, making contact slightly harder against fast bowlers
        # Dharamshala cool weather boosts fast bowling swing even more
        if weather in ['Overcast', 'Humid'] and is_fast_bowler and ball_age < 6.0:
            penalty += 0.12 if venue == 'HPCA Stadium (Dharamshala)' else 0.08
            
        # Dew makes gripping spin hard, spinner skill decreases, batsman benefits
        if weather == 'Night (Dew)' and not is_fast_bowler:
            # Dew impact depends on ground dew factor
            skill_diff += ground_props['dew_impact']
            
        final_score = skill_diff - penalty + random.uniform(-0.3, 0.3)
        
        # Categorize contact quality based on final_score
        if final_score < -0.4:
            contact = 'Missed'
        elif final_score < -0.15:
            contact = 'Edge'
        elif final_score < 0.15:
            contact = 'Weak'
        elif final_score < 0.45:
            contact = 'Solid'
        else:
            contact = 'Perfect'
            
        # Fine-tune contact based on shot selection vs delivery
        if reaction == 'Defensive':
            # Defensive shots rarely get perfect contact but also rarely miss/edge
            contact = np.random.choice(['Weak', 'Solid', 'Missed'], p=[0.7, 0.25, 0.05])
            
        # 6. Runs & Wicket Outcomes
        runs_scored = 0
        is_wicket = 0
        
        # Ground boundary size modifier (Chinnaswamy boosts boundaries, Chepauk reduces)
        boundary_modifier = ground_props['boundary_size']
        
        if contact == 'Perfect':
            # Fours and Sixes probability affected by ground size
            four_prob = max(0.2, 0.5 + boundary_modifier)
            six_prob = max(0.1, 0.4 + boundary_modifier)
            denom = four_prob + six_prob + 0.1
            runs_scored = np.random.choice([4, 6, 2], p=[four_prob/denom, six_prob/denom, 0.1/denom])
            is_wicket = 0
        elif contact == 'Solid':
            # Boost boundary chance slightly if boundary size is small
            four_chance = max(0.05, 0.2 + boundary_modifier)
            other_denom = 0.45 + 0.25 + four_chance + 0.08 + 0.02
            runs_scored = np.random.choice([1, 2, 4, 0, 6], p=[0.45/other_denom, 0.25/other_denom, four_chance/other_denom, 0.08/other_denom, 0.02/other_denom])
            is_wicket = 0
        elif contact == 'Weak':
            runs_scored = np.random.choice([0, 1, 2], p=[0.5, 0.45, 0.05])
            # Small chance of soft dismissal (caught in outfield)
            # Outfield catch is more likely at huge stadiums like Narendra Modi Stadium, less likely at Chinnaswamy
            catch_prob = 0.03 - (boundary_modifier * 0.05) # Chinnaswamy has smaller catch prob
            is_wicket = np.random.choice([0, 1], p=[1 - catch_prob, catch_prob])
        elif contact == 'Edge':
            runs_scored = np.random.choice([0, 1, 4], p=[0.6, 0.3, 0.1])
            # High chance of caught behind/slips
            is_wicket = np.random.choice([0, 1], p=[0.75, 0.25])
        elif contact == 'Missed':
            runs_scored = 0
            # If yorker or good length and middle stump, high bowled/LBW
            if pitch_length in ['Yorker', 'Good Length'] and pitch_line in ['Middle Stump', 'On the Off Stump', 'Leg Stump']:
                is_wicket = np.random.choice([0, 1], p=[0.4, 0.6])
            else:
                is_wicket = np.random.choice([0, 1], p=[0.95, 0.05])
                
        # MS Dhoni finishing boost in last 3 overs of inning 2
        if batsman_name == 'MS Dhoni' and inning == 2 and overs >= 17.0 and runs_scored in [0, 1] and not is_wicket:
            if random.random() < 0.25:
                runs_scored = np.random.choice([4, 6], p=[0.4, 0.6])
                contact = 'Perfect'

        # Wicket updates
        if is_wicket:
            runs_scored = 0
            
        # 7. Win Probability Simulation (Post-delivery state transition)
        # Standard logistic/sigmoid style win probability calculator
        par = ground_props['par']
        if inning == 1:
            projected_runs = current_runs + (runs_scored if not is_wicket else 0) + (120 - int(overs*6)) * (current_run_rate / 6.0 if current_run_rate > 4 else 7.5 / 6.0)
            wickets_penalty = (wickets + is_wicket) * 12 # Penalize based on wickets lost
            metric = (projected_runs - wickets_penalty - par) / 40.0
            win_prob = 1.0 / (1.0 + np.exp(-metric)) # Sigmoid between 0 and 1
            win_prob = np.clip(win_prob, 0.15, 0.85)
        else:
            # Second innings base: runs needed vs balls remaining and wickets
            rem_runs = max(0, runs_needed - (runs_scored if not is_wicket else 0))
            rem_balls = max(1, balls_remaining - 1)
            rem_wicks = 10 - (wickets + is_wicket)
            
            if rem_runs <= 0:
                win_prob = 1.0
            elif rem_wicks <= 0:
                win_prob = 0.0
            else:
                req_rate = (rem_runs / (rem_balls / 6.0))
                wicks_factor = rem_wicks / 10.0
                
                # Heuristic: base probability decreases as req_rate increases, and increases with remaining wickets
                # Wankhede / Modi Stadium dew impact makes chasing easier at night
                dew_bonus = 0.0
                if weather == 'Night (Dew)':
                    dew_bonus = ground_props['dew_impact'] * 0.4
                    
                metric = (12.0 - req_rate) * 0.35 + (wicks_factor - 0.5) * 4.0 + dew_bonus
                win_prob = 1.0 / (1.0 + np.exp(-metric))
                
                # Boundary conditions
                if rem_runs > rem_balls * 6:
                    win_prob = 0.0
                elif rem_runs <= rem_balls * 0.5 and rem_wicks >= 5:
                    win_prob = min(0.98, win_prob + 0.1)

        win_prob = float(np.clip(win_prob, 0.0, 1.0))
        
        data.append({
            'batsman': batsman_name,
            'batsman_hand': batsman_info['hand'],
            'batsman_style': batsman_info['style'],
            'batsman_form': batsman_info['form'],
            'bowler': bowler_name,
            'bowler_type': bowler_info['type'],
            'bowler_form': bowler_info['form'],
            'venue': venue,
            'weather': weather,
            'inning': inning,
            'overs': overs,
            'wickets': wickets,
            'runs_needed': runs_needed,
            'balls_remaining': balls_remaining,
            'current_run_rate': current_run_rate,
            'required_run_rate': required_run_rate,
            'ball_age': ball_age,
            'ball_type': ball_type,
            'bowling_speed_kph': speed,
            'bowling_path_type': variation,
            'pitch_line': pitch_line,
            'pitch_length': pitch_length,
            'batsman_reaction': reaction,
            'shot_contact': contact,
            'runs_scored': runs_scored,
            'is_wicket': is_wicket,
            'win_probability_after': win_prob
        })
        
    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(os.path.abspath('data/ipl_telemetry_dataset.csv')), exist_ok=True)
    df.to_csv('data/ipl_telemetry_dataset.csv', index=False)
    print(f"Dataset generated successfully! Size: {df.shape}")

if __name__ == '__main__':
    generate_telemetry_data()
