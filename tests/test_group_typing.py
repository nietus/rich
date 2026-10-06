"""Regression coverage for parameter types preserved by the group decorator."""

import pytest


def test_group_preserves_parameter_types(tmp_path):
    mypy = pytest.importorskip("mypy.api")
    source = tmp_path / "group_typing.py"
    source.write_text(
        """
from typing import Callable, Iterable
from rich.console import Group, group

@group()
def render(value: str, *, count: int = 1) -> Iterable[str]:
    yield value * count

class Renderer:
    @group(fit=False)
    def render(self, value: str) -> Iterable[str]:
        yield value

result: Group = render("hello", count=2)
bound: Callable[[str], Group] = Renderer().render
bound("hello")
render(42)
render()
render("hello", unknown=True)
render("hello", 2)
""",
        encoding="utf-8",
    )
    output, errors, status = mypy.run(
        ["--follow-imports=silent", "--no-incremental", str(source)]
    )
    assert not errors
    assert status == 1, output
    assert output.count("error:") == 4, output
    assert "[arg-type]" in output
    assert "[call-arg]" in output
