"""Helper script for Mako templates."""

from __future__ import annotations

import logging
import pathlib
from typing import Optional

from mako import exceptions
from mako.template import Template

logger = logging.getLogger(__name__)


def fill_template(
    var: dict, filename: Optional[str | pathlib.Path] = None, text: Optional[str] = None
) -> str:
    """
    Fill a Mako template with the given variables.

    The template is either loaded from a file or passed as a string. If rendering the
    template raises an error, render the error s.t. it can be easily debugged.

    Args:
        var (dict): A dictionary containing the variables to be used in the template.
        filename (Optional[str | pathlib.Path], optional): The path to the template
            file. Defaults to None.
        text (Optional[str], optional): The text of the template. Defaults to None.

    Returns:
        str: The filled template as a string.

    Raises:
        Error: When the template cannot be filled.

    """
    # Convert filename to str
    if isinstance(filename, pathlib.Path):
        filename = str(filename)

    mytemplate: Template = Template(filename=filename, text=text)
    try:
        filledtemplate = mytemplate.render(**var)
        if isinstance(filledtemplate, bytes):
            filledtemplate = filledtemplate.decode("utf-8")
    except Exception as error:
        logger.error(exceptions.text_error_template().render())
        raise error
    return filledtemplate
