# ${package_title}

[![PyPI version](https://badge.fury.io/py/${package_name}.svg)](https://badge.fury.io/py/${package_name})
[![Test](https://github.com/${github_username}/${package_name}/actions/workflows/test.yml/badge.svg)](https://github.com/${github_username}/${package_name}/actions/workflows/test.yml)
[![Lint](https://github.com/${github_username}/${package_name}/actions/workflows/lint.yml/badge.svg)](https://github.com/${github_username}/${package_name}/actions/workflows/lint.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

${description}

## Installation

```bash
pip install ${package_name}
```

With [uv](https://github.com/astral-sh/uv):

```bash
uv pip install ${package_name}
```

## Usage

```python
import ${import_name}

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
git clone https://github.com/${github_username}/${package_name}.git
cd ${package_name}

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
