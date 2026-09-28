# MD/RD baseline fixture

```text
make clean
make
./app
```

Expected output: `1`.

The full E3 behaviour sequence, automated by `scripts/run_lab.py`, is:

1. Change only `config.h` from `VALUE 1` to `VALUE 2`; incremental `make` still prints `1` because the dependency is missing.
2. Run `make clean && make`; the same source now prints `2`.
3. Change only the unused but declared `unused.h`; incremental `make` recompiles `main.o` and still prints `2`.

The source includes `config.h`. The Makefile intentionally declares `unused.h` instead of `config.h`, so the E3 oracle expects one `MISSING` and one `REDUNDANT` finding.
