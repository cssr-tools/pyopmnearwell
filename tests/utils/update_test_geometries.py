# SPDX-FileCopyrightText: 2023-2026, NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0914,C0115,C0116

"""Update the geometries reference data"""

import shutil
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from opm.io.ecl import EGrid as OpmGrid
from opm.io.ecl import EclFile as OpmFile

from pyopmnearwell.core.pyopmnearwell import main

TEST_PATH = Path(__file__).parent.parent


@dataclass(frozen=True)
class ResponseExpected:
    dimension: tuple[int, int, int]
    active_cells: int
    cell_volume: float
    porv: float
    dxyz: tuple[float, float, float, float, float, float]
    txyz: tuple[float, float, float]
    pressure: tuple[float, float]


CASES: tuple[str, ...] = (
    "cake",
    "cartesian",
    "cartesian2d",
    "coord2d",
    "coord3d",
    "core",
    "cpg3d",
    "radial",
    "tensor2d",
    "tensor3d",
)


def run_pyopmnearwell(case_name: str, tmp_path: Path) -> None:
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


def extract_values(case_name: str, tmp_path: Path) -> ResponseExpected:
    upper_name = case_name.upper()

    egrid = OpmGrid(str(tmp_path / f"{upper_name}.EGRID"))
    init = OpmFile(str(tmp_path / f"{upper_name}.INIT"))
    unrst = OpmFile(str(tmp_path / f"{upper_name}.UNRST"))

    nx, ny, nz = egrid.dimension
    active_cells = egrid.active_cells
    cell_volume = float(np.sum(egrid.cellvolumes()))
    porv = float(np.sum(init["PORV"]))

    dxyz_values: list[float] = []
    txyz_values: list[float] = []

    for axis in ("X", "Y", "Z"):
        dkey = f"D{axis}"
        tkey = f"TRAN{axis}"

        dmin = float(np.min(init[dkey]))
        dmax = float(np.max(init[dkey]))
        tsum = float(np.sum(init[tkey]))

        dxyz_values.extend([dmin, dmax])
        txyz_values.append(tsum)

    pressure = unrst["PRESSURE", 0]
    pressure_values = (float(pressure[0]), float(pressure[-1]))

    return ResponseExpected(
        dimension=(nx, ny, nz),
        active_cells=active_cells,
        cell_volume=cell_volume,
        porv=porv,
        dxyz=(
            dxyz_values[0],
            dxyz_values[1],
            dxyz_values[2],
            dxyz_values[3],
            dxyz_values[4],
            dxyz_values[5],
        ),
        txyz=(txyz_values[0], txyz_values[1], txyz_values[2]),
        pressure=pressure_values,
    )


def generate_expected(tmp_path: Path) -> dict[str, ResponseExpected]:
    results: dict[str, ResponseExpected] = {}
    for case_name in CASES:
        run_pyopmnearwell(case_name, tmp_path)
        results[case_name] = extract_values(case_name, tmp_path)
    return results


def format_output(expected: dict[str, ResponseExpected]) -> str:
    lines: list[str] = []
    lines.append("EXPECTED: dict[str, ResponseExpected] = {")

    for case_name, value in expected.items():
        lines.append(f'    "{case_name}": ResponseExpected(')
        lines.append(f"        dimension={value.dimension},")
        lines.append(f"        active_cells={value.active_cells},")
        lines.append(f"        cell_volume={value.cell_volume},")
        lines.append(f"        porv={value.porv},")
        lines.append(f"        dxyz={value.dxyz},")
        lines.append(f"        txyz={value.txyz},")
        lines.append(f"        pressure={value.pressure},")
        lines.append("    ),")
        lines.append("")

    lines.append("}")
    return "\n".join(lines)


def main_generate() -> None:
    tmp_path = TEST_PATH / "_regen_tmp_geom"
    tmp_path.mkdir(exist_ok=True)
    expected = generate_expected(tmp_path)
    output_text = format_output(expected)
    output_file = TEST_PATH / "data" / "geometries_data_updated.txt"
    output_file.write_text(output_text, encoding="utf8")
    shutil.rmtree(tmp_path)


if __name__ == "__main__":
    main_generate()
