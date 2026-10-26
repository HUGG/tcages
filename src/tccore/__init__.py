"""Python interface to the RDAAM (U-Th)/He and ketch AFT age prediction libraries."""

from __future__ import annotations

import os
import platform
import threading
from ctypes import CDLL, POINTER, byref, c_double, c_float, c_int, c_void_p
from dataclasses import dataclass
from importlib.metadata import version
from importlib.resources import files

import numpy as np

# Versioning
try:
    from importlib.metadata import version
    from importlib.resources import files

    __version__ = version("tccore")
except ImportError:
    __version__ = "dev"

__all__ = ["he_ages", "aft_age", "HeResult", "AftResult", "TccoreError"]


class TccoreError(RuntimeError):
    """Raised when an age calculation fails."""


# --- Library loading (once, at import) --------------------------------------
def _load(base: str) -> CDLL:
    name = f"{base}.dll" if platform.system() == "Windows" else f"lib{base}.so"
    path = files("tccore").joinpath(name)
    try:
        return CDLL(os.fspath(path))
    except OSError as e:
        raise ImportError(f"Could not load {name} from {path}: {e}") from e


_rdaam = _load("RDAAM")
_rdaam.make_path.argtypes = []
_rdaam.make_path.restype = c_void_p
_rdaam.path_push.argtypes = [c_void_p, c_double, c_double]
_rdaam.path_push.restype = None
_rdaam.del_path.argtypes = [c_void_p]
_rdaam.del_path.restype = None
_rdaam.run_RDAAM_He.argtypes = [
    c_void_p,                                   # TTPath*
    c_double, c_double, c_double,               # ap_rad, ap_U, ap_Th
    POINTER(c_double), POINTER(c_double),       # ap_age*, ap_corrAge*
    c_double,                                   # total_He
    c_double, c_double, c_double,               # zr_rad, zr_U, zr_Th
    POINTER(c_double), POINTER(c_double),       # zr_age*, zr_corrAge*
    POINTER(c_int), POINTER(c_int),             # ap_success*, zr_success*
]
_rdaam.run_RDAAM_He.restype = None

_ketch = _load("ketch")
_ketch.ketch_main.argtypes = [
    POINTER(c_int), POINTER(c_float), POINTER(c_float),  # ntime*, time[], temp[]
    POINTER(c_double), POINTER(c_double),                # alo*, final_age*
    POINTER(c_double), POINTER(c_double),                # oldest_age*, fmean*
    POINTER(c_double),                                   # fdist[201]
]
_ketch.ketch_main.restype = None

# Both C codes use global state: serialise calls within a process
_rdaam_lock = threading.Lock()
_ketch_lock = threading.Lock()

_NBINS = 200
_LENGTHS = (np.arange(_NBINS) + 0.5) * 20.0 / _NBINS   # bin centres, um


# --- Results ------------------------------------------------------------------
@dataclass(frozen=True)
class HeResult:
    ahe: float        # uncorrected apatite (U-Th)/He age, Ma
    ahe_corr: float   # alpha-ejection-corrected AHe age, Ma
    zhe: float
    zhe_corr: float


@dataclass(frozen=True)
class AftResult:
    age: float            # Ma
    oldest_age: float     # age of oldest track, Ma
    mean_length: float    # um
    lengths: np.ndarray   # bin centres, um (200)
    pdf: np.ndarray       # track-length probability density (200)


# --- Input checks ---------------------------------------------------------------
def _check_path(times, temps) -> tuple[np.ndarray, np.ndarray]:
    t = np.asarray(times, dtype=np.float64).ravel()
    T = np.asarray(temps, dtype=np.float64).ravel()
    if t.shape != T.shape:
        raise ValueError(f"times and temps differ in length ({t.size} vs {T.size})")
    if t.size < 2:
        raise ValueError("A tT path needs at least two points")
    if not (np.isfinite(t).all() and np.isfinite(T).all()):
        raise ValueError("tT path contains NaN or inf")
    if np.any(np.diff(t) < 0):
        raise ValueError("times must increase from present (youngest first)")
    return t, T


# --- Public API ------------------------------------------------------------------
def he_ages(times, temps, ap_rad, ap_u, ap_th, zr_rad, zr_u, zr_th) -> HeResult:
    """Predict apatite and zircon (U-Th)/He ages with RDAAM and ZRDAAM.

    times : Ma, youngest (present) first.  temps : deg C.
    Radius in um, U and Th in ppm.
    """
    t, T = _check_path(times, temps)
    out = [c_double() for _ in range(4)]
    ap_ok, zr_ok = c_int(), c_int()
    with _rdaam_lock:
        path = _rdaam.make_path()
        try:
            for ti, Ti in zip(t, T):
                _rdaam.path_push(path, ti, Ti)
            _rdaam.run_RDAAM_He(
                path, ap_rad, ap_u, ap_th, byref(out[0]), byref(out[1]), 0.0,
                zr_rad, zr_u, zr_th, byref(out[2]), byref(out[3]),
                byref(ap_ok), byref(zr_ok),
            )
        finally:
            _rdaam.del_path(path)   # always free the C++ object
    if ap_ok.value != 1 or zr_ok.value != 1:
        raise TccoreError(f"RDAAM failed (apatite={ap_ok.value}, zircon={zr_ok.value})")
    return HeResult(*(o.value for o in out))


def aft_age(times, temps, alo: float = 16.3) -> AftResult:
    """Predict an apatite fission-track age and length distribution with ketch.

    times : Ma, youngest (present) first.  temps : deg C.
    alo : initial track length, um.
    """
    t, T = _check_path(times, temps)
    t32 = np.ascontiguousarray(t, dtype=np.float32)   # ketch takes float[]
    T32 = np.ascontiguousarray(T, dtype=np.float32)
    age, oldest, fmean = c_double(), c_double(), c_double()
    fdist = (c_double * (_NBINS + 1))()
    with _ketch_lock:
        _ketch.ketch_main(
            byref(c_int(t32.size)),
            t32.ctypes.data_as(POINTER(c_float)),
            T32.ctypes.data_as(POINTER(c_float)),
            byref(c_double(alo)), byref(age), byref(oldest), byref(fmean), fdist,
        )
    pdf = np.frombuffer(fdist, dtype=np.float64)[1:].copy()  # drop fdist[0] padding
    return AftResult(age.value, oldest.value, fmean.value, _LENGTHS.copy(), pdf)