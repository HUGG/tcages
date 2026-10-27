import numpy as np
import pytest
import tcages

T_PATH = ([0.0, 30.0], [0.0, 300.0])  # 10 °C/Myr linear cooling
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


@pytest.mark.parametrize(
    "t, T",
    [([30.0, 0.0], [300.0, 0.0]), ([0.0, 20.0], [0.0]), ([0.0, np.nan], [0.0, 300.0])],
)
def test_bad_paths(t, T):
    with pytest.raises(ValueError):
        tcages.he_ages(t, T, **GRAINS)


def test_numpy_array_inputs():
    """NumPy arrays give the same results as lists."""
    t = np.array(T_PATH[0])
    T = np.array(T_PATH[1])
    assert tcages.he_ages(t, T, **GRAINS) == tcages.he_ages(*T_PATH, **GRAINS)
    a_list = tcages.aft_age(*T_PATH)
    a_array = tcages.aft_age(t, T)
    assert a_array.age == a_list.age
    np.testing.assert_array_equal(a_array.pdf, a_list.pdf)


def test_aft_initial_track_length():
    """A shorter initial track length gives shorter predicted track lengths."""
    default = tcages.aft_age(*T_PATH)
    short = tcages.aft_age(*T_PATH, alo=15.0)
    assert short.mean_length < default.mean_length


def test_aft_track_length_distribution():
    a = tcages.aft_age(*T_PATH)
    np.testing.assert_allclose(a.lengths, (np.arange(200) + 0.5) * 0.1)
    assert np.all(a.pdf >= 0.0)
    # Mean of the distribution matches the reported mean track length
    assert (a.lengths * a.pdf).sum() * 0.1 == pytest.approx(a.mean_length, rel=1e-3)
    # The oldest track cannot be younger than the AFT age
    assert a.oldest_age >= a.age


def test_repeated_oldest_time_raises():
    """Repeating the oldest time point makes RDAAM fail, which raises an error."""
    with pytest.raises(tcages.TcagesError):
        tcages.he_ages([0.0, 15.0, 30.0, 30.0], [0.0, 150.0, 300.0, 300.0], **GRAINS)
