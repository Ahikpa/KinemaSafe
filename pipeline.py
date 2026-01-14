import os
from src.generator import TelemetryGenerator
from src.analyzer import SafetyMonitor
from src.adapter import SynergiesAdapter

def main():
    print("=== KinemaSafe Pipeline Started ===")
    
    # Chemins des fichiers
    raw_data_file = os.path.join("data", "raw_simulation_log.csv")
    final_output_file = os.path.join("data", "kinemasafe_output.json")

    # Étape 1 : Simulation (Mocking Data Generation)
    # Dans la réalité, cela viendrait de SCANeR ou Carla
    sim = TelemetryGenerator(raw_data_file)
    sim.generate_scenario()

    # Étape 2 : Analyse et Calcul d'indicateurs (Core Logic)
    # Calcul du Time-To-Collision
    monitor = SafetyMonitor(critical_ttc_threshold=2.5)
    critical_events = monitor.analyze_stream(raw_data_file)

    # Étape 3 : Standardisation (Data Extraction)
    # Export vers le format commun du projet européen
    adapter = SynergiesAdapter(final_output_file)
    adapter.export(critical_events, raw_data_file)

    print("\n=== Pipeline terminé avec succès ===")
    print(f"Vérifiez le fichier de sortie : {final_output_file}")

if __name__ == "__main__":
    main()

