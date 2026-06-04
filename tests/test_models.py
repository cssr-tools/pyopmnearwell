# SPDX-FileCopyrightText: 2023-2026, NORCE Research AS
# SPDX-FileCopyrightText: 2023 UiB
# SPDX-License-Identifier: GPL-3.0
# pylint: disable=R0913,R0917

"""Test the different models"""

from dataclasses import dataclass
from pathlib import Path

import pytest
from opm.io.ecl import EclFile as OpmFile

from pyopmnearwell.core.pyopmnearwell import main

TEST_PATH = Path(__file__).parent


@dataclass(frozen=True)
class ModelTemplateExpected:
    """Pressure reference data"""

    template: str
    pressure_first: float
    pressure_last: float


@dataclass(frozen=True)
class ModelCase:
    """Configuration to test"""

    model: str
    default_template: str
    keywords: tuple[str, ...]
    templates: tuple[ModelTemplateExpected, ...]


CASES: tuple[ModelCase, ...] = (
    ModelCase(
        model="co2eor",
        default_template="sandve2022",
        keywords=(
            "SOLVENT",
            "WSOLVENT",
        ),
        templates=(
            ModelTemplateExpected("bhpcontrol", 3983.984619140625, 4000.0),
            ModelTemplateExpected("lowerlayerinjection", 3983.984619140625, 4000.0),
            ModelTemplateExpected("sandve2022", 3983.984619140625, 4000.0),
        ),
    ),
    ModelCase(
        model="foam",
        default_template="bhpcontrol",
        keywords=(
            "FOAM",
            "WFOAM",
        ),
        templates=(ModelTemplateExpected("bhpcontrol", 3983.984619140625, 4000.0),),
    ),
    ModelCase(
        model="co2store",
        default_template="topinjection",
        keywords=("CO2STORE",),
        templates=(
            ModelTemplateExpected("base", 100.13536834716797, 102.32533264160156),
            ModelTemplateExpected(
                "no_disgas_no_diffusion", 100.13536834716797, 102.32533264160156
            ),
            ModelTemplateExpected("nosaltprec", 100.1397705078125, 102.5321273803711),
            ModelTemplateExpected(
                "salinity_uniform_inj", 100.13536834716797, 102.32533264160156
            ),
            ModelTemplateExpected("salinity", 100.13536834716797, 102.32533264160156),
            ModelTemplateExpected(
                "topinjection", 100.13536834716797, 102.32533264160156
            ),
        ),
    ),
    ModelCase(
        model="h2store",
        default_template="base",
        keywords=("H2STORE",),
        templates=(
            ModelTemplateExpected("base", 40.04848861694336, 40.92131805419922),
            ModelTemplateExpected("gaswater", 40.04848861694336, 40.92131805419922),
            ModelTemplateExpected("hwell", 40.04848861694336, 40.92131805419922),
            ModelTemplateExpected("hwellnoise", 40.04848861694336, 40.92131805419922),
            ModelTemplateExpected(
                "nodissolution", 40.04848861694336, 40.92131805419922
            ),
            ModelTemplateExpected(
                "okoroafor2023", 40.04848861694336, 40.92131805419922
            ),
        ),
    ),
    ModelCase(
        model="h2store",
        default_template="base",
        keywords=("CH4",),
        templates=(
            ModelTemplateExpected("H2CH4", 40.0012321472168, 40.023380279541016),
        ),
    ),
    ModelCase(
        model="saltprec",
        default_template="base",
        keywords=(
            "PRECSALT",
            "PERMFACT",
            "PCFACT",
        ),
        templates=(
            ModelTemplateExpected("base", 213.10597229003906, 217.5573272705078),
            ModelTemplateExpected("uniform", 213.10597229003906, 217.5573272705078),
        ),
    ),
    ModelCase(
        model="biofilm",
        default_template="biofilm",
        keywords=(
            "BIOFILM",
            "PERMFACT",
            "BIOFPARA",
            "PCFACT",
        ),
        templates=(
            ModelTemplateExpected("biofilm", 40.048500061035156, 54.38808059692383),
        ),
    ),
)


def assert_close(
    rel_tol: float,
    abs_tol: float,
    actual: float,
    expected: float,
    label: str,
    case_id: str,
) -> None:
    """Assert two floating-point values are approximately equal with a useful message."""
    assert actual == pytest.approx(
        expected, rel=rel_tol, abs=abs_tol
    ), f"{case_id}: {label} mismatch, expected {expected}, got {actual}"


def write_config_for_template(
    model: str,
    default_template: str,
    template: str,
    tmp_path: Path,
) -> Path:
    """Copy the base model TOML file into tmp_path and replace the default template
    token with the selected template using pure Python"""
    src = TEST_PATH / "models" / f"{model}.toml"
    dst = tmp_path / f"{model}_{template}.toml"

    content = src.read_text(encoding="utf8")
    content = content.replace(default_template, template)
    dst.write_text(content, encoding="utf8")

    return dst


def run_model(config_path: Path, tmp_path: Path) -> None:
    """Run pyopmnearwell using the provided config file."""
    main(
        [
            "-i",
            str(config_path),
            "-o",
            str(tmp_path),
            "-m",
            "single",
        ]
    )


def assert_output_files_exist(tmp_path: Path, output_stem: str, case_id: str) -> None:
    """Verify that required output files were generated."""
    for ext in ("DATA", "UNRST"):
        output_file = tmp_path / f"{output_stem}.{ext}"
        assert (
            output_file.exists()
        ), f"{case_id}: missing output file {output_file.name}"


def validate_data_file(
    data_path: Path, keywords: tuple[str, ...], case_id: str
) -> None:
    """Validate that all expected keywords appear in the generated DATA file."""
    content = data_path.read_text(encoding="utf8")
    for keyword in keywords:
        assert (
            keyword in content
        ), f"{case_id}: keyword '{keyword}' not found in {data_path.name}"


def validate_unrst(
    rel_tol: float,
    abs_tol: float,
    unrst: OpmFile,
    expected: ModelTemplateExpected,
    case_id: str,
) -> None:
    """Validate UNRST-derived pressure values."""
    pressure = unrst["PRESSURE", 0]
    assert_close(
        rel_tol,
        abs_tol,
        float(pressure[0]),
        expected.pressure_first,
        "PRESSURE[0]",
        case_id,
    )
    assert_close(
        rel_tol,
        abs_tol,
        float(pressure[-1]),
        expected.pressure_last,
        "PRESSURE[-1]",
        case_id,
    )


@pytest.mark.parametrize(
    "case",
    CASES,
    ids=[
        f"{case.model}:{','.join(t.template for t in case.templates)}" for case in CASES
    ],
)
def test_models(
    case: ModelCase,
    rel_tol: float,
    abs_tol: float,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """See tests/models."""
    monkeypatch.chdir(tmp_path)

    for template_case in case.templates:
        config_path = write_config_for_template(
            model=case.model,
            default_template=case.default_template,
            template=template_case.template,
            tmp_path=tmp_path,
        )

        run_model(config_path, tmp_path)

        output_stem = f"{case.model.upper()}_{template_case.template.upper()}"
        case_id = f"{case.model}/{template_case.template}"

        assert_output_files_exist(tmp_path, output_stem, case_id)

        data_path = tmp_path / f"{output_stem}.DATA"
        validate_data_file(data_path, case.keywords, case_id)

        unrst_path = tmp_path / f"{output_stem}.UNRST"
        unrst = OpmFile(str(unrst_path))
        validate_unrst(rel_tol, abs_tol, unrst, template_case, case_id)
