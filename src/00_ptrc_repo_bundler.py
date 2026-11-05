# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program (see the LICENSE file in the root directory).
# If not, see <https://gnu.org>.
# ==============================================================================

# -*- coding: utf-8 -*-

import os

def bundle_repository():
    # Ermittle das Verzeichnis, in dem dieses Skript liegt
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # DYNAMISCHE ROOT-ERKENNUNG:
    # Wenn das Skript im Unterordner "src" liegt, ist das Hauptverzeichnis eine Ebene höher.
    if os.path.basename(current_script_dir) == "src":
        root_dir = os.path.dirname(current_script_dir)
    else:
        root_dir = current_script_dir
        
    output_filename = "ptrc_complete_context_bundle.txt"
    output_file = os.path.join(root_dir, output_filename)
    
    # Erlaubte Datei-Endungen für den KI-Kontext
    valid_extensions = (".py", ".md", ".txt", ".c", ".h")
    
    # Hauptordner im Root-Verzeichnis scannen (Experimental bleibt für spekulatve Texte gesperrt)
    target_root_folders = ["src", "paper", "embedded"]
    
    print(f"[ START ] Erzeuge das geschützte pTRC-Kontext-Bundle im Hauptverzeichnis: {root_dir}")
    
    # Listen, um die gefundenen Pfade für das Inhaltsverzeichnis zu sammeln
    files_to_bundle = []
    
    # Schritt 1: README direkt im Root erfassen
    readme_path = os.path.join(root_dir, "README.md")
    if os.path.exists(readme_path):
        files_to_bundle.append("README.md")
        
    # Schritt 2: Standard-Ordner durchlaufen (src, paper, embedded)
    # Bindet das neue Core-Testskript "src/00_ptrc_fpu_drift_test.py" nahtlos ein
    for root_folder in target_root_folders:
        root_folder_path = os.path.join(root_dir, root_folder)
        if not os.path.exists(root_folder_path):
            continue
            
        for dirpath, _, filenames in os.walk(root_folder_path):
            for filename in sorted(filenames):
                if filename.endswith(valid_extensions):
                    if filename == output_filename:
                        continue
                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, root_dir)
                    files_to_bundle.append(relative_path)

    # Schritt 3: ISOLIERTER SCAN der Grafik-Engine aus dem experimental-Ordner
    # Extrahiert ausschließlich die harten mathematischen Visualisierungsskripte
    experimental_graphics_path = os.path.join(root_dir, "experimental", "ptrc_3d_engine")
    if os.path.exists(experimental_graphics_path):
        print("        -> Schalte Isolations-Sieve für Grafik-Sektion aktiv...")
        for dirpath, _, filenames in os.walk(experimental_graphics_path):
            for filename in sorted(filenames):
                if filename.endswith(valid_extensions):
                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, root_dir)
                    files_to_bundle.append(relative_path)

    # Schritt 4: Schreiben des Bundles (Inhaltsverzeichnis zuerst, dann die Inhalte)
    with open(output_file, "w", encoding="utf-8") as outfile:
        # Header und Inhaltsverzeichnis in die Datei schreiben
        outfile.write("======================================================================\n")
        outfile.write("pTRC REPOSITORY COMPLETE CONTEXT BUNDLE (Isolated Graphics Release)\n")
        outfile.write("======================================================================\n\n")
        outfile.write("--- TABLE OF CONTENTS ---\n")
        for idx, rel_path in enumerate(files_to_bundle, 1):
            outfile.write(f"{idx:02d}. {rel_path}\n")
        outfile.write("----------------------------------------------------------------------\n\n\n")
        
        # Jetzt die Dateien nacheinander einlesen und anhängen
        for rel_path in files_to_bundle:
            full_path = os.path.join(root_dir, rel_path)
            
            outfile.write("======================================================================\n")
            outfile.write(f"--- START OF REPOSITORY FILE: {rel_path} ---\n")
            outfile.write("======================================================================\n\n")
            
            with open(full_path, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
                
            outfile.write("\n\n")
            print(f"        Gebündelt und indexiert: {rel_path}")
                        
    print(f"\n[ OK ] Das bereinigte Repository-Bundle wurde vereint: {output_file}")

if __name__ == "__main__":
    bundle_repository()
