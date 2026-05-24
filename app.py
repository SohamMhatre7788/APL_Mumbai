import os
import json
import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional

# Define the FastAPI app
app = FastAPI(title="IPL Player Tactical Analytics Platform")

# In-memory player database
PLAYER_DETAILS = {
    'Virat Kohli': {
        'role': 'Batsman', 'hand': 'Right Hand', 'style': 'Anchor', 'form': 0.92,
        'bio': 'One of the greatest modern-day batsmen, master of run-chases and timing.',
        'pace_rating': 95, 'spin_rating': 85, 'defense_rating': 90, 'aggression_rating': 75,
        'image': 'https://images.unsplash.com/photo-1540747737956-37872404f802?q=80&w=250&auto=format&fit=crop',
        'weakness_lengths': ['Good Length'], 'weakness_paths': ['Out-swinger']
    },
    'Rohit Sharma': {
        'role': 'Batsman', 'hand': 'Right Hand', 'style': 'Aggressive', 'form': 0.82,
        'bio': 'Lethal opening batsman, famous for his elegant pull shots and big scores.',
        'pace_rating': 92, 'spin_rating': 80, 'defense_rating': 80, 'aggression_rating': 90,
        'image': 'https://images.unsplash.com/photo-1531415074968-036ba1b575da?q=80&w=250&auto=format&fit=crop',
        'weakness_lengths': ['Yorker', 'Good Length'], 'weakness_paths': ['In-swinger']
    },
    'MS Dhoni': {
        'role': 'Batsman', 'hand': 'Right Hand', 'style': 'Finisher', 'form': 0.86,
        'bio': 'Legendary captain and finisher, possessing lightning-fast reflexes and cool head.',
        'pace_rating': 80, 'spin_rating': 95, 'defense_rating': 85, 'aggression_rating': 85,
        'image': 'https://images.unsplash.com/photo-1607734834834-d2e85a6a3b2b?q=80&w=250&auto=format&fit=crop',
        'weakness_lengths': ['Short', 'Good Length'], 'weakness_paths': ['Bouncer', 'Out-swinger']
    },
    'Suryakumar Yadav': {
        'role': 'Batsman', 'hand': 'Right Hand', 'style': 'Aggressive (360°)', 'form': 0.94,
        'bio': 'Highly inventive T20 batsman who can hit boundaries all over the ground.',
        'pace_rating': 94, 'spin_rating': 92, 'defense_rating': 70, 'aggression_rating': 98,
        'image': 'https://images.unsplash.com/photo-1568602471122-7832951cc4c5?q=80&w=250&auto=format&fit=crop',
        'weakness_lengths': ['Short'], 'weakness_paths': ['Bouncer']
    },
    'Rishabh Pant': {
        'role': 'Batsman', 'hand': 'Left Hand', 'style': 'Aggressive', 'form': 0.78,
        'bio': 'Fearless left-handed batsman and wicketkeeper, known for audacious lofted shots.',
        'pace_rating': 82, 'spin_rating': 90, 'defense_rating': 75, 'aggression_rating': 92,
        'image': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?q=80&w=250&auto=format&fit=crop',
        'weakness_lengths': ['Good Length'], 'weakness_paths': ['Out-swinger', 'Cutter']
    },
    'Shubman Gill': {
        'role': 'Batsman', 'hand': 'Right Hand', 'style': 'Anchor', 'form': 0.85,
        'bio': 'Technically gifted top-order batsman representing the future of Indian cricket.',
        'pace_rating': 90, 'spin_rating': 84, 'defense_rating': 88, 'aggression_rating': 80,
        'image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=250&auto=format&fit=crop',
        'weakness_lengths': ['Short'], 'weakness_paths': ['Bouncer']
    },
    'Jasprit Bumrah': {
        'role': 'Bowler', 'hand': 'Right Arm', 'style': 'Fast', 'form': 0.96,
        'bio': 'World-class fast bowler with a unique release and deadly yorkers.',
        'speed_rating': 98, 'control_rating': 96, 'variation_rating': 94, 'deception_rating': 98,
        'image': 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?q=80&w=250&auto=format&fit=crop'
    },
    'Rashid Khan': {
        'role': 'Bowler', 'hand': 'Right Arm', 'style': 'Leg Spin', 'form': 0.90,
        'bio': 'Elite Afghan leg-spinner, famous for his quick arm action and unreadable googly.',
        'speed_rating': 75, 'control_rating': 92, 'variation_rating': 95, 'deception_rating': 96,
        'image': 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?q=80&w=250&auto=format&fit=crop'
    },
    'Mitchell Starc': {
        'role': 'Bowler', 'hand': 'Left Arm', 'style': 'Fast', 'form': 0.82,
        'bio': 'Premium left-arm fast bowler, highly destructive with the new swinging ball.',
        'speed_rating': 96, 'control_rating': 80, 'variation_rating': 85, 'deception_rating': 84,
        'image': 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?q=80&w=250&auto=format&fit=crop'
    },
    'Yuzvendra Chahal': {
        'role': 'Bowler', 'hand': 'Right Arm', 'style': 'Leg Spin', 'form': 0.78,
        'bio': 'Cunning leg-spinner, master of flighting the ball and inducing false shots.',
        'speed_rating': 60, 'control_rating': 80, 'variation_rating': 88, 'deception_rating': 86,
        'image': 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?q=80&w=250&auto=format&fit=crop'
    },
    'Ravindra Jadeja': {
        'role': 'Bowler', 'hand': 'Left Arm', 'style': 'Orthodox Spin', 'form': 0.86,
        'bio': 'Accuracy personified, bowls quick defensive overs and exploits dry pitches.',
        'speed_rating': 70, 'control_rating': 98, 'variation_rating': 75, 'deception_rating': 80,
        'image': 'https://images.unsplash.com/photo-1501196354995-cbb51c65aaea?q=80&w=250&auto=format&fit=crop'
    }
}

