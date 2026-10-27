import numpy as np
import pytest
import tcages

T_PATH = ([0.0, 30.0], [0.0, 300.0])   # 10 °C/Myr linear cooling
GRAINS = dict(ap_rad=60, ap_u=10, ap_th=40, zr_rad=60, zr_u=100, zr_th=40)

def test_he_known_answer():
    h = tcages.he_ages(*T_PATH, **GRAINS)
    assert h.ahe_corr == pytest.approx(6.1321, rel=1e-3)
    assert h.zhe_corr == pytest.approx(13.2037, rel=1e-3)

def test_aft_known_answer():
    a = tcages.aft_age(*T_PATH)
    assert a.age == pytest.approx(10.679, rel=1e-3)
    assert a.mean_length == pytest.approx(13.937, rel=1e-3)
    assert a.pdf.size == 200
    assert a.pdf.sum() * 0.1 == pytest.approx(1.0, abs=1e-3)

def test_age_order():
    h = tcages.he_ages(*T_PATH, **GRAINS)
    assert h.ahe_corr < tcages.aft_age(*T_PATH).age < h.zhe_corr

def test_repeatable():
    assert tcages.he_ages(*T_PATH, **GRAINS) == tcages.he_ages(*T_PATH, **GRAINS)

@pytest.mark.parametrize("t, T", [([30.0, 0.0], [300.0, 0.0]),
                                  ([0.0, 20.0], [0.0]),
                                  ([0.0, np.nan], [0.0, 300.0])])
def test_bad_paths(t, T):
    with pytest.raises(ValueError):
        tcages.he_ages(t, T, **GRAINS)