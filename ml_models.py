import numpy as np
import pandas as pd
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

def generate_technical_features(df):
    """Abstracts mathematical pattern features out of price matrices arrays."""
    df_feat = df.copy()
    if len(df_feat) < 50:
        return None
    
    # Mathematical Indicator Feature Matrices Extraction
    df_feat['RSI'] = RSIIndicator(close=df_feat['Close'], window=14).rsi_indicator()
    df_feat['EMA20'] = EMAIndicator(close=df_feat['Close'], window=20).ema_indicator()
    df_feat['EMA50'] = EMAIndicator(close=df_feat['Close'], window=50).ema_indicator()
    df_feat['Vol_SMA'] = df_feat['Volume'].rolling(window=20).mean()
    
    # Price distance structural delta features
    df_feat['Price_EMA20_Dist'] = df_feat['Close'] - df_feat['EMA20']
    df_feat['Price_EMA50_Dist'] = df_feat['Close'] - df_feat['EMA50']
    df_feat['Vol_Ratio'] = df_feat['Volume'] / (df_feat['Vol_SMA'] + 1e-8)
    
    # Map a binary classification column target: 1 if next bar closes up, else 0
    df_feat['Target'] = np.where(df_feat['Close'].shift(-1) > df_feat['Close'], 1, 0)
    
    return df_feat.dropna()

def train_ensemble_confidence_classifiers(historical_bars_df):
    """Trains a combination of gradient boosters to rank breakout setups."""
    df_features = generate_technical_features(historical_bars_df)
    if df_features is None or len(df_features) < 30:
        return None, 0.5
    
    feature_columns = ['RSI', 'Price_EMA20_Dist', 'Price_EMA50_Dist', 'Vol_Ratio']
    X = df_features[feature_columns].values
    y = df_features['Target'].values
    
    # Initialize fast institutional configurations
    xgb = XGBClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, eval_metric='logloss')
    lgb = LGBMClassifier(n_estimators=50, max_depth=3, learning_rate=0.1, verbose=-1)
    
    xgb.fit(X, y)
    lgb.fit(X, y)
    
    latest_features = df_features[feature_columns].iloc[-1].values.reshape(1, -1)
    
    # Calculate probability metrics across model structures
    xgb_prob = xgb.predict_proba(latest_features)[0][1]
    lgb_prob = lgb.predict_proba(latest_features)[0][1]
    
    voted_confidence_score = (xgb_prob + lgb_prob) / 2.0
    return voted_confidence_score
