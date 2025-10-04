import json
import numpy as np
import time
import matplotlib.pyplot as plt
from sklearn.model_selection import learning_curve
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    log_loss, confusion_matrix, classification_report
)
from sklearn.preprocessing import label_binarize


class ModelEvaluator:
    def __init__(self, model, X_train, y_train, X_test, y_test, class_labels=None):
        """
        :param model: Modèle sklearn (déjà fit ou non)
        :param X_train: Données d'entraînement
        :param y_train: Labels d'entraînement
        :param X_test: Données de test
        :param y_test: Labels de test
        :param class_labels: Liste des noms de classes (optionnel)
        """
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.class_labels = class_labels if class_labels else np.unique(y_train)
        self.report = {}

    def evaluate(self, cv=5, scoring='accuracy', show_curve=False):
        """Évalue le modèle, calcule toutes les métriques et la courbe d'apprentissage."""

        # ==== Entraînement + mesure du temps ====
        start_fit = time.time()
        self.model.fit(self.X_train, self.y_train)
        fit_time = round(time.time() - start_fit, 3)

        # ==== Prédictions ====
        start_pred = time.time()
        y_pred_train = self.model.predict(self.X_train)
        y_pred_test = self.model.predict(self.X_test)
        pred_time = round(time.time() - start_pred, 3)

        # ==== Probabilités (si dispo) ====
        y_prob_test = None
        if hasattr(self.model, "predict_proba"):
            try:
                y_prob_test = self.model.predict_proba(self.X_test)
            except Exception:
                pass

        # ==== Métriques globales ====
        def compute_metrics(y_true, y_pred, y_prob=None):
            result = {
                "accuracy": round(accuracy_score(y_true, y_pred), 4),
                "precision": round(precision_score(y_true, y_pred, average='weighted', zero_division=0), 4),
                "recall": round(recall_score(y_true, y_pred, average='weighted', zero_division=0), 4),
                "f1_score": round(f1_score(y_true, y_pred, average='weighted', zero_division=0), 4),
            }
            if y_prob is not None:
                # log_loss & ROC AUC
                try:
                    y_true_bin = label_binarize(y_true, classes=np.unique(y_true))
                    result["roc_auc"] = round(roc_auc_score(y_true_bin, y_prob, multi_class='ovr'), 4)
                except Exception:
                    result["roc_auc"] = None
                try:
                    result["log_loss"] = round(log_loss(y_true, y_prob), 4)
                except Exception:
                    result["log_loss"] = None
            return result

        train_metrics = compute_metrics(self.y_train, y_pred_train)
        test_metrics  = compute_metrics(self.y_test, y_pred_test, y_prob_test)

        # ==== Rapport complet ====
        self.report = {
            "model_info": {
                "model_name": type(self.model).__name__,
                "parameters": self.model.get_params(),
                "fit_time_sec": fit_time,
                "predict_time_sec": pred_time
            },
            "train": train_metrics,
            "test": test_metrics,
            "confusion_matrix": confusion_matrix(self.y_test, y_pred_test).tolist(),
            "classification_report": classification_report(
                self.y_test, y_pred_test, target_names=self.class_labels, output_dict=True
            )
        }

        # ==== Courbe d'apprentissage ====
        train_sizes, train_scores, test_scores = learning_curve(
            self.model, self.X_train, self.y_train,
            cv=cv, scoring=scoring, train_sizes=np.linspace(0.1, 1.0, 10), n_jobs=-1
        )
        train_mean, test_mean = np.mean(train_scores, axis=1), np.mean(test_scores, axis=1)

        self.report["learning_curve"] = {
            "train_sizes": train_sizes.tolist(),
            "train_scores": train_mean.round(4).tolist(),
            "test_scores": test_mean.round(4).tolist()
        }
        return self.report

    def to_json(self, indent=4):
        """Renvoie le rapport complet en JSON"""
        return json.dumps(self.report, indent=indent)
