# Python Development Guide

## Version
Target Python version: **3.13+**

## Code Philosophy
- **Clean & Expressive**: Write code that is easy to read and understand.
- **Modern**: Leverage the latest Python features (3.13+).
- **Elegant**: Prefer simple, elegant solutions over complex ones.
- **No Overengineering**: Avoid unnecessary abstractions. YAGNI (You Ain't Gonna Need It).
- **Not Overfitted**: Solutions should be general enough for the domain but specific to the problem.

## Coding Standards

### Type Hinting
- **Do NOT** use the `typing` module for standard collections or optionals.
- Use built-in types:
    - `list[str]` instead of `List[str]`
    - `dict[str, int]` instead of `Dict[str, int]`
    - `tuple[int, ...]` instead of `Tuple[int, ...]`
- Use the union operator `|` for optional or union types:
    - `str | None` instead of `Optional[str]`
    - `int | float` instead of `Union[int, float]`

### Data Classes
- Use `@dataclass` for data holding classes.
- Use `slots=True` where appropriate for performance (Python 3.10+).

### Docstrings
- Use Google-style docstrings.

### Testing
- Use `pytest` for all tests.
- Follow TDD: Write tests *before* implementation.
- Use `pytest-mock` for mocking dependencies.

### Dependency Management
- Use `uv` for all package management.
