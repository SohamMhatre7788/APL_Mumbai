import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_squared_error

def train_and_save_models():
    dataset_path = 'data/ipl_telemetry_dataset.csv'
    
    if not os.path.exists(dataset_path):
        print(f"Dataset not found at {dataset_path}. Please run generate_data.py first.")
        return
        
    print("Loading dataset...")
    df = pd.read_csv(dataset_path)
    print(f"Loaded {df.shape[0]} delivery records.")
    
    # ----------------------------------------------------
    # Model 1: Batsman Reaction Model
    # Predicts shot selected by batsman
    # ----------------------------------------------------
    print("\n--- Training Batsman Reaction Model ---")
    reaction_features = [
        'batsman', 'bowler', 'bowling_speed_kph', 'bowling_path_type', 
        'pitch_line', 'pitch_length', 'weather', 'ball_type', 'ball_age', 
        'inning', 'overs', 'wickets', 'venue'
    ]
    reaction_categorical = [
        'batsman', 'bowler', 'bowling_path_type', 
        'pitch_line', 'pitch_length', 'weather', 'ball_type', 'venue'
    ]
    reaction_numerical = ['bowling_speed_kph', 'ball_age', 'inning', 'overs', 'wickets']
    
    X_react = df[reaction_features]
    y_react = df['batsman_reaction']
    
    X_react_train, X_react_test, y_react_train, y_react_test = train_test_split(
        X_react, y_react, test_size=0.2, random_state=42
    )
    
    preprocessor_react = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), reaction_categorical),
            ('num', StandardScaler(), reaction_numerical)
        ]
    )
    
    pipeline_react = Pipeline([
        ('preprocessor', preprocessor_react),
        ('classifier', RandomForestClassifier(n_estimators=50, max_depth=12, random_state=42, n_jobs=-1))
    ])
    
    print("Fitting Reaction Model...")
    pipeline_react.fit(X_react_train, y_react_train)
    y_react_pred = pipeline_react.predict(X_react_test)
    print(f"Reaction Model Accuracy: {accuracy_score(y_react_test, y_react_pred):.4f}")
    
    # ----------------------------------------------------
    # Model 2 & 3: Outcome Models (Runs and Wickets)
    # Predict runs scored (0, 1, 2, 4, 6) and wicket probability (0, 1)
    # ----------------------------------------------------
    print("\n--- Training Outcome Models ---")
    outcome_features = [
        'batsman', 'bowler', 'bowling_speed_kph', 'bowling_path_type', 
        'pitch_line', 'pitch_length', 'weather', 'ball_type', 'ball_age',
        'batsman_reaction', 'venue'
    ]
    outcome_categorical = [
        'batsman', 'bowler', 'bowling_path_type', 
        'pitch_line', 'pitch_length', 'weather', 'ball_type', 'batsman_reaction', 'venue'
    ]
    outcome_numerical = ['bowling_speed_kph', 'ball_age']
    
    X_out = df[outcome_features]
    y_runs = df['runs_scored']
    y_wick = df['is_wicket']
    
    X_out_train, X_out_test, y_runs_train, y_runs_test, y_wick_train, y_wick_test = train_test_split(
        X_out, y_runs, y_wick, test_size=0.2, random_state=42
    )
    
    preprocessor_out = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), outcome_categorical),
            ('num', StandardScaler(), outcome_numerical)
        ]
    )
    
    pipeline_runs = Pipeline([
        ('preprocessor', preprocessor_out),
        ('classifier', RandomForestClassifier(n_estimators=50, max_depth=12, random_state=42, n_jobs=-1))
    ])
    
    print("Fitting Runs Model...")
    pipeline_runs.fit(X_out_train, y_runs_train)
    y_runs_pred = pipeline_runs.predict(X_out_test)
    print(f"Runs Model Accuracy: {accuracy_score(y_runs_test, y_runs_pred):.4f}")
    
    pipeline_wick = Pipeline([
        ('preprocessor', preprocessor_out),
        ('classifier', RandomForestClassifier(n_estimators=50, max_depth=12, random_state=42, n_jobs=-1))
    ])
    
    print("Fitting Wicket Model...")
    pipeline_wick.fit(X_out_train, y_wick_train)
    y_wick_pred = pipeline_wick.predict(X_out_test)
    print(f"Wicket Model Accuracy: {accuracy_score(y_wick_test, y_wick_pred):.4f}")
    
    # ----------------------------------------------------
    # Model 4: Win Probability Model
    # Predicts win probability (0.0 to 1.0)
    # ----------------------------------------------------
    print("\n--- Training Win Probability Model ---")
    win_features = [
        'inning', 'overs', 'wickets', 'runs_needed', 'balls_remaining', 
        'current_run_rate', 'required_run_rate', 'venue', 'weather',
        'batsman_form', 'bowler_form'
    ]
    win_categorical = ['venue', 'weather']
    win_numerical = [
        'inning', 'overs', 'wickets', 'runs_needed', 'balls_remaining', 
        'current_run_rate', 'required_run_rate', 'batsman_form', 'bowler_form'
    ]
    
    X_win = df[win_features]
    y_win = df['win_probability_after']
    
    X_win_train, X_win_test, y_win_train, y_win_test = train_test_split(
        X_win, y_win, test_size=0.2, random_state=42
    )
    
    preprocessor_win = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore'), win_categorical),
            ('num', StandardScaler(), win_numerical)
        ]
    )
    
    pipeline_win = Pipeline([
        ('preprocessor', preprocessor_win),
        ('regressor', RandomForestRegressor(n_estimators=50, max_depth=10, random_state=42, n_jobs=-1))
    ])
    
    print("Fitting Win Probability Model...")
    pipeline_win.fit(X_win_train, y_win_train)
    y_win_pred = pipeline_win.predict(X_win_test)
    print(f"Win Probability Model MSE: {mean_squared_error(y_win_test, y_win_pred):.6f}")
    
    # Save the models
    os.makedirs('models', exist_ok=True)
    joblib.dump(pipeline_react, 'models/batsman_reaction_model.pkl')
    joblib.dump(pipeline_runs, 'models/runs_model.pkl')
    joblib.dump(pipeline_wick, 'models/wicket_model.pkl')
    joblib.dump(pipeline_win, 'models/win_prob_model.pkl')
    
    # Save a JSON file with unique values for dropdowns
    import json
    metadata = {
        'batsmen': df['batsman'].unique().tolist(),
        'bowlers': df['bowler'].unique().tolist(),
        'venues': df['venue'].unique().tolist(),
        'weather_conditions': df['weather'].unique().tolist(),
        'ball_types': df['ball_type'].unique().tolist(),
        'lines': df['pitch_line'].unique().tolist(),
        'lengths': df['pitch_length'].unique().tolist(),
        'variations': df['bowling_path_type'].unique().tolist(),
        'reactions': df['batsman_reaction'].unique().tolist()
    }
    with open('models/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
        
    print("\nAll models and metadata saved successfully in the 'models/' directory!")

if __name__ == '__main__':
    train_and_save_models()
