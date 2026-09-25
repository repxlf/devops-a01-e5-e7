# MD/RD baseline fixture

```text
make clean
make
./app
```

Expected output: `1`.

The source includes `config.h`. The Makefile intentionally declares `unused.h` instead of `config.h`, so the E3 oracle expects one `MISSING` and one `REDUNDANT` finding.
