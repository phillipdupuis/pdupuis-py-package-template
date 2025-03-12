# ${project_name}

[![PyPI version](https://badge.fury.io/py/${project_name}.svg)](https://badge.fury.io/py/${project_name})
[![Test](https://github.com/${github_username}/${project_name}/actions/workflows/test.yml/badge.svg)](https://github.com/${github_username}/${project_name}/actions/workflows/test.yml)
[![Lint](https://github.com/${github_username}/${project_name}/actions/workflows/lint.yml/badge.svg)](https://github.com/${github_username}/${project_name}/actions/workflows/lint.yml)
[![Coverage Status](https://codecov.io/github/${github_username}/${project_name}/branch/main/graph/badge.svg)](https://codecov.io/github/${github_username}/${project_name})

${description}

## Installation

```bash
pip install ${project_name}
```

With [uv](https://github.com/astral-sh/uv):

```bash
uv pip install ${project_name}
```

## Usage

```python
import ${project_name}

# Add usage examples here
```

## Development

This project uses modern Python tooling:

- [uv](https://github.com/astral-sh/uv) for dependency management
- [pytest](https://docs.pytest.org/) for testing
- [ruff](https://github.com/astral-sh/ruff) for linting and formatting

### Setup

```bash
# Clone the repository
git clone https://github.com/${github_username}/${project_name}.git
cd ${project_name}

# Install development dependencies
uv pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
ruff check .
ruff format .
```

## License

[GNU General Public License v3.0](LICENSE)
