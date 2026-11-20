# pTRC Light Universe (`ptrc_light_universe`) — v4.5.0

**Discrete 1-Bit Integer Physics, 144-Facet Anisotropy & 1+12 Space-Crystal Windtunnel**  
Copyright (c) 2026 Kurt Guido Wirminghaus. All Rights Reserved.  
License: GNU Affero General Public License v3.0 (AGPL-3.0).

---

## 1. Kernprinzipien der Engine

`ptrc_light_universe` ist eine deterministische, reine Ganzzahl-Physik- und Beobachter-Grafik-Engine ohne Gleitkommazahlen (`float`/`double`), ohne dynamische Speicherallokation im Laufzeitbetrieb und ohne Null-Zustände (`0` / `0x00`).

* **Nullfreier Diskreter Raum (\(\mathbb{Z}^3 \setminus \{0\}\)):** Jede Raumkoordinate, jeder Impulsvektor und jedes Farb-/Zustandsbyte schließt die Null strikt aus. Der Ursprungsübergang erfolgt über den gekreuzten Plichta-Spiegel (`-1 <-> +1`).
* **144-Facetten-Kristallanisotropie:** Der interne Zustandsspeicher besteht aus **144 Facetten** (`120` Gedächtnisfacetten + `24` Kontaktstellen / Junctions). Jede Kollision koppelt über die aktive 24-Takt-Phase (`clock_phase_24`) und den 137er-Spiegelimpuls (`PTRC_GFX_TAKT_137`) deterministisch auf die 24 Richtungsvektoren.
* **Superkompaktes 1+12-Raumgitter (FCC / Kuboktaeder-Packung):** Um orthogonale Treppenstufen und kubische Moiré-Interferenzen zu verhindern, sind alle Gitterplätze über gerade Koordinatenparität (`(x + y + z) & 1 == 0`) versetzt. Jeder Cluster besteht aus **1 Zentralkristall + 12 kuboktaedrischen Hüllkristallen** (`13` Raumkristalle).

---

## 2. 1-Byte-Register (`state_byte`, `1..255`)

Jeder Cluster kodiert seinen vollständigen optischen und physikalischen Zustand in einem einzigen nullfreien Byte (`uint8_t`, Wertebereich `1..255`):

| Bit-Position | Maske | Bedeutung | Wertebereich |
| :--- | :--- | :--- | :--- |
| **Bit 7** | `0x80` | **Kaskaden- & Kohäsionsanker** (`cascade_anchor`) | `0` = frei, `1` = stark gebundener Cluster |
| **Bits 6..5** | `0x60` | **Optik- & Materialmodus** (`optics_mode`) | `0` = Opak, `1` = Transluzent, `2` = Kristallin, `3` = Feldgekoppelt |
| **Bits 4..0** | `0x1F` | **Digitale Wellenlänge** (`wavelength_id`) | `1..31` (Farb- & Impulstransposition auf die Retina) |

---

## 3. 3D-Windkanal-Bemaßung (`32 cm × 18 cm × 8 cm`)

| Komponente | Real-Bemaßung | Nullfreies Kristallgitter (\(\mathbb{Z}^3 \setminus \{0\}\)) | Funktion im Experiment |
| :--- | :--- | :--- | :--- |
| **Windkanal-Volumen** | **32 cm × 18 cm × 8 cm** | `X ∈ [-960..+960]`, `Y ∈ [-540..+540]`, `Z ∈ [-240..+240]` | Laminare Einströmung links (`-X`), Auslass & Rückführung rechts (`+X`) |
| **Luftmolekül-Agenten** | **60.000 Cluster** | Je **1+12 = 13 Raumkristalle** (`780.000` aktive Kristallknoten) | Stoßwechselwirkung über 65.536 FCC-Slots + 144-Facetten-Streuung |
| **Rotierende 3D-Pyramide** | **Höhe 9,0 cm, Basis 6,4 cm** | Zentrum `X = -320` (linkes Drittel), `3.288` Sub-Winkelstufen | Teilt den Hauptluftstrom, erzeugt Hochdruckkeil & Kármán-Wirbel |
| **Rotierende 3D-Kugel** | **Ø 4,5 cm** (`2/3` Pyramide) | Zentrum `X = +260, Y = -220, Z = -15` (rechts oben nahe Mitte) | Nutzt den oberen Luftstrom für sekundäre Wirbelablösung (Magnus-Effekt) |

## 4. Adaptive Multi-Engine-Architektur & Ereignishorizont

### Parallele pTRC-Sektor-Engines (`PTRC_PARALLEL_ENGINES`)
Die C11-Engine (`ptrc_gfx_step_takt_parallel`) teilt die `60.000` Molekül-Cluster über POSIX-Threads (`pthread`) auf parallele pTRC-Engines auf. Alle Sektor-Engines arbeiten auf demselben deterministischen 137er-Mastertakt.

### Beobachter-Synchronisation & Ereignishorizont (`PTRC_RENDER_STALL`)
Wenn die lokale Kollisions- und Informationsdichte (`active_load`) in einem Beobachtercluster ansteigt, verlangsamt sich das lokale Beobachter-Renderintervall dynamisch in Vielfachen des 137er-Takts:

| `active_load` (Last-Index) | Beobachter-Renderintervall | Systemzustand |
| :--- | :--- | :--- |
| `< 1350` | `137` Takte | **Laminar / Echtzeit** (`PTRC_RENDER_READY`) |
| `1350 .. 1899` | `274` Takte (`2 × 137`) | **Verdichtung / Wirbelstau** (lokale Zeitdilatation) |
| `1900 .. 2599` | `548` Takte (`4 × 137`) | **Hochdichte-Cluster** (starke Verlangsamung) |
| `>= 2600` | `0` (Ausgesetzt) | **Ereignishorizont / Singularität** (`PTRC_RENDER_STALL`) |

---

## 5. Dateien & Ausführung

* `embedded/graphics/ptrc_light_universe.h` — C11-Header & Datenstrukturen (`ptrc_gfx_ctx_t`).
* `embedded/graphics/ptrc_light_universe.c` — C11-Implementierung (Single-Thread, 4-Engine-Parallel, Z-Buffer-Renderer).
* `src/ptrc_light_universe.py` — Bit-identische Python-Referenzimplementierung.
* `src/00_test_ptrc_graphics_parity.py` — Bit-Paritäts- & `0x00`-Freiheits-Audit (`C11 <-> Python`).
* `src/00_ptrc_live_viewer.py` — Interaktiver Full-HD Live-Viewer (`1920 × 1080`) mit Laufzeit- & Takt-HUD.
* `src/00_benchmark_ptrc_graphics.py` — Statistischer Langzeit-Benchmark (Mittelwert, Median, StdAbw, P95/P99).

### Schnellstart im Terminal

```bash
# 1. Bit-Paritaets- & Nullfreiheits-Audit ausfuehren
python3 src/00_test_ptrc_graphics_parity.py

# 2. Statistischer 30-Sekunden-Benchmark (frei waehlbar via --seconds)
python3 src/00_benchmark_ptrc_graphics.py --seconds 30

# 3. Full-HD Live-Windkanal starten (1920x1080, 4x Parallel-Engines)
python3 src/00_ptrc_live_viewer.py
```