# Lazy loading of models
models = {}

def get_model(name):
    if name not in models:
        model_path = f"models/{name}.pkl"
        if not os.path.exists(model_path):
            raise HTTPException(status_code=500, detail=f"Model '{name}' not trained yet. Run train_models.py first.")
        models[name] = joblib.load(model_path)
    return models[name]

# Pydantic input schemas
class DeliveryPredictionInput(BaseModel):
    batsman: str
    bowler: str
    bowling_speed_kph: float
    bowling_path_type: str
    pitch_line: str
    pitch_length: str
    weather: str
    ball_type: str
    ball_age: float
    inning: int
    overs: float
    wickets: int
    venue: str

class WinProbabilityInput(BaseModel):
    inning: int
    overs: float
    wickets: int
    runs_needed: int
    balls_remaining: int
    current_run_rate: float
    required_run_rate: float
    venue: str
    weather: str
    batsman: str
    bowler: str

class RecommendationInput(BaseModel):
    batsman: str
    bowler: str
    weather: str
    ball_type: str
    ball_age: float
    venue: str
    mode: Optional[str] = "bowling" # "bowling" or "batting"

# Helper function for live cricbuzz match scraping
def get_mock_live_match(reason: str):
    print(f"Fallback to mock live match. Reason: {reason}")
    return {
        'is_live': False,
        'match_name': "MI vs CSK, IPL Rivalry (Simulation Cache)",
        'venue': "Wankhede Stadium (Mumbai)",
        'weather': "Night (Dew)",
        'inning': 2,
        'overs': 17.2,
        'wickets': 6,
        'runs_needed': 32,
        'balls_remaining': 16,
        'target_runs': 185,
        'current_score': 153,
        'batsman': "MS Dhoni",
        'bowler': "Jasprit Bumrah",
        'weather_details': {'temp_C': '31', 'humidity': '72%', 'desc': 'Partly cloudy'}
    }

