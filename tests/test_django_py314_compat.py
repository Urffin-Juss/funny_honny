import pytest
from django.template import Context


@pytest.mark.django_db
def test_context_copy_works_on_current_runtime():
    context = Context({"x": 1})
    copied = context.__copy__()

    assert copied["x"] == 1
    assert hasattr(copied, "dicts")
    assert isinstance(copied.dicts, list)
