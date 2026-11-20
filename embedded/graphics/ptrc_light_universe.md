<!--
# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics Engine
# Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.
#
# LICENSE & LIABILITY NOTICE:
# Academic, non-commercial research and evaluation is permitted strictly under 
# the terms of the GNU Affero General Public License version 3 (AGPLv3).
# For the complete, unedited license text see: https://gnu.org
#
# ANY COMMERCIAL DEPLOYMENT, production utilization, or proprietary enterprise 
# integration requires a separate, individually negotiated commercial infrastructure 
# waiver issued directly by the author.
#
# WARRANTY DISCLAIMER: THIS SOFTWARE IS PROVIDED "AS IS" AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE SYSTEMATICALLY DISCLAIMED.
# ==============================================================================
-->

# pTRC Light Universe — 1-Bit Integer Physics & Observer Graphics (`v4.6.0`)

**Discrete 1-Bit Integer Physics, 144-Facet Anisotropy, 1+12 Space-Crystal Lattice & Adaptive Multi-Engine Windtunnel**  
Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.  
License: GNU Affero General Public License v3.0 (AGPL-3.0).

---

## 1. Architektur-Überblick (`v4.6.0`)

`ptrc_light_universe` ist eine deterministische Ganzzahl-Physik- und Beobachter-Grafik-Engine in **ISO C11** mit bit-identischer **Python-Referenz**. Die Engine arbeitet ohne Gleitkommazahlen (`float`/`double`), ohne dynamische Heap-Allokation im Laufzeit-Loop und ohne Null-Zustände (`0` / `0x00`).

* **Nullfreier Raum (\(\mathbb{Z}^3 \setminus \{0\}\)):** Sämtliche Raumkoordinaten, Impulsvektoren und Farb-/Zustandsbytes schließen die Null aus. Der Ursprungsübergang erfolgt deterministisch über den gekreuzten Plichta-Spiegel (`-1 <-> +1`).
* **144-Facetten-Kristallanisotropie:** Der interne Zustandsspeicher besteht aus **144 Facetten** (`120` Gedächtnisfacetten + `24` Kontaktstellen / Junctions). Jede Stoßwechselwirkung koppelt über die aktive 24-Takt-Phase (`clock_phase_24`) und den 137er-Spiegelimpuls (`PTRC_GFX_TAKT_137`).
* **Superkompaktes 1+12-Raumgitter (Kuboktaeder / FCC):** Alle Gitterplätze sind über gerade Koordinatenparität (`(x + y + z) & 1 == 0`) versetzt. Jeder Cluster repräsentiert **1 Zentralkristall + 12 Hüllkristalle** (`13` Raumkristalle).
* **Hardware-`int32`-GPU-Erkennung & CPU-Fallback:** Beim Start prüft die Engine automatisch via `dlopen("libOpenCL.so.1")` auf Hardware-`int32`-ALUs (`INT32-GPU`) und fällt ohne OpenCL-ICD nahtlos und bit-identisch auf `CPU-INT` zurück.

---

## 2. 1-Byte-Register (`state_byte`, `1..255`)

| Bit-Position | Maske | Funktion | Wertebereich |
| :--- | :--- | :--- | :--- |
| **Bit 7** | `0x80` | **Kohäsions- & Bindungsanker** (`cohesion_anchor`) | `0` = frei, `1` = stark gebundener Cluster (hält `1+12`-Nachbarschaft zusammen) |
| **Bits 6..5** | `0x60` | **Optik- & Materialmodus** (`optics_mode`) | `0` = Opak, `1` = Transluzent, `2` = Kristallin, `3` = Feldgekoppelt |
| **Bits 4..0** | `0x1F` | **Digitale Wellenlänge** (`wavelength_id`) | `1..31` (Retina-Farb- & Impulstransposition) |

---

## 3. 3D-Windkanal-Bemaßung (`32 cm × 18 cm × 8 cm`)

| Komponente | Real-Bemaßung | Nullfreies Kristallgitter (\(\mathbb{Z}^3 \setminus \{0\}\)) | Physikalische Rolle |
| :--- | :--- | :--- | :--- |
| **Windkanal-Volumen** | **32 cm × 18 cm × 8 cm** | `X ∈ [-960..+960]`, `Y ∈ [-540..+540]`, `Z ∈ [-240..+240]` | Laminare Einströmung links (`-X`), Auslass & Rückführung rechts (`+X`) |
| **Luftmolekül-Agenten** | **60.000 Cluster** | Je **1+12 = 13 Raumkristalle** (`780.000` aktive Kristalle) | Kollisions- & Kohäsionsaustausch über 65.536 FCC-Slots + 144-Facetten-Streuung |
| **Rotierende 3D-Pyramide** | **Höhe 9,0 cm, Basis 6,4 cm** | Zentrum `X = -320` (linkes Drittel), `3.288` Sub-Winkelstufen | Teilt den Hauptstrom, bildet Hochdruckkeil & Kármán-Wirbelstraße |
| **Rotierende 3D-Kugel** | **Ø 9,0 cm** (`R = 270`) | Zentrum `X = +320, Y = -200, Z = -1` (100 % Kanaltiefe) | Zentriert im oberen Luftstrom für maximale Interaktion & Magnus-Ablenkung |

