import numpy as np
# Changement CLÉ : Importer RandomForestClassifier au lieu de LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
# OneVsRestClassifier n'est plus nécessaire car RandomForest le gère nativement
# from sklearn.multiclass import OneVsRestClassifier 


class RandomForestModel:
    """
    Une interface pour le modèle de Forêt Aléatoire (Random Forest)
    qui gère automatiquement la standardisation des données.
    """
    
    def __init__(self, n_estimators=100, criterion='gini', max_depth=None, 
                 min_samples_leaf=1, random_state=None, n_jobs=-1):
        """
        Initialise le modèle Forêt Aléatoire en utilisant les hyperparamètres de Scikit-learn.
        
        Args:
            n_estimators (int): Le nombre d'arbres dans la forêt.
            criterion (str): La fonction pour mesurer la qualité d'une division ('gini' ou 'entropy').
            max_depth (int): Profondeur maximale de l'arbre.
            min_samples_leaf (int): Nombre minimum d'échantillons requis à un nœud feuille.
            random_state (int): Graine pour la reproductibilité.
            n_jobs (int): Nombre de cœurs de CPU à utiliser pour le parallélisme. (-1 = tous les cœurs).
        """
        # Créer le modèle RandomForestClassifier (gère nativement le multi-classe)
        self.model = RandomForestClassifier(
            n_estimators=n_estimators,
            criterion=criterion,
            max_depth=max_depth,
            min_samples_leaf=min_samples_leaf,
            random_state=random_state,
            n_jobs=n_jobs  # Utilisation du parallélisme pour la vitesse
        )
        
        # Initialise un scaler pour la standardisation des données
        # (La standardisation est optionnelle pour RF, mais on la garde pour la cohérence de l'interface)
        self.scaler = StandardScaler()

    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """
        Standardise et entraîne le modèle sur les données d'entraînement.
        
        Args:
            X_train (np.ndarray): Les données d'entraînement (features).
            y_train (np.ndarray): Les étiquettes cibles (labels).
        """
        # Standardise les données et garde le scaler en mémoire
        # Bien que la Forêt Aléatoire ne soit pas affectée par la mise à l'échelle,
        # cette étape est conservée pour l'uniformité de l'interface.
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Entraîne le modèle Random Forest
        self.model.fit(X_train_scaled, y_train)

    def predict(self, X_test: np.ndarray) -> np.ndarray:
        """
        Standardise les nouvelles données et prédit leurs classes.
        
        Args:
            X_test (np.ndarray): Les données pour lesquelles faire une prédiction.
            
        Returns:
            np.ndarray: Le tableau des classes prédites.
        """
        # Standardise les données de test avec le MÊME scaler que pour l'entraînement
        X_test_scaled = self.scaler.transform(X_test)
        
        # Fait la prédiction
        return self.model.predict(X_test_scaled)

    def predict_proba(self, X_test: np.ndarray) -> np.ndarray:
        """
        Standardise les nouvelles données et prédit leurs probabilités de classe.
        
        Args:
            X_test (np.ndarray): Les données pour lesquelles faire une prédiction.
            
        Returns:
            np.ndarray: Le tableau des probabilités de classe.
        """
        X_test_scaled = self.scaler.transform(X_test)
        return self.model.predict_proba(X_test_scaled)

    def get_params(self, deep=True):
        """Retourne les paramètres du modèle Scikit-learn."""
        return self.model.get_params(deep=deep)
