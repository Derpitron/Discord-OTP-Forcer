test:
    uv run pytest --headless

coverage:
    uv run coverage run -m pytest
    uv run coverage report -m
