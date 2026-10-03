# Contributing to csv-cleaner

Thanks for taking a look. This is a small, deliberately focused tool — the goal is to stay
dependency-free, predictable, and easy to audit. Contributions that respect that are welcome.

## Ground rules

- **Standard library only.** No new runtime dependencies. This is the project's main selling
  point; a pull request that adds `pandas`, `numpy`, or any third-party import will be declined.
- **Python 3.11+.** The code targets the modern stdlib and does not carry compatibility shims.
- **Deterministic output.** Identical input, flags, and input path must produce byte-identical
  output. Do not introduce timestamps, random ordering, or environment-dependent behaviour.
- **Exit codes are a public contract.** `0` success, `1` data/I-O error, `2` usage error,
  `3` strict-mode warnings. Do not renumber or repurpose them.

## Getting started

```sh
git clone https://github.com/omniforgelabs-dev/csv-cleaner.git
cd csv-cleaner
python3 --version          # must be 3.11 or newer
python3 -m unittest discover -s tests -t . -v
```

You should see `Ran 16 tests ... OK`. There is nothing to install.

## Making a change

1. **Open an issue first** for anything beyond a small fix — it saves you writing code that
   does not fit the project's scope.
2. **Add a test.** Every behaviour change needs a test in `tests/`. Bug fixes should include a
   test that fails before the fix and passes after.
3. **Keep the diff small.** One logical change per pull request.
4. **Run the full suite** before opening the pull request:

   ```sh
   python3 -m unittest discover -s tests -t . -v
   ```

5. **Do not reformat unrelated code.** Whitespace-only diffs make review harder.

## What is in scope

- Bug fixes in header normalization, deduplication, missing-value handling, or type inference.
- New flags that fit the existing CLI shape and are off by default.
- Documentation improvements, especially real-world examples.
- Performance work that does not add dependencies.

## What is out of scope

- Streaming / out-of-core processing for multi-GB files (use DuckDB or Polars).
- Delimiter or encoding auto-detection.
- A GUI, TUI, or web interface.
- Anything that adds a runtime dependency.

## Reporting a bug

Please include:

- The exact command you ran.
- The input CSV (or a minimal reproduction that shows the same behaviour).
- The output you got, and the output you expected.
- Your Python version (`python3 --version`) and operating system.

## Code style

Match the surrounding code. The existing modules are small and readable — keep them that way.
Type hints are welcome where they clarify a signature. Comments should explain *why*, not *what*.

## License

By contributing, you agree that your contributions are licensed under the MIT License
(see `LICENSE`).
