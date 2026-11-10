"""Pruebas unitarias del error absoluto medio (MAD)."""

import pytest

from pronosticos import mad

REAL = [141, 138, 150]
PRONOSTICO = [126.67, 133.67, 135.67]


def test_calcula_el_error_absoluto_medio():
    resultado = mad(REAL, PRONOSTICO)

    # (14.33 + 4.33 + 14.33) / 3 = 11.00, calculado de forma independiente.
    # Los decimales se comparan con tolerancia, nunca con igualdad exacta.
    assert resultado == pytest.approx(11.00, abs=0.01)


def test_es_cero_cuando_el_pronostico_es_exacto():
    assert mad([100, 100], [100, 100]) == 0


def test_rechaza_series_de_distinta_longitud():
    with pytest.raises(ValueError, match="mismo número de periodos"):
        mad([100, 110], [100])


def test_rechaza_series_vacias():
    with pytest.raises(ValueError, match="al menos un periodo"):
        mad([], [])