## 4. Verifizierte Benchmark-Statistik (`v4.6.0`, 60 s Dauerlauf, Linux x86_64)

Gemessen mit `src/00_benchmark_ptrc_graphics.py --seconds 60` bei nativer **Full-HD-Auflösung (`1920 × 1080`)**, **8 adaptiven pTRC-Sektor-Engines (`1..8` dynamisch)** und `60.000` `1+12`-Clustern (`780.000` Raumkristalle, davon `20.080` gebundene Kohäsions-Cluster):

| Metrik | Messwert (`v4.6.0`) |
| :--- | :--- |
| **Messdauer / Frames / Takte** | `60.07 s` \| `511` Full-HD Frames \| `1.022` Physik-Takte |
| **Physik-Takt-Latenz (60.000 Cluster)** | **Mean `2.372 ms`** \| Std `0.263 ms` \| Median `2.291 ms` \| P95 `2.846 ms` \| P99 `3.642 ms` |
| **Full-HD Software-Z-Buffer (`1+12` Projektion)** | **Mean `113.425 ms`** \| Std `3.565 ms` \| Median `113.283 ms` \| P95 `119.100 ms` \| P99 `126.723 ms` |
| **Gesamt-Framerate (`2 Takte + Full-HD Render`)** | **`8.51 FPS`** (Mean `115.851 ms`, Median `117.881 ms`) |
| **Kollisions- & Interaktionsrate** | **`21.522.758` Kollisionen** (`358.285` Interaktionen/s) |
| **Raumkristall-Updates pro Sekunde** | **`13.270.161` Kristall-Berechnungen/s** |
| **Null-Byte-Verletzungen (`0x00` in \(\mathbb{Z}^3 \setminus \{0\}\))** | **`0` (100 % nullfrei & bit-identisch C11 \(\leftrightarrow\) Python)** |

---

## 5. Adaptive Engine-Skalierung (`1..8`) & Ereignishorizont (`PTRC_RENDER_STALL`)

Jedem Beobachtercluster wird anhand seiner lokalen Informationsdichte (`active_load`) und gebundenen Kohäsions-Cluster (`bound_clusters`) dynamisch die benötigte Anzahl an pTRC-Engines zugewiesen (`assigned_engines = 1..8`):

| Effektive Last (`load + bound >> 7`) | Zugewiesene pTRC-Engines | Beobachter-Intervall | Systemzustand |
| :--- | :--- | :--- | :--- |
| `< 950` | `1` Engine | `137` Takte | **Laminar / Minimal-Last** (`PTRC_RENDER_READY`) |
| `950 .. 1349` | `2` Engines | `137` Takte | **Leichte Verdichtung** |
| `1350 .. 1899` | `4` Engines | `274` Takte (`2 × 137`) | **Wirbelstau / Lokale Zeitdilatation** |
| `>= 1900` (`load < 2600`) | `8` Engines (Maximum) | `548` Takte (`4 × 137`) | **Hochdichte-Kohäsionscluster** |
| `active_load >= 2600` | `8` Engines (gesättigt) | `0` (Ausgesetzt) | **Ereignishorizont / Singularität** (`PTRC_RENDER_STALL`) |

---

## 6. Dateien & Schnellstart

* `embedded/graphics/ptrc_light_universe.h` — C11-Header & Datenstrukturen (`ptrc_gfx_ctx_t`).
* `embedded/graphics/ptrc_light_universe.c` — C11-Implementierung (Adaptive `1..8` Engines, `int32`-GPU-Probe, Z-Buffer).
* `src/ptrc_light_universe.py` — Bit-identische Python-Referenzimplementierung.
* `src/00_test_ptrc_graphics_parity.py` — Bit-Paritäts- & `0x00`-Freiheits-Audit (`C11 <-> Python`).
* `src/00_ptrc_live_viewer.py` — Interaktiver Full-HD Live-Viewer (`1920 × 1080`).
* `src/00_benchmark_ptrc_graphics.py` — Statistischer Langzeit-Benchmark (`ptrc_graphics_benchmark_report.json`).

```bash
python3 src/00_test_ptrc_graphics_parity.py
python3 src/00_benchmark_ptrc_graphics.py --seconds 60
python3 src/00_ptrc_live_viewer.py
```

