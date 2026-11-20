# ==============================================================================
# pTRC Framework - Discrete 1-Bit Integer Physics & Observer Windtunnel v4.5.0
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

"""
Bit-Paritaets- & Nullfreiheits-Audit (Z^3 \\ {0}) zwischen C11 und Python
fuer die pTRC 3D-Raumkristall-Engine v4.5.0 (inkl. 1-Byte Kaskaden & Z-Occlusion).
"""

from __future__ import annotations

import ctypes
import subprocess
import sys
import tempfile
from pathlib import Path

from ptrc_light_universe import (
    PTRC_GFX_FACETS,
    PTRC_GFX_MEM_FACETS,
    PTRC_GFX_OK,
    PTRC_GFX_PRIME_RINGS,
    PTRC_LATTICE_CELLS,
    PTRC_MAX_IMPULSE_PACKETS,
    PTRC_RENDER_STALL,
    PtrcGfxContext,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
C_SRC = REPO_ROOT / "embedded" / "graphics" / "ptrc_light_universe.c"
C_INC = REPO_ROOT / "embedded" / "graphics"


class CPtrcCrystalCell(ctypes.Structure):
    _fields_ = [
        ("cx", ctypes.c_int8),
        ("cy", ctypes.c_int8),
        ("cz", ctypes.c_int8),
        ("state_byte", ctypes.c_uint8),
        ("impulse", ctypes.c_uint8),
        ("observer_cluster", ctypes.c_uint8),
        ("facet_mem", ctypes.c_uint8 * PTRC_GFX_MEM_FACETS),
    ]


class CPtrcImpulsePacket(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_int32),
        ("y", ctypes.c_int32),
        ("z", ctypes.c_int32),
        ("dir_idx", ctypes.c_uint8),
        ("impulse", ctypes.c_uint8),
        ("wavelength_id", ctypes.c_uint8),
        ("element_id", ctypes.c_uint8),
        ("optics_mode", ctypes.c_uint8),
        ("cascade_root", ctypes.c_uint8),
    ]


class CPtrcGfxCtx(ctypes.Structure):
    _fields_ = [
        ("cells", CPtrcCrystalCell * PTRC_LATTICE_CELLS),
        ("packets", CPtrcImpulsePacket * PTRC_MAX_IMPULSE_PACKETS),
        ("sponge", ctypes.c_int32 * PTRC_GFX_FACETS),
        ("prime_rings", ctypes.c_uint32 * PTRC_GFX_PRIME_RINGS),
        ("takt_counter", ctypes.c_uint64),
        ("clock_phase_24", ctypes.c_uint32),
        ("active_load", ctypes.c_uint32),
        ("render_interval_takts", ctypes.c_uint32),
        ("last_render_takt", ctypes.c_uint32),
        ("deflection_count", ctypes.c_uint32),
        ("mirror_pulses", ctypes.c_uint32),
        ("render_status", ctypes.c_int32),
    ]


def build_shared_lib(build_dir: Path) -> ctypes.CDLL:
    so_path = build_dir / "libptrc_light_universe.so"
    cmd = [
        "gcc",
        "-std=c11",
        "-O2",
        "-Wall",
        "-Wextra",
        "-Werror",
        "-shared",
        "-fPIC",
        f"-I{C_INC}",
        str(C_SRC),
        "-o",
        str(so_path),
    ]
    subprocess.run(cmd, check=True)
    lib = ctypes.CDLL(str(so_path))

    lib.ptrc_gfx_init.argtypes = [ctypes.POINTER(CPtrcGfxCtx), ctypes.c_uint64]
    lib.ptrc_gfx_init.restype = ctypes.c_int

    lib.ptrc_gfx_step_takt.argtypes = [ctypes.POINTER(CPtrcGfxCtx)]
    lib.ptrc_gfx_step_takt.restype = ctypes.c_int

    lib.ptrc_gfx_render_observer_rgb24.argtypes = [
        ctypes.POINTER(CPtrcGfxCtx),
        ctypes.c_uint32,
        ctypes.c_uint32,
        ctypes.POINTER(ctypes.c_uint8),
    ]
    lib.ptrc_gfx_render_observer_rgb24.restype = ctypes.c_int

    lib.ptrc_gfx_wipe.argtypes = [ctypes.POINTER(CPtrcGfxCtx)]
    lib.ptrc_gfx_wipe.restype = None
    return lib


def run_parity_audit() -> int:
    seed = 137210144
    width, height = 320, 240

    with tempfile.TemporaryDirectory() as tmp:
        lib = build_shared_lib(Path(tmp))
        c_ctx = CPtrcGfxCtx()
        assert lib.ptrc_gfx_init(ctypes.byref(c_ctx), seed) == PTRC_GFX_OK

        py_ctx = PtrcGfxContext(seed=seed)

        for _ in range(137):
            assert lib.ptrc_gfx_step_takt(ctypes.byref(c_ctx)) == PTRC_GFX_OK
            assert py_ctx.step_takt() == PTRC_GFX_OK

        assert c_ctx.takt_counter == py_ctx.takt_counter
        assert c_ctx.active_load == py_ctx.active_load
        assert c_ctx.deflection_count == py_ctx.deflection_count
        assert c_ctx.mirror_pulses == py_ctx.mirror_pulses
        assert c_ctx.render_interval_takts == py_ctx.render_interval_takts
        assert c_ctx.render_status == py_ctx.render_status

        for i in range(PTRC_LATTICE_CELLS):
            cc = c_ctx.cells[i]
            pc = py_ctx.cells[i]
            assert cc.cx != 0 and cc.cy != 0 and cc.cz != 0
            assert cc.state_byte != 0 and cc.impulse != 0
            assert (cc.cx, cc.cy, cc.cz) == (pc.cx, pc.cy, pc.cz)
            assert cc.state_byte == pc.state_byte
            assert cc.impulse == pc.impulse

        c_buf = (ctypes.c_uint8 * (width * height * 3))()
        rc = lib.ptrc_gfx_render_observer_rgb24(ctypes.byref(c_ctx), width, height, c_buf)
        assert rc in (PTRC_GFX_OK, PTRC_RENDER_STALL)

        c_bytes = bytes(c_buf)
        py_bytes = py_ctx.render_observer_rgb24(width, height)

        assert b"\x00" not in c_bytes, "Verstoss: 0x00 Byte im C-Frame gefunden!"
        assert c_bytes == py_bytes, "Paritaets-Abweichung zwischen C11 und Python!"

        lib.ptrc_gfx_wipe(ctypes.byref(c_ctx))
        print(
            f"[PASS] C11 <-> Python 100% Bit-Paritaet | Takt={py_ctx.takt_counter} | "
            f"Last={py_ctx.active_load} | Intervall={py_ctx.render_interval_takts} | "
            f"Umlenkungen={py_ctx.deflection_count} | 0x00-Bytes=0"
        )
    return 0


if __name__ == "__main__":
    sys.exit(run_parity_audit())
