# SPDX-FileCopyrightText: 2023-2026, NORCE Research AS
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=C0301,C0115,C0116

"""Update the models reference data"""

import shutil
from dataclasses import dataclass
from pathlib import Path

from opm.io.ecl import EclFile as OpmFile

from pyopmnearwell.core.pyopmnearwell import main

TEST_PATH = Path(__file__).parent.parent


@dataclass(frozen=True)
class ModelTemplateExpected:
    template: str
    pressure_first: float
    pressure_last: float


@dataclass(frozen=True)
class ModelCase:
    model: str
    default_template: str
    keywords: tuple[str, ...]
    templates: tuple[str, ...]


CASES: tuple[ModelCase, ...] = (
    ModelCase(
        model="co2eor",
        default_template="sandve2022",
        keywords=("SOLVENT", "WSOLVENT"),
        templates=("bhpcontrol", "lowerlayerinjection", "sandve2022"),
    ),
    ModelCase(
        model="foam",
        default_template="bhpcontrol",
        keywords=("FOAM", "WFOAM"),
        templates=("bhpcontrol",),
    ),
    ModelCase(
        model="co2store",
        default_template="topinjection",
        keywords=("CO2STORE",),
        templates=(
            "base",
            "no_disgas_no_diffusion",
            "nosaltprec",
            "salinity_uniform_inj",
            "salinity",
            "topinjection",
        ),
    ),
    ModelCase(
        model="h2store",
        default_template="base",
        keywords=("H2STORE",),
        templates=(
            "base",
            "gaswater",
            "hwell",
            "hwellnoise",
            "nodissolution",
            "okoroafor2023",
        ),
    ),
    ModelCase(
        model="h2store",
        default_template="base",
        keywords=("CH4",),
        templates=("H2CH4",),
    ),
    ModelCase(
        model="saltprec",
        default_template="base",
        keywords=("PRECSALT", "PERMFACT", "PCFACT"),
        templates=("base", "uniform"),
    ),
    ModelCase(
        model="biofilm",
        default_template="biofilm",
        keywords=("BIOFILM", "PERMFACT", "BIOFPARA", "PCFACT"),
        templates=("biofilm",),
    ),
)


def write_config_for_template(
    model: str, default_template: str, template: str, tmp_path: Path
) -> Path:
    src = TEST_PATH / "models" / f"{model}.toml"
    dst = tmp_path / f"{model}_{template}.toml"
    content = src.read_text(encoding="utf8")
    content = content.replace(default_template, template)
    dst.write_text(content, encoding="utf8")
    return dst


def run_model(config_path: Path, tmp_path: Path) -> None:
    main(["-i", str(config_path), "-o", str(tmp_path), "-m", "single"])


def extract_pressures(unrst_path: Path) -> tuple[float, float]:
    unrst = OpmFile(str(unrst_path))
    pressure = unrst["PRESSURE", 0]
    return float(pressure[0]), float(pressure[-1])


def generate_updated_cases(
    tmp_path: Path,
) -> list[tuple[ModelCase, list[ModelTemplateExpected]]]:
    results: list[tuple[ModelCase, list[ModelTemplateExpected]]] = []
    for case in CASES:
        template_results: list[ModelTemplateExpected] = []
        for template in case.templates:
            config_path = write_config_for_template(
                case.model, case.default_template, template, tmp_path
            )
            run_model(config_path, tmp_path)
            output_stem = f"{case.model.upper()}_{template.upper()}"
            unrst_path = tmp_path / f"{output_stem}.UNRST"
            pressure_first, pressure_last = extract_pressures(unrst_path)
            template_results.append(
                ModelTemplateExpected(template, pressure_first, pressure_last)
            )
        results.append((case, template_results))
    return results


def format_output(
    updated_cases: list[tuple[ModelCase, list[ModelTemplateExpected]]],
) -> str:
    lines: list[str] = []
    lines.append("CASES: tuple[ModelCase, ...] = (")
    for case, templates in updated_cases:
        lines.append("    ModelCase(")
        lines.append(f'        model="{case.model}",')
        lines.append(f'        default_template="{case.default_template}",')
        keyword_string = ", ".join(f'"{keyword}"' for keyword in case.keywords)
        lines.append(f"        keywords=({keyword_string},),")
        lines.append("        templates=(")
        for template in templates:
            lines.append(
                f'            ModelTemplateExpected("{template.template}", {template.pressure_first}, {template.pressure_last}),'
            )
        lines.append("        ),")
        lines.append("    ),")
    lines.append(")")
    lines.append("")
    return "\n".join(lines)


def main_generate() -> None:
    tmp_path = TEST_PATH / "_regen_tmp"
    tmp_path.mkdir(exist_ok=True)
    updated_cases = generate_updated_cases(tmp_path)
    output_text = format_output(updated_cases)
    output_file = TEST_PATH / "data" / "models_data_updated.txt"
    output_file.write_text(output_text, encoding="utf8")
    shutil.rmtree(tmp_path)


if __name__ == "__main__":
    main_generate()