def fetch_live_match_state():
    import urllib.request
    import urllib.parse
    import re
    
    url = "https://www.cricbuzz.com/cricket-match/live-scores"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
        # Parse match score pages
        links = re.findall(r'href="(/live-cricket-scores/\d+/[^"]+)"', html)
        if not links:
            return get_mock_live_match("No live matches found on Cricbuzz.")
            
        # Filter for IPL / T20 matches
        ipl_links = [l for l in links if 'premier-league' in l.lower() or 'ipl' in l.lower()]
        target_link = ipl_links[0] if ipl_links else links[0]
        
        match_url = f"https://www.cricbuzz.com{target_link}"
        req_detail = urllib.request.Request(match_url, headers=headers)
        with urllib.request.urlopen(req_detail) as response_detail:
            detail_html = response_detail.read().decode('utf-8')
            
        # Extract meta description
        meta_match = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', detail_html)
        if not meta_match:
            return get_mock_live_match("Could not extract meta description from Cricbuzz page.")
        
        desc = meta_match.group(1).replace('\n', ' ').strip()
        
        # Match venue and city
        stadiums = [
            'Wankhede Stadium (Mumbai)',
            'Eden Gardens (Kolkata)',
            'M. Chinnaswamy Stadium (Bengaluru)',
            'M. A. Chidambaram Stadium (Chennai)',
            'Narendra Modi Stadium (Ahmedabad)',
            'Rajiv Gandhi International Stadium (Hyderabad)',
            'Arun Jaitley Stadium (Delhi)',
            'HPCA Stadium (Dharamshala)'
        ]
        
        selected_venue = "Wankhede Stadium (Mumbai)"
        city = "Mumbai"
        for v in stadiums:
            short_name = v.split(" Stadium")[0]
            if short_name.lower() in detail_html.lower():
                selected_venue = v
                city_match = re.search(r'\(([^)]+)\)', v)
                if city_match:
                    city = city_match.group(1)
                break
                
        # Weather Lookup
        weather_category = "Sunny"
        weather_details = {'temp_C': '30', 'humidity': '60%', 'desc': 'Clear'}
        try:
            weather_url = f"http://wttr.in/{urllib.parse.quote(city)}?format=j1"
            w_req = urllib.request.Request(weather_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(w_req) as w_resp:
                w_data = json.loads(w_resp.read().decode('utf-8'))
                curr = w_data['current_condition'][0]
                temp = curr['temp_C']
                humidity_val = int(curr['humidity'])
                desc_text = curr['weatherDesc'][0]['value']
                weather_details = {'temp_C': temp, 'humidity': f"{humidity_val}%", 'desc': desc_text}
                
                if "rain" in desc_text.lower() or "cloud" in desc_text.lower() or "overcast" in desc_text.lower():
                    weather_category = "Overcast"
                elif humidity_val > 70:
                    weather_category = "Humid"
                else:
                    weather_category = "Sunny"
                    
                if humidity_val > 60:
                    weather_category = "Night (Dew)"
        except Exception as we:
            print("Failed to fetch weather:", we)

        # Parse match score patterns: TEAM runs/wickets (overs)
        score_patterns = re.findall(r'([A-Za-z\d\-]+)\s+(\d+)/(\d+)\s*\((\d+\.?\d*)\)', desc)
        if not score_patterns:
            score_patterns = re.findall(r'([A-Za-z\d\-]+)\s+(\d+)-(\d+)\s*\((\d+\.?\d*)\)', desc)
            
        inning = 1
        runs_needed = 0
        balls_remaining = 120
        target_runs = 0
        current_score = 0
        wickets = 0
        overs = 0.1
        
        if len(score_patterns) >= 2:
            inning = 2
            team1, runs1, wickets1, overs1 = score_patterns[0]
            team2, runs2, wickets2, overs2 = score_patterns[1]
            
            target_runs = int(runs1) + 1
            current_score = int(runs2)
            wickets = int(wickets2)
            overs = float(overs2)
            
            need_match = re.search(r'need\s+(\d+)\s+runs\s+in\s+(\d+)\s+balls', desc, re.I)
            if need_match:
                runs_needed = int(need_match.group(1))
                balls_remaining = int(need_match.group(2))
            else:
                runs_needed = max(1, target_runs - current_score)
                int_overs = int(overs)
                balls_bowled = int((overs - int_overs) * 10)
                balls_remaining = max(1, 120 - (int_overs * 6 + balls_bowled))
        elif len(score_patterns) == 1:
            team1, runs1, wickets1, overs1 = score_patterns[0]
            current_score = int(runs1)
            wickets = int(wickets1)
            overs = float(overs1)
            
            need_match = re.search(r'need\s+(\d+)\s+runs\s+in\s+(\d+)\s+balls', desc, re.I)
            if need_match:
                inning = 2
                runs_needed = int(need_match.group(1))
                balls_remaining = int(need_match.group(2))
                target_runs = current_score + runs_needed
            else:
                inning = 1
                runs_needed = 0
                balls_remaining = max(1, 120 - int(int(overs) * 6 + (overs - int(overs)) * 10))
                target_runs = 0
                
        # Parse active batters
        batsman_list = []
        batsmen_in_parenthesis = re.search(r'\(([^)]+)\)', desc)
        if batsmen_in_parenthesis:
            names = re.findall(r'([A-Za-z\s]+)\s+\d+\(\d+\)', batsmen_in_parenthesis.group(1))
            batsman_list = [n.strip() for n in names if n.strip()]
            
        selected_batsman = "Virat Kohli"
        selected_bowler = "Jasprit Bumrah"
        
        db_batsmen = ['Virat Kohli', 'Rohit Sharma', 'MS Dhoni', 'Suryakumar Yadav', 'Rishabh Pant', 'Shubman Gill']
        db_bowlers = ['Jasprit Bumrah', 'Rashid Khan', 'Mitchell Starc', 'Yuzvendra Chahal', 'Ravindra Jadeja']
        
        batsman_mapped = False
        for b in batsman_list:
            for db_b in db_batsmen:
                last_name = db_b.split(" ")[-1]
                first_name = db_b.split(" ")[0]
                if last_name.lower() in b.lower() or first_name.lower() in b.lower():
                    selected_batsman = db_b
                    batsman_mapped = True
                    break
            if batsman_mapped:
                break
                
        bowler_mapped = False
        for db_b in db_bowlers:
            last_name = db_b.split(" ")[-1]
            if last_name.lower() in detail_html.lower():
                selected_bowler = db_b
                bowler_mapped = True
                break
                
        match_title = re.search(r'<title>([^<]+)</title>', detail_html)
        match_name = match_title.group(1).split(" | ")[-1] if match_title else "Live Cricbuzz Match"
        if "Commentary" in match_name:
            match_name = match_name.split("Commentary - ")[-1]
            
        return {
            'is_live': True,
            'match_name': match_name,
            'venue': selected_venue,
            'weather': weather_category,
            'inning': inning,
            'overs': overs,
            'wickets': wickets,
            'runs_needed': runs_needed,
            'balls_remaining': balls_remaining,
            'target_runs': target_runs,
            'current_score': current_score,
            'batsman': selected_batsman,
            'bowler': selected_bowler,
            'weather_details': weather_details
        }
    except Exception as e:
        print("Scraper error, falling back:", e)
        return get_mock_live_match(f"Scraper error: {e}")

# Live match API endpoint
@app.get("/api/live-match")
def get_live_match():
    """Sync and parse live scores and weather parameters from cricbuzz and wttr.in."""
    state = fetch_live_match_state()
    return JSONResponse(content=state)

@app.get("/api/players")
def get_players():
    """Retrieve all available players and their details."""
    return JSONResponse(content=PLAYER_DETAILS)

@app.post("/api/predict-delivery")
def predict_delivery(payload: DeliveryPredictionInput):
    """Predict batsman reaction, runs scored, and wicket likelihood for a single delivery."""
    try:
        react_model = get_model("batsman_reaction_model")
        runs_model = get_model("runs_model")
        wick_model = get_model("wicket_model")
        
        # Prepare dataframes for sklearn pipelines
        react_df = pd.DataFrame([{
            'batsman': payload.batsman,
            'bowler': payload.bowler,
            'bowling_speed_kph': payload.bowling_speed_kph,
            'bowling_path_type': payload.bowling_path_type,
            'pitch_line': payload.pitch_line,
            'pitch_length': payload.pitch_length,
            'weather': payload.weather,
            'ball_type': payload.ball_type,
            'ball_age': payload.ball_age,
            'inning': payload.inning,
            'overs': payload.overs,
            'wickets': payload.wickets,
            'venue': payload.venue
        }])
        
        # 1. Predict Shot Selection (Reaction)
        predicted_reaction = react_model.predict(react_df)[0]
        react_probs = react_model.predict_proba(react_df)[0]
        react_classes = react_model.classes_
        react_prob_dict = {str(c): float(p) for c, p in zip(react_classes, react_probs)}
        
        # 2. Predict Runs and Wicket based on selected reaction
        out_df = pd.DataFrame([{
            'batsman': payload.batsman,
            'bowler': payload.bowler,
            'bowling_speed_kph': payload.bowling_speed_kph,
            'bowling_path_type': payload.bowling_path_type,
            'pitch_line': payload.pitch_line,
            'pitch_length': payload.pitch_length,
            'weather': payload.weather,
            'ball_type': payload.ball_type,
            'ball_age': payload.ball_age,
            'batsman_reaction': predicted_reaction,
            'venue': payload.venue
        }])
        
        predicted_runs = int(runs_model.predict(out_df)[0])
        runs_probs = runs_model.predict_proba(out_df)[0]
        runs_classes = runs_model.classes_
        runs_prob_dict = {str(c): float(p) for c, p in zip(runs_classes, runs_probs)}
        
        predicted_wicket = int(wick_model.predict(out_df)[0])
        wick_probs = wick_model.predict_proba(out_df)[0]
        # class 1 corresponds to wicket
        wicket_prob = float(wick_probs[1]) if len(wick_probs) > 1 else (float(wick_probs[0]) if predicted_wicket == 1 else 0.0)
        
        # Physical trajectory modifier for frontend canvas animation
        # Calculate horizontal and vertical deviations based on spin/swing
        deviation_x = 0.0
        deviation_y = 0.0
        
        if payload.bowling_path_type == 'In-swinger':
            deviation_x = -0.6 if PLAYER_DETAILS[payload.batsman]['hand'] == 'Right Hand' else 0.6
        elif payload.bowling_path_type == 'Out-swinger':
            deviation_x = 0.6 if PLAYER_DETAILS[payload.batsman]['hand'] == 'Right Hand' else -0.6
        elif payload.bowling_path_type == 'Googly':
            deviation_x = -0.5 if PLAYER_DETAILS[payload.batsman]['hand'] == 'Right Hand' else 0.5
        elif payload.bowling_path_type == 'Leg-break':
            deviation_x = 0.5 if PLAYER_DETAILS[payload.batsman]['hand'] == 'Right Hand' else -0.5
        elif payload.bowling_path_type == 'Off-break':
            deviation_x = -0.4 if PLAYER_DETAILS[payload.batsman]['hand'] == 'Right Hand' else 0.4
            
        # Bounce height depends on pitch length and ground conditions (e.g. Wankhede/Dharamshala are bouncy)
        bounce_height_coeff = 1.0
        if payload.pitch_length == 'Short':
            bounce_height_coeff = 1.6
        elif payload.pitch_length == 'Yorker':
            bounce_height_coeff = 0.3
        elif payload.pitch_length == 'Full':
            bounce_height_coeff = 0.7
        elif payload.pitch_length == 'Full Toss':
            bounce_height_coeff = 1.2
            
        # Bounce multiplier based on venue
        if "Dharamshala" in payload.venue or "Mumbai" in payload.venue:
            bounce_height_coeff *= 1.2
        elif "Chennai" in payload.venue:
            bounce_height_coeff *= 0.8
            
        return JSONResponse(content={
            'batsman_reaction': predicted_reaction,
            'reaction_probabilities': react_prob_dict,
            'runs_scored': predicted_runs,
            'runs_probabilities': runs_prob_dict,
            'is_wicket': predicted_wicket,
            'wicket_probability': wicket_prob,
            'trajectory_mod': {
                'dev_x': deviation_x,
                'bounce_coeff': bounce_height_coeff
            }
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/predict-win-prob")
def predict_win_prob(payload: WinProbabilityInput):
    """Predict the win probability of the batting team after this state."""
    try:
        win_model = get_model("win_prob_model")
        
        batsman_form = PLAYER_DETAILS[payload.batsman]['form']
        bowler_form = PLAYER_DETAILS[payload.bowler]['form']
        
        win_df = pd.DataFrame([{
            'inning': payload.inning,
            'overs': payload.overs,
            'wickets': payload.wickets,
            'runs_needed': payload.runs_needed,
            'balls_remaining': payload.balls_remaining,
            'current_run_rate': payload.current_run_rate,
            'required_run_rate': payload.required_run_rate,
            'venue': payload.venue,
            'weather': payload.weather,
            'batsman_form': batsman_form,
            'bowler_form': bowler_form
        }])
        
        win_prob = float(win_model.predict(win_df)[0])
        win_prob = np.clip(win_prob, 0.0, 1.0)
        
        return JSONResponse(content={
            'win_probability': win_prob,
            'bowling_team_win_probability': 1.0 - win_prob
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tactical-recommendation")
def get_recommendation(payload: RecommendationInput):
    """Perform a search over delivery parameters to find optimal actions for batting or bowling team."""
    try:
        react_model = get_model("batsman_reaction_model")
        runs_model = get_model("runs_model")
        wick_model = get_model("wicket_model")
        
        # Bowling Strategy Mode
        if payload.mode == "bowling":
            bowler_info = PLAYER_DETAILS[payload.bowler]
            
            # Setup search space
            lines = ['Outside Off', 'On the Off Stump', 'Middle Stump', 'Leg Stump', 'Outside Leg']
            lengths = ['Short', 'Good Length', 'Full', 'Yorker', 'Full Toss']
            variations = bowler_info.get('variations', ['Normal'])
            
            avg_speed = (bowler_info.get('speed_min', 120) + bowler_info.get('speed_max', 140)) / 2
            speeds = [avg_speed]
            if 'Cutter' in variations or 'Slower ball' in variations:
                speeds.append(avg_speed - 20.0)
            if len(speeds) == 1:
                speeds.append(avg_speed - 5.0)
                
            recommendations = []
            
            for line in lines:
                for length in lengths:
                    for var in variations:
                        for speed in speeds:
                            react_df = pd.DataFrame([{
                                'batsman': payload.batsman,
                                'bowler': payload.bowler,
                                'bowling_speed_kph': speed,
                                'bowling_path_type': var,
                                'pitch_line': line,
                                'pitch_length': length,
                                'weather': payload.weather,
                                'ball_type': payload.ball_type,
                                'ball_age': payload.ball_age,
                                'inning': 2,
                                'overs': 10.0,
                                'wickets': 3,
                                'venue': payload.venue
                            }])
                            
                            pred_shot = react_model.predict(react_df)[0]
                            
                            out_df = pd.DataFrame([{
                                'batsman': payload.batsman,
                                'bowler': payload.bowler,
                                'bowling_speed_kph': speed,
                                'bowling_path_type': var,
                                'pitch_line': line,
                                'pitch_length': length,
                                'weather': payload.weather,
                                'ball_type': payload.ball_type,
                                'ball_age': payload.ball_age,
                                'batsman_reaction': pred_shot,
                                'venue': payload.venue
                            }])
                            
                            runs_probs = runs_model.predict_proba(out_df)[0]
                            runs_classes = runs_model.classes_
                            expected_runs = float(sum(p * c for p, c in zip(runs_probs, runs_classes)))
                            
                            wick_probs = wick_model.predict_proba(out_df)[0]
                            wicket_prob = float(wick_probs[1]) if len(wick_probs) > 1 else 0.0
                            
                            tactical_score = (wicket_prob * 15.0) - expected_runs
                            
                            recommendations.append({
                                'line': line,
                                'length': length,
                                'variation': var,
                                'speed_kph': round(speed, 1),
                                'expected_runs': round(expected_runs, 2),
                                'wicket_probability': round(wicket_prob, 3),
                                'predicted_shot': pred_shot,
                                'tactical_score': tactical_score
                            })
                            
            recommendations.sort(key=lambda x: x['tactical_score'], reverse=True)
            top_3 = recommendations[:3]
            primary_rec = top_3[0]
            shot = primary_rec['predicted_shot']
            
            field_suggestions = []
            if shot in ['Pull/Hook', 'Slog']:
                field_suggestions = ["Deep Mid-Wicket", "Deep Square Leg", "Long On", "Deep Fine Leg"]
            elif shot in ['Drive', 'Lofted Shot']:
                field_suggestions = ["Mid Off (Cover)", "Extra Cover", "Long Off", "Point"]
            elif shot == 'Sweep':
                field_suggestions = ["Deep Square Leg", "Short Fine Leg", "Mid-Wicket"]
            elif shot in ['Ramp/Scoop']:
                field_suggestions = ["Fine Leg", "Third Man", "Short Fine Leg"]
            else:
                field_suggestions = ["Silly Point", "Short Leg", "Slip", "Wicketkeeper tight"]
                
            if payload.ball_age < 4.0 and primary_rec['variation'] in ['In-swinger', 'Out-swinger']:
                field_suggestions.insert(0, "First Slip")
                if len(field_suggestions) > 4:
                    field_suggestions.pop()
                    
            ground_advice = ""
            if "Chennai" in payload.venue:
                ground_advice = " Chennai pitch offers significant turn. Focus on slow variations."
            elif "Bengaluru" in payload.venue:
                ground_advice = " Small boundary dimensions here at Chinnaswamy! Protect boundary lines."
            elif "Dharamshala" in payload.venue:
                ground_advice = " High altitude and cool air helper! Utilize quick swinging deliveries."
            elif "Mumbai" in payload.venue:
                ground_advice = " Red soil pitch with good bounce. Short bouncers can induce top edges."
                
            return JSONResponse(content={
                'top_recommendations': top_3,
                'field_suggestions': field_suggestions[:4],
                'batsman_weakness_summary': f"Vulnerable to {', '.join(PLAYER_DETAILS[payload.batsman]['weakness_lengths'])} lengths. {ground_advice}"
            })
            
        # Batting Strategy Mode
        else:
            batsman_info = PLAYER_DETAILS[payload.batsman]
            preferred_shots = batsman_info.get('preferred_shots', ['Defensive', 'Drive'])
            
            # Search space for typical bowler deliveries
            lines = ['Outside Off', 'On the Off Stump', 'Middle Stump', 'Leg Stump']
            lengths = ['Short', 'Good Length', 'Full', 'Yorker']
            
            # Bowler properties
            bowler_info = PLAYER_DETAILS[payload.bowler]
            variations = bowler_info.get('variations', ['Normal'])
            avg_speed = (bowler_info.get('speed_min', 120) + bowler_info.get('speed_max', 140)) / 2
            
            shot_recommendations = []
            
            # Evaluate how each preferred shot performs against the range of bowler variations
            for shot in preferred_shots:
                expected_runs_list = []
                wicket_prob_list = []
                
                # Grid sample of delivery types
                for line in lines:
                    for length in lengths:
                        for var in variations:
                            out_df = pd.DataFrame([{
                                'batsman': payload.batsman,
                                'bowler': payload.bowler,
                                'bowling_speed_kph': avg_speed,
                                'bowling_path_type': var,
                                'pitch_line': line,
                                'pitch_length': length,
                                'weather': payload.weather,
                                'ball_type': payload.ball_type,
                                'ball_age': payload.ball_age,
                                'batsman_reaction': shot,
                                'venue': payload.venue
                            }])
                            
                            runs_probs = runs_model.predict_proba(out_df)[0]
                            runs_classes = runs_model.classes_
                            expected_runs = float(sum(p * c for p, c in zip(runs_probs, runs_classes)))
                            
                            wick_probs = wick_model.predict_proba(out_df)[0]
                            wicket_prob = float(wick_probs[1]) if len(wick_probs) > 1 else 0.0
                            
                            expected_runs_list.append(expected_runs)
                            wicket_prob_list.append(wicket_prob)
                            
                avg_runs = float(np.mean(expected_runs_list))
                avg_wick = float(np.mean(wicket_prob_list))
                # Batting score: maximize runs, minimize wicket chance
                batting_score = avg_runs - (avg_wick * 20.0)
                
                shot_recommendations.append({
                    'shot': shot,
                    'expected_runs': round(avg_runs, 2),
                    'wicket_probability': round(avg_wick, 3),
                    'batting_score': batting_score
                })
                
            shot_recommendations.sort(key=lambda x: x['batting_score'], reverse=True)
            
            # Find the most dangerous delivery (max wicket probability for the batsman)
            max_wick_prob = -1.0
            danger_ball = ""
            
            for line in lines:
                for length in lengths:
                    for var in variations:
                        out_df = pd.DataFrame([{
                            'batsman': payload.batsman,
                            'bowler': payload.bowler,
                            'bowling_speed_kph': avg_speed,
                            'bowling_path_type': var,
                            'pitch_line': line,
                            'pitch_length': length,
                            'weather': payload.weather,
                            'ball_type': payload.ball_type,
                            'ball_age': payload.ball_age,
                            'batsman_reaction': 'Drive', # baseline
                            'venue': payload.venue
                        }])
                        wick_probs = wick_model.predict_proba(out_df)[0]
                        w_prob = float(wick_probs[1]) if len(wick_probs) > 1 else 0.0
                        if w_prob > max_wick_prob:
                            max_wick_prob = w_prob
                            danger_ball = f"{var} ({length} at {line})"
                            
            # Convert recommendations format to match top_recommendations schema
            top_rec = []
            for r in shot_recommendations[:3]:
                top_rec.append({
                    'line': 'Varies',
                    'length': 'Varies',
                    'variation': r['shot'],
                    'speed_kph': avg_speed,
                    'expected_runs': r['expected_runs'],
                    'wicket_probability': r['wicket_probability'],
                    'predicted_shot': r['shot'],
                    'tactical_score': r['batting_score']
                })
                
            field_suggestions = ["Vulnerable Areas:", "Protect Off Stump", "Avoid Bouncer Pulls"]
            if len(batsman_info.get('weakness_lines', [])) > 0:
                field_suggestions.append(f"Line Weakness: {batsman_info['weakness_lines'][0]}")
                
            return JSONResponse(content={
                'top_recommendations': top_rec,
                'field_suggestions': field_suggestions[:4],
                'batsman_weakness_summary': f"Hazard Alert! {payload.bowler}'s most dangerous ball is {danger_ball} with a {(max_wick_prob*100):.1f}% wicket rate."
            })
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def get_index():
    index_path = "static/index.html"
    if not os.path.exists(index_path):
        return {"status": "success", "message": "FastAPI is running! Static files are missing."}
    return FileResponse(index_path)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
