import csv
import random
import os

class TelemetryGenerator:
    """
    Simule un flux de données provenant d'un simulateur (ex: SCANeR/Carla).
    Génère un scénario de freinage d'urgence.
    """
    def __init__(self, output_path):
        self.output_path = output_path
        self.duration_seconds = 20
        self.frequency_hz = 10  # 10 mesures par seconde

    def generate_scenario(self):
        print(f"[SIMULATION] Génération des données brutes vers {self.output_path}...")
        
        with open(self.output_path, 'w', newline='') as csvfile:
            fieldnames = ['timestamp', 'vehicle_speed_kph', 'obstacle_distance_m', 'brake_pedal_status']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # État initial
            distance = 150.0
            speed = 50.0 # km/h
            
            for i in range(self.duration_seconds * self.frequency_hz):
                timestamp = i / self.frequency_hz
                
                # Scénario : On roule, obstacle apparaît, on freine fort
                if 5.0 < timestamp < 12.0:
                    # L'obstacle se rapproche dangereusement (vitesse relative simulée)
                    distance -= (speed / 3.6) * 0.1  # d = v * t
                    brake = 0.0
                elif timestamp >= 12.0:
                    # Freinage d'urgence !
                    brake = 1.0
                    speed = max(0, speed - 2.5) # Décélération
                    if speed > 0:
                        distance -= (speed / 3.6) * 0.1
                else:
                    # Approche normale
                    distance -= (speed / 3.6) * 0.1
                    brake = 0.0

                # Ajout d'un peu de "bruit" de capteur (réalisme)
                noisy_dist = max(0, distance + random.uniform(-0.1, 0.1))
                
                writer.writerow({
                    'timestamp': round(timestamp, 2),
                    'vehicle_speed_kph': round(speed, 2),
                    'obstacle_distance_m': round(noisy_dist, 2),
                    'brake_pedal_status': brake
                })
        
        print("[SIMULATION] Terminée.")
