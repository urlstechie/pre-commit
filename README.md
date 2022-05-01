<div style="text-align:center"><img src="https://raw.githubusercontent.com/urlstechie/urlchecker-python/master/docs/urlstechie.png"/></div>

# urlchecker pre-commit

You can use urlchecker-python with [pre-commit](https://pre-commit.com/)!

## Setup

Add the following entry to your `.pre-commit-config.yaml` in the root of
your repository:

```yaml
repos:
-   repo: https://github.com/urlstechie/pre-commit
    rev: 0.0.11
    hooks:
    -   id: urlchecker-check
        additional_dependencies: [urlchecker>=0.0.28]
```

You can add additional args (those you would add to the check command) to further
customize the run:


```yaml
repos:
-   repo: https://github.com/urlstechie/pre-commit
    rev: 0.0.11
    hooks:
    -   id: urlchecker-check
        additional_dependencies: [urlchecker>=0.0.28]
```

Make sure that you get the latest version from [releases](https://github.com/urlstechie/pre-commit/releases/tag/0.0.11).
Note that the `--files` argument that previously accepted patterns for urlchecker
for this module is instead `--patterns`. The reason is because pre-commit is already
going to provide a list of filenames to check verbatim with the commit, and your
additional specification of `--patterns` is primarily to further filter this list.

## Run

And then you can install and run!

```bash
$ pre-commit install
```
```bash
$ git commit -a -s -m 'testing a commit'
[INFO] Initializing environment for https://github.com/urlstechie/pre-commit.
[INFO] Initializing environment for https://github.com/urlstechie/pre-commit:urlchecker>=0.0.28.
[INFO] Installing environment for https://github.com/urlstechie/pre-commit.
[INFO] Once installed this environment will be reused.
[INFO] This may take a few minutes...
urlchecker...............................................................Passed
[main 5fb40a8] testing a commit
 1 file changed, 1 insertion(+)
```


## Support

If you need help, or want to suggest a project for the organization,
please [open an issue](https://github.com/urlstechie/pre-commit)
