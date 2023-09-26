"""Helper script for Mako templates."""

from typing import Optional

from mako import exceptions
from mako.template import Template


def fill_template(
    var: dict, filename: Optional[str] = None, text: Optional[str] = None
) -> str:
    mytemplate: Template = Template(filename=filename, text=text)
    try:
        filledtemplate = mytemplate.render(**var)
    except Exception as error:
        print(exceptions.text_error_template().render())
        raise (error)
    return filledtemplate
