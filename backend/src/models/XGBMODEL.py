import numpy as np
import xgboost as xgb
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from typing import Union # Pour les annotations de type

class XGBoostModel:
    """
    Une interface pour le modèle de Classification XGBoost qui gère la standardisation.
    
    Note: Ce modèle est généralement utilisé APRÈS l'étape d'imputation dans un Pipeline.
    """
    
    def __init__(self, n_estimators=100, max_depth=6, learning_rate=0.1, 
                 random_state=None, n_jobs=-1, **kwargs):
        """
        Initialise le modèle XGBClassifier.
        
        Args:
            n_estimators (int): Le nombre d'arbres (boosting rounds).
            max_depth (int): Profondeur maximale de l'arbre.
            learning_rate (float): Taux d'apprentissage.
            random_state (int): Graine pour la reproductibilité.
            n_jobs (int): Nombre de cœurs de CPU à utiliser pour le parallélisme.
            **kwargs: Arguments supplémentaires passés à XGBClassifier.
        """
        self.model = XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            random_state=random_state,
            n_jobs=n_jobs,
            use_label_encoder=False, 
            eval_metric='mlogloss', # Métrique standard pour la multi-classification
            **kwargs
        )
        
        # Le scaler est inclus pour respecter l'interface originale, 
        # mais la standardisation est optionnelle pour les modèles basés sur les arbres.
        self.scaler = StandardScaler()

    def train(self, X_train: Union[np.ndarray, pd.DataFrame], y_train: Union[np.ndarray, pd.Series]):
        """
        Standardise et entraîne le modèle.
        """
        # Standardise les données (fit_transform)
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Entraîne le modèle XGBoost
        self.model.fit(X_train_scaled, y_train)

    def predict(self, X_test: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Standardise les nouvelles données et prédit leurs classes.
        """
        # Standardise les données de test (transform)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Fait la prédiction
        return self.model.predict(X_test_scaled)

    def predict_proba(self, X_test: Union[np.ndarray, pd.DataFrame]) -> np.ndarray:
        """
        Standardise les nouvelles données et prédit leurs probabilités de classe.
        """
        X_test_scaled = self.scaler.transform(X_test)
        return self.model.predict_proba(X_test_scaled)

    def get_params(self, deep=True):
        """Retourne les paramètres du modèle Scikit-learn, nécessaire pour GridSearchCV."""
        return self.model.get_params(deep=deep)

    def set_params(self, **params):
        """Définit les paramètres du modèle Scikit-learn, nécessaire pour GridSearchCV."""
        return self.model.set_params(**params)