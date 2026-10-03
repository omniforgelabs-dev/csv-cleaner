# Push this repository to GitHub

This folder is a complete, ready-to-push git repository. No GitHub connection was
available in the environment that produced it, so the push is left to you — it takes
about two minutes.

## 1. Create an empty repository on GitHub

1. Go to <https://github.com/new>.
2. **Repository name:** `csv-cleaner` (or `dataclean`).
3. **Visibility:** Public (or Private, your choice).
4. **Do NOT** initialize with a README, `.gitignore`, or license — this folder already has them.
5. Click **Create repository** and copy the URL shown, e.g.
   `https://github.com/<your-username>/csv-cleaner.git`.

## 2. Push from this folder

Run these commands from inside the `csv-cleaner` directory (the one containing
`pyproject.toml`):

```sh
git init
git add .
git commit -m "Initial commit: dataclean 1.0.0 - dependency-free CSV cleaner and data-quality reporter"
git branch -M main
git remote add origin https://github.com/<your-username>/csv-cleaner.git
git push -u origin main
```

Replace `<your-username>` with your GitHub username.

## 3. If you use SSH instead of HTTPS

```sh
git remote add origin git@github.com:<your-username>/csv-cleaner.git
git push -u origin main
```

## 4. If GitHub asks for a password

GitHub no longer accepts account passwords over HTTPS. Use a **Personal Access Token**
(Settings → Developer settings → Personal access tokens → Fine-grained tokens, with
`Contents: Read and write` on the new repo) as the password, or use the SSH remote above.

## 5. Verify

```sh
git log --oneline
git remote -v
```

Then open `https://github.com/<your-username>/csv-cleaner` in a browser.

## 6. Sanity check before pushing (optional)

```sh
python3 -m unittest discover -s tests -t . -v
```

Expected: `Ran 16 tests ... OK`.

## What is in this folder

```
pyproject.toml            project metadata + `dataclean` console entry point
README.md                 description, usage, examples, exit codes, limitations
LICENSE                   MIT
.gitignore                Python ignores (__pycache__, .venv, out/, *.egg-info, ...)
PUSH_INSTRUCTIONS.md      this file
dataclean/__init__.py     version constant
dataclean/__main__.py     module entry point
dataclean/cli.py          argparse wiring, exit-code mapping, summaries, strict mode
dataclean/reader.py       CSV reading + validation
dataclean/cleaner.py      header/cell normalization, dedupe, fill, CSV writing
dataclean/profiler.py     type inference + report/profile JSON
tests/__init__.py         (empty)
tests/test_cleaner.py     unit tests: normalization, dedupe, fill, inference
tests/test_cli.py         unit tests: exit codes + end-to-end runs
fixtures/sample.csv       messy fixture used by the examples
fixtures/bad.csv          ragged fixture used by the error-path tests
```

`PUSH_INSTRUCTIONS.md` is a convenience file — delete it after pushing if you prefer a
cleaner repository root:

```sh
git rm PUSH_INSTRUCTIONS.md
git commit -m "Remove push instructions"
```
