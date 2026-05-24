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

# Routes
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
    """Perform a grid search over delivery parameters to find the optimal ball against this batsman."""
    try:
        react_model = get_model("batsman_reaction_model")
        runs_model = get_model("runs_model")
        wick_model = get_model("wicket_model")
        
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
        
        # Grid search
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
                        
                        # Score formula: maximize wickets, minimize expected runs
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
                        
        # Sort and select best
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
                
        # Generate specific tactical advice based on ground properties
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
