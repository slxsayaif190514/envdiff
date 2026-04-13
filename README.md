# envdiff

A CLI tool that compares `.env` files across environments and highlights missing or mismatched keys.

---

## Installation

```bash
pip install envdiff
```

Or install from source:

```bash
git clone https://github.com/yourname/envdiff.git
cd envdiff && pip install -e .
```

---

## Usage

Compare two `.env` files:

```bash
envdiff .env.development .env.production
```

**Example output:**

```
✔  DB_HOST          present in both
✘  API_KEY          missing in .env.production
~  LOG_LEVEL        dev=debug | prod=info
✘  CACHE_URL        missing in .env.development
```

Compare multiple environments at once:

```bash
envdiff .env.development .env.staging .env.production
```

Show only missing keys:

```bash
envdiff .env.development .env.production --only-missing
```

---

## Options

| Flag             | Description                          |
|------------------|--------------------------------------|
| `--only-missing` | Show only keys absent in any file    |
| `--no-color`     | Disable colored output               |
| `--quiet`        | Exit with non-zero code if diff found |

---

## License

MIT © [yourname](https://github.com/yourname)