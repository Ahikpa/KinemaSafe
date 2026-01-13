import unittest
import os
import csv
from src.analyzer import SafetyMonitor

class TestSafetyMonitor(unittest.TestCase):
    
    def setUp(self):
        """Préparation de l'environnement de test : création d'un CSV temporaire"""
        self.test_file = "test_data.csv"
        with open(self.test_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['timestamp', 'vehicle_speed_kph', 'obstacle_distance_m', 'brake_pedal_status'])
            # Cas 1: Vitesse élevée, distance courte -> DANGER (TTC = 20m / (72kmh/3.6) = 20/20 = 1s)
            writer.writerow([1.0, 72.0, 20.0, 0])
            # Cas 2: Vitesse faible, distance longue -> SAFE (TTC = 100m / (10kmh/3.6) = ~36s)
            writer.writerow([2.0, 10.0, 100.0, 0])
            # Cas 3: À l'arrêt -> SAFE (TTC Infini)
            writer.writerow([3.0, 0.0, 10.0, 0])

    def tearDown(self):
        """Nettoyage après le test"""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_detection_logique(self):
        """Vérifie que le moniteur détecte bien UNIQUEMENT le cas dangereux"""
        monitor = SafetyMonitor(critical_ttc_threshold=2.0)
        events = monitor.analyze_stream(self.test_file)
        
        # On ne doit avoir qu'un seul événement critique (le Cas 1)
        self.assertEqual(len(events), 1)
        
        # Vérification des valeurs calculées
        danger_event = events[0]
        self.assertAlmostEqual(danger_event['ttc_value'], 1.0, places=2)
        self.assertEqual(danger_event['severity'], "HIGH")

    def test_cas_limite_arret(self):
        """Vérifie que le véhicule à l'arrêt ne crashe pas le code (division par zero)"""
        monitor = SafetyMonitor(critical_ttc_threshold=2.0)
        # On réutilise le fichier, le Cas 3 ne doit pas planter ni être détecté comme critique
        events = monitor.analyze_stream(self.test_file)
        
        # Le timestamp 3.0 (arrêt) ne doit PAS être dans les événements critiques
        timestamps = [e['timestamp'] for e in events]
        self.assertNotIn(3.0, timestamps)

if __name__ == '__main__':
    unittest.main()
