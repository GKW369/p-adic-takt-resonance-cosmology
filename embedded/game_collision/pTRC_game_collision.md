# pTRC Game-Collision Engine (`ptrc_game_collision`) — v4.6.0

**Deterministic 1-Bit Integer Physics, Zero-Tunneling Guarantee & Lockstep Multiplayer Verification**  
Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.  
License: GNU Affero General Public License v3.0 (AGPL-3.0).

---

## 1. Warum pTRC für Spiele-Engines & Echtzeit-Physik?

Klassische Spiele-Physik-Engines basieren auf Gleitkommazahlen (`float`/`double`), kontinuierlichen Zeit-Deltas (`dt`) und kubischen Octrees. Das führt in der Praxis zu drei bekannten Problemen:
1. **Tunneling:** Schnelle Projektile oder Partikel durchdringen dünne Wände zwischen zwei Frames.
2. **Multiplayer-Desync:** Unterschiedliche CPU-Architekturen oder Compiler-Optimierungen erzeugen leichte Gleitkomma-Abweichungen über viele Ticks.
3. **Kubische Gitter-Artefakte:** Achsenparallele Kollisionsgitter verursachen diagonale Ungenauigkeiten.

**`ptrc_game_collision` löst diese Probleme architektonisch auf Basis von `ptrc_light_universe` v4.6.0:**
* **0-Tunneling-Invariante (`tunneling_escapes == 0`):** Alle `60.000` dynamischen Körper (`780.000` Raumkristalle) bewegen sich auf einem diskreten, nullfreien `1+12`-Kuboktaeder-Raumgitter (\(\mathbb{Z}^3 \setminus \{0\}\)). Kein Objekt kann einen Gitterpunkt überspringen oder eine Kollisionshülle durchdringen.
* **100 % Bit-identischer Lockstep (`lockstep_state_hash`):** Nach jedem Physik-Tick wird ein deterministischer 64-Bit-Primorial-FNV-Hash über sämtliche `60.000` Positionen und `1-Byte`-Zustände berechnet. Zwei unabhängige Simulationen liefern auf das letzte Bit identische Hashes.
* **Echtzeit-Trefferklassifikation:** Trennt in jedem Tick exakt zwischen **Rigid-Body-Treffern** (rotierende 3D-Kristallpyramide & zentrierte 3D-Kristallkugel) und **Partikel-zu-Partikel-Kollisionen** (über `65.536` FCC-Slots und `144`-Facetten-Anisotropie).

---

## 2. API-Übersicht (`ptrc_game_collision.h`)

| Funktion | Aufgabe |
| :--- | :--- |
| `ptrc_gc_init(world, seed)` | Initialisiert den 3D-Windkanal, `60.000` `1+12`-Cluster und den initialen Lockstep-Hash. |
| `ptrc_gc_step_tick(world)` | Führt einen deterministischen Physik-Tick (inkl. adaptiver `1..8` Sektor-Engines) aus, aktualisiert alle Trefferzähler und prüft `tunneling_escapes == 0`. |
| `ptrc_gc_compute_lockstep_hash(world)` | Berechnet die 64-Bit-Prüfsumme über den gesamten Weltzustand. |
| `ptrc_gc_render_rgb24(world, w, h, out)` | Rendert die Beobachterperspektive in `0x00`-freies RGB24 (`1920 × 1080`). |

---

## 3. Verifikation & Live-Showcase im Terminal

```bash
# 1. Build- & Lockstep-Determinismus-Audit ausfuehren
chmod +x embedded/game_collision/verify_ptrc_collision.sh
./embedded/game_collision/verify_ptrc_collision.sh

# 2. Full-HD Game-Collision Live-Showcase (inkl. Echtzeit-Trefferzaehler & Lockstep-Hash) starten
python3 src/00_ptrc_game_collision_live.py
```
