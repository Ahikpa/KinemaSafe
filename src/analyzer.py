from typing import List, Dict, Any
import csv

class SafetyMonitor:
    """
    Responsable de l'analyse des données cinématiques pour identifier les situations critiques.
    
    Attributes:
        threshold (float): Le seuil de TTC (Time To Collision) en secondes en dessous duquel
                           une situation est considérée comme critique.
    """
    
    def __init__(self, critical_ttc_threshold: float = 3.0):
        """
        Initialise le moniteur de sécurité.

        Args:
            critical_ttc_threshold (float): Seuil d'alerte TTC en secondes. Défaut à 3.0s.
        """
        self.threshold = critical_ttc_threshold

    def analyze_stream(self, input_csv: str) -> List[Dict[str, Any]]:
        """
        Lit un flux de données CSV et identifie les frames où la sécurité est compromise.

        Args:
            input_csv (str): Chemin vers le fichier CSV source.

        Returns:
            List[Dict[str, Any]]: Une liste de dictionnaires contenant les métadonnées des événements critiques.
        """
        print(f"[ANALYSE] Recherche de situations critiques (TTC < {self.threshold}s)...")
        
        critical_events: List[Dict[str, Any]] = []
        
        try:
            with open(input_csv, 'r') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    # Conversion avec gestion d'erreur implicite via le typage attendu
                    speed_kmh = float(row['vehicle_speed_kph'])
                    dist_m = float(row['obstacle_distance_m'])
                    time = float(row['timestamp'])
                    
                    # Conversion km/h -> m/s
                    speed_ms = speed_kmh / 3.6
                    
                    # Calcul TTC (Time To Collision) = Distance / Vitesse Relative
                    # Gestion du cas limite : Division par zéro si véhicule à l'arrêt
                    if speed_ms > 0.1:
                        ttc = dist_m / speed_ms
                    else:
                        ttc = 999.0 # Considéré comme infini (sécurisé)

                    # Si le TTC passe sous le seuil, on enregistre l'événement
                    if ttc < self.threshold:
                        critical_events.append({
                            "timestamp": time,
                            "ttc_value": round(ttc, 2),
                            "speed": speed_kmh,
                            "distance": dist_m,
                            "severity": "HIGH" if ttc < 1.5 else "MEDIUM"
                        })
                        
            print(f"[ANALYSE] {len(critical_events)} frames critiques détectées.")
            return critical_events
            
        except FileNotFoundError:
            print(f"[ERREUR] Le fichier {input_csv} est introuvable.")
            return []
        except Exception as e:
            print(f"[ERREUR] Une erreur inattendue est survenue : {e}")
            return []
