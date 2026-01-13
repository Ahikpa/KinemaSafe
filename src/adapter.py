import json
from datetime import datetime

class SynergiesAdapter:
    """
    Module d'exportation vers le format standardisé (fictif) du projet SYNERGIES.
    Transforme les données Python en JSON structuré.
    """
    def __init__(self, output_path):
        self.output_path = output_path

    def export(self, critical_data, source_file):
        print(f"[EXPORT] Conversion vers le format SYNERGIES-SSD -> {self.output_path}")
        
        # Structure JSON qui imite un standard industriel
        payload = {
            "metadata": {
                "project": "SYNERGIES",
                "export_date": datetime.now().isoformat(),
                "source_simulation": source_file,
                "partner": "SystemX_Candidate_POC"
            },
            "scenarios_identified": [
                {
                    "type": "NEAR_COLLISION",
                    "description": "Vehicle approached obstacle with low TTC",
                    "events_count": len(critical_data),
                    "time_series_data": critical_data
                }
            ]
        }

        with open(self.output_path, 'w') as f:
            json.dump(payload, f, indent=4)
            
        print("[EXPORT] Succès.")
