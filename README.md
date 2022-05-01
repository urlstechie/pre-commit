<div style="text-align:center"><img src="https://raw.githubusercontent.com/urlstechie/urlchecker-python/master/docs/urlstechie.png"/></div>

# urlchecker pre-commit

You can use urlchecker-python with [pre-commit](https://pre-commit.com/)!

## Setup

Add the following entry to your `.pre-commit-config.yaml` in the root of
your repository:

```yaml
repos:
-   repo: https://github.com/urlstechie/pre-commit
    rev: 0.0.1
    hooks:
    -   id: urlchecker-check
        additional_dependencies: [urlchecker>=0.0.28]
```

You can add additional args (those you would add to the check command) to further
customize the run:


```yaml
repos:
-   repo: https://github.com/urlstechie/pre-commit
    rev: 0.0.1
    hooks:
    -   id: urlchecker-check
        additional_dependencies: [urlchecker>=0.0.28]
```

Note that the `--files` argument that previously accepted patterns for urlchecker
for this module is instead `--patterns`. The reason is because pre-commit is already
going to provide a list of filenames to check verbatim with the commit, and your
additional specification of `--patterns` is primarily to further filter this list.

## Run

And then you can run:

```bash
$ pre-commit run
```

or install to your repository:

```bash
$ pre-commit install
```

## Support

If you need help, or want to suggest a project for the organization,
please [open an issue](https://github.com/urlstechie/pre-commit)
