# Contributing
Contributions are welcome.
Please create an issue before writing a pull request so we can discuss what needs to be changed.

# Testing
The code can be tested with [hatch](https://hatch.pypa.io/latest/)

* `hatch run cov:test` can be used to test all supported python versions and to check for coverage.
* `hatch test -py 3.10 -- --sw` runs pytest for python 3.10 with the `--sw` argument.


# Coverage
This project has a hard coverage requirement of 100%.
The goal here is to find different edge cases which might have bugs.

However, it is possible to exclude some code from the coverage.

Code can be marked with `pragma: no cover`, if it can not be tested for some reason.
This makes it easy to spot uncovered code in the source.

Impossible conditions can be handled with `assert False`.
``` python
if some_condition:
    ...
if some_other_condition:
    ...
else:
    assert False, "unreachable because ..."
```
This serves also as an additional check during runtime.


# Commits
Please use [prek](https://prek.j178.dev/) for your commits. It uses the
`.pre-commit-config.yaml` configuration included in this project.

# Changelog
Add a changelog fragment for user-visible changes with
`uv run scriv create --add --edit`. The fragments are collected automatically
when the release pull request is created.

Pull requests containing `feat:` or `fix:` commits (including scopes and breaking
changes, such as `feat(cli):` or `fix!:`) must add at least one new, non-empty
`changelog.d/*.md` fragment. CI checks the commits and files of the entire pull
request, so the fragment can be added in a separate commit.

Install the Git hooks once with `uvx prek install`. This installs the
usual commit and commit-message checks, plus a changelog check that runs
automatically before `git push`. The changelog check inspects committed changes on the whole branch,
so the fragment can be added in a separate commit before pushing.

To run the changelog check manually:

```sh
uvx prek run check-changelog --stage manual
```

The hook detects the base branch from `origin/HEAD`, falling back to
`origin/main`, `origin/master`, `main`, or `master`. Keep the remote references
up to date with `git fetch`. For a different base, configure
`args: [--base-ref, YOUR_BASE_BRANCH]` on the hook. CI uses the PR's exact base
and head commits instead of automatic detection.

Run all regular checks locally with `uvx prek run --all-files`. The CI Lint job
runs those checks and validates the changelog against the PR's exact base and
head commits using a full Git checkout. Monthly hook updates are included in
the existing weekly maintenance workflow; manual maintenance runs update them
as well.

When replacing an existing pre-commit installation, use
`uvx prek install --force` to replace its Git hook shims.

If pre-commit.ci was enabled for this repository, switch any required status
check to `Lint`, then disable the old service after the Lint job is available.
No external CI app is required for these checks.

The regular hooks also reject tracked files matched by repository `.gitignore`
rules. Adding a pattern to `.gitignore` does not stop tracking existing files.
Use `git rm --cached -- <path>` and commit the removal to keep a file local, or
adjust the ignore rules when the file is intentionally tracked. This check
reports problems without changing files or the Git index.
