# Developer's notes

We use [`black`](https://github.com/psf/black) and [`isort`](https://github.com/pycqa/isort) for autoformatting and [`flake8`](https://github.com/PyCQA/flake8) for linting.

You are encouraged to add editor support (enable autoformat on save w/ black) and show linting errors with flake8. See the documentation for your editor to set up.

To manually run each of the tools:

black:

```sh
black . --check --diff
```

isort:

```sh
isort . --check --diff
```

flake8:

```sh
flake8 .
```

We also have pre-commit hooks. You can install them with `pre-commit install`
