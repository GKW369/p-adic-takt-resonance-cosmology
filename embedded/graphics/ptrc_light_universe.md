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

# pTRC Light Universe — 1-Bit Integer Physics & Observer Graphics (`v4.5.0`)

**Discrete 1-Bit Integer Physics, 144-Facet Anisotropy & 1+12 Space-Crystal Windtunnel**  
Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.  
License: GNU Affero General Public License v3.0 (AGPL-3.0).

---

## 1. Architektur-Überblick

`ptrc_light_universe` ist eine deterministische Ganzzahl-Physik- und Beobachter-Grafik-Engine in **ISO C11** mit bit-identischer **Python-Referenz**. Die Engine arbeitet ohne Gleitkommazahlen (`float`/`double`), ohne dynamische Heap-Allokation im Laufzeit-Loop und ohne Null-Zustände (`0` / `0x00`).

* **Nullfreier Raum (\(\mathbb{Z}^3 \setminus \{0\}\)):** Sämtliche Raumkoordinaten, Impulsvektoren und Farb-/Zustandsbytes schließen die Null aus. Der Ursprungsübergang erfolgt deterministisch über den gekreuzten Plichta-Spiegel (`-1 <-> +1`).
* **144-Facetten-Kristallanisotropie:** Der interne Zustandsspeicher besteht aus **144 Facetten** (`120` Gedächtnisfacetten + `24` Kontaktstellen / Junctions). Jede Stoßwechselwirkung koppelt über die aktive 24-Takt-Phase (`clock_phase_24`) und den 137er-Spiegelimpuls (`PTRC_GFX_TAKT_137`).
* **Superkompaktes 1+12-Raumgitter (Kuboktaeder / FCC):** Alle Gitterplätze sind über gerade Koordinatenparität (`(x + y + z) & 1 == 0`) versetzt, um orthogonale Treppen und kubische Moiré-Muster zu eliminieren. Jeder Cluster repräsentiert **1 Zentralkristall + 12 Hüllkristalle** (`13` Raumkristalle).

---

## 2. 1-Byte-Register (`state_byte`, `1..255`)

| Bit-Position | Maske | Funktion | Wertebereich |
| :--- | :--- | :--- | :--- |
| **Bit 7** | `0x80` | **Kaskaden- & Kohäsionsanker** (`cascade_anchor`) | `0` = frei, `1` = gebundener Cluster |
| **Bits 6..5** | `0x60` | **Optik- & Materialmodus** (`optics_mode`) | `0` = Opak, `1` = Transluzent, `2` = Kristallin, `3` = Feldgekoppelt |
| **Bits 4..0** | `0x1F` | **Digitale Wellenlänge** (`wavelength_id`) | `1..31` (Retina-Farb- & Impulstransposition) |

---

## 3. 3D-Windkanal-Bemaßung (`32 cm × 18 cm × 8 cm`)

| Komponente | Real-Bemaßung | Nullfreies Kristallgitter (\(\mathbb{Z}^3 \setminus \{0\}\)) | Physikalische Rolle |
| :--- | :--- | :--- | :--- |
| **Windkanal-Volumen** | **32 cm × 18 cm × 8 cm** | `X ∈ [-960..+960]`, `Y ∈ [-540..+540]`, `Z ∈ [-240..+240]` | Laminare Einströmung links (`-X`), Auslass & Rückführung rechts (`+X`) |
| **Luftmolekül-Agenten** | **60.000 Cluster** | Je **1+12 = 13 Raumkristalle** (`780.000` aktive Kristalle) | Kollisionsaustausch über 65.536 FCC-Slots + 144-Facetten-Streuung |
| **Rotierende 3D-Pyramide** | **Höhe 9,0 cm, Basis 6,4 cm** | Zentrum `X = -320` (linkes Drittel), `3.288` Sub-Winkelstufen | Teilt den Hauptstrom, bildet Hochdruckkeil & Kármán-Wirbelstraße |
| **Rotierende 3D-Kugel** | **Ø 4,5 cm** (`2/3` Pyramide) | Zentrum `X = +260, Y = -220, Z = -15` (rechts oben) | Nutzt den oberen Luftstrom für sekundäre Wirbelablösung |

