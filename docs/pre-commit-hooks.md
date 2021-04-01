# Pre-commit hooks
Git's pre-commit hooks are a way of automatically running tasks whenever you commit changes to a branch.

They can help us:
* remove tedious work – organizing import statements
* keep our code clean – identifying unused imports and variables
* catch errors early – detecting syntax errors in python files, and invalid json or yaml files

## The hooks we use
The hooks are configured in `.pre-commit-config.yaml`, and include:
### isort
[isort](https://pycqa.github.io/isort/) organizes import statements according to our [style guide](style-guide.md).

isort is configured in `pyproject.toml`

### flake8
[flake8](https://flake8.pycqa.org/en/latest/) is a powerful code-analysis tool, which can identify syntax errors, PEP8 style violations, unused imports and variables, and a host of other problems.

If you want flake8 to ignore a violation on a particular line, you can add a comment with the error code:
```python
from library import * # noqa: F403
```

flake8 is configured in `setup.cfg`

### Other
A bunch of standard code checkers and cleaners (check-json, check-yaml, end-of-file-fixer, etc.)

## Configuring pre-commit hooks
_More details at [https://pre-commit.com/](https://pre-commit.com/)_

Install pre-commit on the machine hosting the repository
```bash
pip install pre-commit
```

Navigate to the root of the project (where .git is), e.g. `~/redpot-unchained`
```bash
cd ~/redpot-unchained
```

Activate pre-commit on the repository
```bash
pre-commit install
```

The project's hooks (configured in `.pre-commit-config.yaml`) will now run every time you commit.

If a hook automatically modifies your files, it will cause your commit to fail (by design), saying
`files were modified by this hook.` Just commit again.
