# SPDX-FileCopyrightText: 2023-2026, NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0913,R0914,R0917

"""Test the different type of grids"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pytest

from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import EclFile as OpmFile

from pyopmnearwell.core.pyopmnearwell import main

TEST_PATH = Path(__file__).parent


@dataclass(frozen=True)
class ResponseExpected:
    """Reference data"""

    dimension: tuple[int, int, int]
    active_cells: int
    cell_volume: float
    porv: float
    dxyz: tuple[float, float, float, float, float, float]
    txyz: tuple[float, float, float]
    pressure: tuple[float, float]


EXPECTED: dict[str, ResponseExpected] = {
    "cake": ResponseExpected(
        dimension=(50, 1, 32),
        active_cells=1600,
        cell_volume=34641017.25777892,
        porv=1445570432.0,
        dxyz=(
            6.387606143951416,
            45.34769821166992,
            3.6878859996795654,
            1128.51904296875,
            1.8749799728393555,
            1.8750200271606445,
        ),
        txyz=(164838.765625, 0.0, 3640986.5),
        pressure=(10.190634727478027, 34.944915771484375),
    ),
    "cartesian": ResponseExpected(
        dimension=(21, 21, 32),
        active_cells=14112,
        cell_volume=240000000.0,
        porv=21415247872.0,
        dxyz=(
            17.326719284057617,
            209.64108276367188,
            17.326719284057617,
            209.64108276367188,
            1.875,
            1.875,
        ),
        txyz=(157792.921875, 157792.921875, 25225494.0),
        pressure=(10.17773151397705, 15.775778770446777),
    ),
    "cartesian2d": ResponseExpected(
        dimension=(10, 1, 32),
        active_cells=320,
        cell_volume=600000.0,
        porv=12850772.0,
        dxyz=(34.653438568115234, 209.64108276367188, 10.0, 10.0, 1.875, 1.875),
        txyz=(279.08758544921875, 0.0, 63063.734375),
        pressure=(10.17773151397705, 15.775778770446777),
    ),
    "coord2d": ResponseExpected(
        dimension=(7, 1, 32),
        active_cells=224,
        cell_volume=34641011.370726645,
        porv=1264404224.0,
        dxyz=(
            51.762290954589844,
            287.4208984375,
            29.88496971130371,
            988.7579956054688,
            1.8749749660491943,
            1.8750200271606445,
        ),
        txyz=(3051.59912109375, 0.0, 3640987.5),
        pressure=(10.91711139678955, 30.848596572875977),
    ),
    "coord3d": ResponseExpected(
        dimension=(7, 7, 32),
        active_cells=1568,
        cell_volume=2400000.0,
        porv=2754004992.0,
        dxyz=(2.0, 90.0, 2.0, 90.0, 1.875, 1.875),
        txyz=(69315.921875, 69315.921875, 252254.9375),
        pressure=(10.17773151397705, 15.775778770446777),
    ),
    "core": ResponseExpected(
        dimension=(50, 9, 9),
        active_cells=2090,
        cell_volume=0.0013004999513626103,
        porv=0.00013422442134469748,
        dxyz=(
            0.009999999776482582,
            0.009999999776482582,
            0.00566666666418314,
            0.00566666666418314,
            0.00566666666418314,
            0.00566666666418314,
        ),
        txyz=(128.0831756591797, 355.0522155761719, 33.97709274291992),
        pressure=(40.000274658203125, 40.00467300415039),
    ),
    "cpg3d": ResponseExpected(
        dimension=(41, 41, 32),
        active_cells=53792,
        cell_volume=239999997.46671194,
        porv=22492059648.0,
        dxyz=(
            8.230551719665527,
            110.05720520019531,
            8.230551719665527,
            110.05720520019531,
            1.8749849796295166,
            1.8750100135803223,
        ),
        txyz=(521988.6875, 579231.25, 25225496.0),
        pressure=(29.492521286010742, 35.095375061035156),
    ),
    "radial": ResponseExpected(
        dimension=(50, 1, 32),
        active_cells=1600,
        cell_volume=25985957.199545294,
        porv=1311122176.0,
        dxyz=(
            5.531829357147217,
            39.27226638793945,
            3.2938029766082764,
            977.4261474609375,
            1.875,
            1.875,
        ),
        txyz=(188249.203125, 0.0, 2731286.0),
        pressure=(10.17773151397705, 15.775778770446777),
    ),
    "tensor2d": ResponseExpected(
        dimension=(22, 1, 32),
        active_cells=704,
        cell_volume=34641016.307188734,
        porv=1404219264.0,
        dxyz=(
            14.895700454711914,
            100.50060272216797,
            8.6000337600708,
            1096.676513671875,
            1.8749799728393555,
            1.8750150203704834,
        ),
        txyz=(31302.095703125, 0.0, 3640986.5),
        pressure=(10.247254371643066, 35.15092849731445),
    ),
    "tensor3d": ResponseExpected(
        dimension=(63, 63, 32),
        active_cells=127008,
        cell_volume=240000000.0,
        porv=22891900928.0,
        dxyz=(
            5.215385437011719,
            72.25807189941406,
            5.215385437011719,
            72.25807189941406,
            1.875,
            1.875,
        ),
        txyz=(1340666.5, 1340666.5, 25225494.0),
        pressure=(10.17773151397705, 15.775778770446777),
    ),
}


def assert_close(
    rel_tol: float,
    abs_tol: float,
    actual: float,
    expected: float,
    label: str,
    cfg_file: str,
) -> None:
    """Assert two floating-point values are approximately equal with a useful message."""
    assert actual == pytest.approx(
        expected, rel=rel_tol, abs=abs_tol
    ), f"{cfg_file}: {label} mismatch, expected {expected}, got {actual}"


def assert_output_files_exist(tmp_path: Path, case_name: str, cfg_file: str) -> None:
    """Verify that all required output files were generated."""
    for ext in ("UNRST", "EGRID", "INIT"):
        output_file = tmp_path / f"{case_name}.{ext}"
        assert (
            output_file.exists()
        ), f"{cfg_file}: missing output file {output_file.name}"


def run_pyopmnearwell(cfg_file: str, tmp_path: Path) -> None:
    """Run the pyopmnearwell CLI for a specific geometry case."""
    case_name = cfg_file
    main(
        [
            "-i",
            str(TEST_PATH / "geometries" / f"{case_name}.toml"),
            "-o",
            str(tmp_path),
            "-m",
            "single",
        ],
    )


def validate_grid(
    rel_tol: float,
    abs_tol: float,
    egrid: OpmGrid,
    expected: ResponseExpected,
    cfg_file: str,
) -> None:
    """Validate EGRID-derived properties."""
    nx, ny, nz = egrid.dimension

    assert (nx, ny, nz) == expected.dimension, (
        f"{cfg_file}: dimension mismatch, "
        f"expected {expected.dimension}, got {(nx, ny, nz)}"
    )

    assert egrid.active_cells == expected.active_cells, (
        f"{cfg_file}: active cell mismatch, "
        f"expected {expected.active_cells}, got {egrid.active_cells}"
    )

    total_cell_volume = float(np.sum(egrid.cellvolumes()))
    assert_close(
        rel_tol,
        abs_tol,
        total_cell_volume,
        expected.cell_volume,
        "total cell volume",
        cfg_file,
    )


def validate_init(
    rel_tol: float,
    abs_tol: float,
    init: OpmFile,
    expected: ResponseExpected,
    cfg_file: str,
) -> None:
    """Validate INIT-derived properties."""
    total_porv = float(np.sum(init["PORV"]))
    assert_close(rel_tol, abs_tol, total_porv, expected.porv, "PORV", cfg_file)

    for i, axis in enumerate(("X", "Y", "Z")):
        dkey = f"D{axis}"
        tkey = f"TRAN{axis}"

        actual_min = float(np.min(init[dkey]))
        actual_max = float(np.max(init[dkey]))
        actual_trans_sum = float(np.sum(init[tkey]))

        expected_min = expected.dxyz[2 * i]
        expected_max = expected.dxyz[2 * i + 1]
        expected_trans = expected.txyz[i]

        assert_close(
            rel_tol, abs_tol, actual_min, expected_min, f"min({dkey})", cfg_file
        )
        assert_close(
            rel_tol, abs_tol, actual_max, expected_max, f"max({dkey})", cfg_file
        )
        assert_close(
            rel_tol, abs_tol, actual_trans_sum, expected_trans, f"sum({tkey})", cfg_file
        )


def validate_unrst(
    rel_tol: float,
    abs_tol: float,
    unrst: OpmFile,
    expected: ResponseExpected,
    cfg_file: str,
) -> None:
    """Validate UNRST-derived properties."""
    pressure = unrst["PRESSURE", 0]
    assert_close(
        rel_tol, abs_tol, pressure[0], expected.pressure[0], "PPRESSURE[0]", cfg_file
    )
    assert_close(
        rel_tol, abs_tol, pressure[-1], expected.pressure[-1], "PPRESSURE[-1]", cfg_file
    )


@pytest.mark.parametrize("cfg_file", EXPECTED.keys())
def test_geometries(
    cfg_file: str, rel_tol: float, abs_tol: float, tmp_path: Path
) -> None:
    """See tests/geometries"""

    expected = EXPECTED[cfg_file]
    case_name = cfg_file.upper()

    run_pyopmnearwell(cfg_file, tmp_path)
    assert_output_files_exist(tmp_path, case_name, cfg_file)

    egrid = OpmGrid(str(tmp_path / f"{case_name}.EGRID"))
    validate_grid(rel_tol, abs_tol, egrid, expected, cfg_file)

    init = OpmFile(str(tmp_path / f"{case_name}.INIT"))
    validate_init(rel_tol, abs_tol, init, expected, cfg_file)

    unrst = OpmFile(str(tmp_path / f"{case_name}.UNRST"))
    validate_unrst(rel_tol, abs_tol, unrst, expected, cfg_file)
