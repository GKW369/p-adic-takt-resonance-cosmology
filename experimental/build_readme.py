import os

base_dir = os.path.dirname(os.path.abspath(__file__))
readme_path = os.path.join(base_dir, "README.md")

# Wir nehmen deine aktuelle GitHub-README als Basis-Text
with open(readme_path, "r", encoding="utf-8") as f:
    current_content = f.read()

# Deine neuen industriellen Erweiterungen als sauberer String
extra_matrix_entries = """

| **Digital Audio Signal Processing** | Accumulation of high-frequency quantization noise during iterative cascading digital filter cycles. | Invariant topological filtering using exact, nanosecond-matched integer clock cycles via nested modular rings. | **100% artifact-free, phase-synchronized studio acoustics** without degradation of digital filter states. |
| **Neuro-Tech & Biosignal Tracking** | Thermal accumulation from continuous float interpolation creates heat dissipation hazards for low-power processing units. | Fixed-point, 1-bit discrete Takt-processing in Z using Modulo-24 clock intervals, bypassing complex transcendental function overhead. | **Drastically reduces thermal power profiles** during local signal conditioning, allowing ultra-low-power, cold chip operations. |
| **Logistik & Supply Chain** | Dynamische Routenberechnung mit Rundungsfehlern im kontinuierlichen Raum führt zu fehlerhaften Kapazitätsgrenzen. | Ganzzahlige Graphenoptimierung und Streckennetz-Filterung über die Restklassen des Modulo-210-Uhrsystems. | **Fehlerfreie Echtzeit-Disposition** und absolute Routen-Invarianz ohne kumulativen Rechenzeit-Overhead. |
| **Robotik & Sensorik** | Kalman-Filter-Drift und Akkumulationsfehler bei der kontinuierlichen Fließkomma-Sensorfusion im Raum. | Diskrete Zustandsaktualisierung und sensorische Takt-Synchronisation direkt im unteilbaren Ganzzahl-Raster ($\mathbb{Z}$). | **Deterministische Kollisionsvermeidung** und absolut driftfreie Positionsbestimmung bei maximaler Ausführungsschärfe. |
"""

# Wir suchen die Stelle in deiner Tabelle, um die neuen Zeilen formschlüssig einzufügen
if "Anisotropic Crystalline Waveguide Trajectories" in current_content:
    # Wir fügen die neuen Zeilen direkt in die bestehende Industriematrix ein
    parts = current_content.split("| **Ballistics & Trajectory Control**")
    updated_content = parts[0] + extra_matrix_entries + "\n| **Ballistics & Trajectory Control**" + parts[1]
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print("[ SUCCESS ] Deine README.md wurde lokal gerettet und um alle Industriebereiche erweitert!")
else:
    print("[ INFO ] Manuelle Anpassung: Kopiere die vier Zeilen aus 'extra_matrix_entries' direkt in deine Tabellenstruktur.")
