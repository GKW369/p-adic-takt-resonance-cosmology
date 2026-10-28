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
    # Definiere das Basisverzeichnis (wo dieses Skript liegt)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_filename = "ptrc_complete_context_bundle.txt"
    output_file = os.path.join(base_dir, output_filename)
    
    # Erlaubte Datei-Endungen für den KI-Kontext
    valid_extensions = (".py", ".md", ".txt")
    
    # Hauptordner, die wir samt all ihrer Unterordner scannen wollen
    target_root_folders = ["src", "paper", "experimental"]
    
    print("[ START ] Erzeuge das globale pTRC-Kontext-Bundle mit Inhaltsverzeichnis...")
    
    # Listen, um die gefundenen Pfade für das Inhaltsverzeichnis zu sammeln
    files_to_bundle = []
    
    # Schritt 1: Vorscan für das Inhaltsverzeichnis
    readme_path = os.path.join(base_dir, "README.md")
    if os.path.exists(readme_path):
        files_to_bundle.append("README.md")
        
    for root_folder in target_root_folders:
        root_folder_path = os.path.join(base_dir, root_folder)
        if not os.path.exists(root_folder_path):
            continue
            
        for dirpath, _, filenames in os.walk(root_folder_path):
            for filename in sorted(filenames):
                if filename.endswith(valid_extensions):
                    if filename == output_filename:
                        continue
                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, base_dir)
                    files_to_bundle.append(relative_path)

    # Schritt 2: Schreiben des Bundles (Inhaltsverzeichnis zuerst, dann die Inhalte)
    with open(output_file, "w", encoding="utf-8") as outfile:
        # Header und Inhaltsverzeichnis in die Datei schreiben
        outfile.write("======================================================================\n")
        outfile.write("pTRC REPOSITORY COMPLETE CONTEXT BUNDLE\n")
        outfile.write("======================================================================\n\n")
        outfile.write("--- TABLE OF CONTENTS ---\n")
        for idx, rel_path in enumerate(files_to_bundle, 1):
            outfile.write(f"{idx:02d}. {rel_path}\n")
        outfile.write("----------------------------------------------------------------------\n\n\n")
        
        # Jetzt die Dateien nacheinander einlesen und anhängen
        for rel_path in files_to_bundle:
            full_path = os.path.join(base_dir, rel_path)
            
            outfile.write("======================================================================\n")
            outfile.write(f"--- START OF REPOSITORY FILE: {rel_path} ---\n")
            outfile.write("======================================================================\n\n")
            
            with open(full_path, "r", encoding="utf-8") as infile:
                outfile.write(infile.read())
                
            outfile.write("\n\n")
            print(f"        Gebündelt und indexiert: {rel_path}")
                        
    print(f"\n[ OK ] Das komplette Repository wurde vereint (inkl. Index): {output_file}")

if __name__ == "__main__":
    bundle_repository()