## 4. Verifizierte Benchmark-Statistik (60 s Dauerlauf, Linux x86_64, 4 Kerne)

Gemessen mit `src/00_benchmark_ptrc_graphics.py --seconds 60` bei nativer **Full-HD-Auflösung (`1920 × 1080`)**, `4x` parallelen pTRC-Sektor-Engines (`pthread`) und `60.000` `1+12`-Clustern (`780.000` Raumkristalle):

| Metrik | Messwert |
| :--- | :--- |
| **Messdauer / Frames / Takte** | `60.06 s` \| `592` Full-HD Frames \| `1.184` Physik-Takte |
| **Physik-Takt-Latenz (60.000 Cluster)** | **Mean `1.998 ms`** \| Std `0.246 ms` \| Median `1.997 ms` \| P95 `2.214 ms` \| P99 `3.078 ms` |
| **Full-HD Software-Z-Buffer (`1+12` Projektion)** | **Mean `95.741 ms`** \| Std `2.672 ms` \| Median `95.754 ms` \| P95 `98.796 ms` \| P99 `102.437 ms` |
| **Gesamt-Framerate (`2 Takte + Full-HD Render`)** | **`9.86 FPS`** (Mean `99.745 ms`, Std `2.822 ms`) |
| **Kollisions- & Interaktionsrate** | **`24.802.653` Kollisionen** (`412.981` Interaktionen/s) |
| **Raumkristall-Updates pro Sekunde** | **`15.377.232` Kristall-Berechnungen/s** |
| **Null-Byte-Verletzungen (`0x00` in \(\mathbb{Z}^3 \setminus \{0\}\))** | **`0` (100 % nullfrei & bit-identisch C11 \(\leftrightarrow\) Python)** |

---

## 5. Beobachter-Synchronisation & Ereignishorizont (`PTRC_RENDER_STALL`)

| `active_load` (Last-Index) | Beobachter-Renderintervall | Systemzustand |
| :--- | :--- | :--- |
| `< 1350` | `137` Takte | **Laminar / Echtzeit** (`PTRC_RENDER_READY`) |
| `1350 .. 1899` | `274` Takte (`2 × 137`) | **Verdichtung / Wirbelstau** (lokale Zeitdilatation) |
| `1900 .. 2599` | `548` Takte (`4 × 137`) | **Hochdichte-Cluster** (starke Verlangsamung) |
| `>= 2600` | `0` (Ausgesetzt) | **Ereignishorizont / Singularität** (`PTRC_RENDER_STALL`) |

---

## 6. Dateien & Schnellstart

* `embedded/graphics/ptrc_light_universe.h` — C11-Header & Datenstrukturen (`ptrc_gfx_ctx_t`).
* `embedded/graphics/ptrc_light_universe.c` — C11-Implementierung (Single-Thread, 4-Engine-Parallel, Z-Buffer-Renderer).
* `src/ptrc_light_universe.py` — Bit-identische Python-Referenzimplementierung.
* `src/00_test_ptrc_graphics_parity.py` — Bit-Paritäts- & `0x00`-Freiheits-Audit (`C11 <-> Python`).
* `src/00_ptrc_live_viewer.py` — Interaktiver Full-HD Live-Viewer (`1920 × 1080`).
* `src/00_benchmark_ptrc_graphics.py` — Statistischer Langzeit-Benchmark (`ptrc_graphics_benchmark_report.json`).

```bash
python3 src/00_test_ptrc_graphics_parity.py
python3 src/00_benchmark_ptrc_graphics.py --seconds 60
python3 src/00_ptrc_live_viewer.py
```

