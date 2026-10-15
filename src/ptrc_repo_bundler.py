# ==============================================================================
# pTRC Framework - Repository Context Bundler for AI Analysis
# Copyright (c) 2026 Kurt Guido Wirminghaus <g.wirminghaus@gmx.de>
# GPLv3 Open Source / Commercial License Required
# ==============================================================================
# -*- coding: utf-8 -*-

import os

def bundle_repository():
    # Definiere das Zielverzeichnis (dein lokaler pTRC-Ordner)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(base_dir, "ptrc_complete_context_bundle.txt")
    
    # Erlaubte Datei-Endungen für das KI-Futter
    valid_extensions = (".py", ".md", ".txt")
    # Ordner, die wir scannen wollen
    target_folders = ["src", "paper", "experimental"]
    
    print("[ START ] Erzeuge das globale pTRC-Kontext-Bundle...")
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        # 1. Zuerst die Haupt-README aus dem Root-Verzeichnis einbinden
        readme_path = os.path.join(base_dir, "README.md")
        if os.path.exists(readme_path):
            outfile.write("======================================================================\n")
            outfile.write("--- START OF ROOT FILE: README.md ---\n")
            outfile.write("======================================================================\n\n")
            with open(readme_path, "r", encoding="utf-8") as f:
                outfile.write(f.read())
            outfile.write("\n\n")
            print("        Root-Ebene: README.md erfolgreich gebündelt.")

        # 2. Danach alle Unterordner (src, paper, experimental) systematisch auslesen
        for folder in target_folders:
            folder_path = os.path.join(base_dir, folder)
            if not os.path.exists(folder_path):
                continue
                
            # Sortierte Dateiliste für eine unbestechliche, reproduzierbare Reihenfolge
            for filename in sorted(os.listdir(folder_path)):
                if filename.endswith(valid_extensions):
                    file_path = os.path.join(folder_path, filename)
                    relative_path = os.path.join(folder, filename)
                    
                    outfile.write("======================================================================\n")
                    outfile.write(f"--- START OF REPOSITORY FILE: {relative_path} ---\n")
                    outfile.write("======================================================================\n\n")
                    
                    with open(file_path, "r", encoding="utf-8") as infile:
                        outfile.write(infile.read())
                        
                    outfile.write("\n\n")
                    print(f"        Verzeichnis [{folder}]: {filename} erfolgreich gebündelt.")
                    
    print(f"\n[ OK ] Das komplette Repository wurde in eine Datei gegossen: {output_file}")

if __name__ == "__main__":
    bundle_repository()
