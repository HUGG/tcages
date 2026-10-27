# T<sub>c</sub>core

[![PyPI](https://img.shields.io/pypi/v/tccore.svg)](https://pypi.org/project/tccore/)
[![Build](https://github.com/HUGG/tccore/actions/workflows/publish-to-pypi.yml/badge.svg)](https://github.com/HUGG/tccore/actions/workflows/publish-to-pypi.yml)

T<sub>c</sub>core is a Python package for predicting low-temperature thermochronometer ages from a time-temperature (tT) history.
It provides compiled versions of two widely used age prediction codes with a simple Python interface:

- **RDAAM / ZRDAAM** for apatite and zircon (U-Th)/He ages, including the effects of radiation damage on He diffusion ([Flowers et al., 2009](https://doi.org/10.1016/j.gca.2009.01.015); [Guenthner et al., 2013](https://doi.org/10.2475/03.2013.01))
- **ketch** for apatite fission-track (AFT) ages and track-length distributions ([Ketcham et al., 1999](https://doi.org/10.2138/am-1999-0903))

T<sub>c</sub>core is the age prediction engine used by [T<sub>c</sub>1D](https://github.com/HUGG/Tc1D) and [T<sub>c</sub>plotter](https://github.com/HUGG/tcplotter), but it can also be used on its own.

## Installation

T<sub>c</sub>core can be installed using `pip`:

```bash
pip install tccore
```

Pre-built wheels are available for Linux (x86-64 and ARM64), macOS (Intel and Apple silicon) and Windows (x86-64 and ARM64), so no compilers are needed.
T<sub>c</sub>core requires Python 3.10 or newer and NumPy.

> [!NOTE]
> On Windows ARM64, Python 3.11 or newer is needed because NumPy does not provide Windows ARM64 packages for Python 3.10.

### Older versions of T<sub>c</sub>1D and T<sub>c</sub>plotter

Prior to version 0.3, T<sub>c</sub>core was distributed as two command-line programs (`RDAAM_He` and `ketch_aft`) rather than a Python package.
These programs are still needed by T<sub>c</sub>1D versions prior to 0.5.0 and T<sub>c</sub>plotter versions prior to 0.4.0.
They can be downloaded from the [v0.2 release](https://github.com/HUGG/tccore/releases/tag/v0.2) and installation instructions are in the [v0.2 README](https://github.com/HUGG/tccore/blob/v0.2/README.md).

### Building from source

Building from source requires a C/C++ compiler (GCC, Clang or MSVC).
CMake is installed automatically during the build if needed.

```bash
git clone https://github.com/HUGG/tccore.git
cd tccore
pip install .
```

To run the tests:

```bash
pip install pytest
pytest tests
```

## Quick start

```python
import tccore

# Define thermal history with cooling from 300 °C at 30 Ma to 0 °C today (rate of 10 °C/Myr)
times = [0.0, 30.0]    # Ma, youngest (present day) first
temps = [0.0, 300.0]   # °C

# Calculate (U-Th)/He and AFT ages
he = tccore.he_ages(
    times, temps,
    ap_rad=60.0, ap_u=10.0, ap_th=40.0,    # apatite: radius (µm), U and Th (ppm)
    zr_rad=60.0, zr_u=100.0, zr_th=40.0,   # zircon: radius (µm), U and Th (ppm)
)
aft = tccore.aft_age(times, temps)

# Print results
print(f"AHe: {he.ahe_corr:.2f} Ma")
print(f"AFT: {aft.age:.2f} Ma (mean track length {aft.mean_length:.2f} µm)")
print(f"ZHe: {he.zhe_corr:.2f} Ma")
```

Output:

```
AHe: 6.13 Ma
AFT: 10.68 Ma (mean track length 13.94 µm)
ZHe: 13.20 Ma
```

## Citing T<sub>c</sub>core

If you use T<sub>c</sub>core in your work, please cite the papers describing the models it implements (see [References](#references)).
If you use T<sub>c</sub>core through T<sub>c</sub>1D or T<sub>c</sub>plotter, please also cite those packages as described in their documentation.

## References

- Flowers, R. M., Ketcham, R. A., Shuster, D. L., and Farley, K. A.: Apatite (U-Th)/He thermochronometry using a radiation damage accumulation and annealing model, *Geochimica et Cosmochimica Acta*, 73, 2347–2365, <https://doi.org/10.1016/j.gca.2009.01.015>, 2009.
- Guenthner, W. R., Reiners, P. W., Ketcham, R. A., Nasdala, L., and Giester, G.: Helium diffusion in natural zircon: Radiation damage, anisotropy, and the interpretation of zircon (U-Th)/He thermochronology, *American Journal of Science*, 313, 145–198, <https://doi.org/10.2475/03.2013.01>, 2013.
- Ketcham, R. A., Donelick, R. A., and Carlson, W. D.: Variability of apatite fission-track annealing kinetics III: Extrapolation to geological time scales, *American Mineralogist*, 84, 1235–1255, <https://doi.org/10.2138/am-1999-0903>, 1999.
- Ketcham, R. A., Carter, A., Donelick, R. A., Barbarand, J., and Hurford, A. J.: Improved modeling of fission-track annealing in apatite, *American Mineralogist*, 92, 799–810, <https://doi.org/10.2138/am.2007.2281>, 2007.
- Ketcham, R. A., Gautheron, C., and Tassan-Got, L.: Accounting for long alpha-particle stopping distances in (U–Th–Sm)/He geochronology: Refinement of the baseline case, *Geochimica et Cosmochimica Acta*, 75, 7779–7791, <https://doi.org/10.1016/j.gca.2011.10.011>, 2011.

## License

T<sub>c</sub>core is distributed under the [GNU General Public License v3.0](LICENSE).
