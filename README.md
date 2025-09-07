# IG-Unfollowers

Short one-liner about the project.

## Table of Contents
- [Overview](#overview)
- [Getting Your Instagram Files](#getting-your-instagram-files)
- [Requirements](#requirements)
- [Usage](#usage)
- [Examples](#examples)
- [Ignore List](#ignore-list)
- [Output](#output)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## Overview
What the tool does and what it does **not** do.

## Getting Your Instagram Files
Step-by-step to download Followers & Following export.

## Requirements
- Python 3.9+
- (Optional) `bs4` for stronger HTML parsing

## Usage
```bash
python3 foll.py -i following.html -e followers.html \
  [--csv results.csv] [--json results.json] \
  [--print all|unfollowers|fans|mutuals|summary] [--sort] [--ignore ignore.txt]
```

## Flags

-i, --following …

-e, --followers …

--csv, --json, --print, --sort, --ignore

Examples
python3 foll.py -i following.html -e followers.html
python3 foll.py -i following.html -e followers.html --print all --sort --ignore ignore.txt

Ignore List

One username per line (case/@ ignored).

Output

Show a small sample of the “Summary” and lists.

Troubleshooting

Common issues and fixes.

Contributing

PRs welcome. If IG changes export format, open an issue with a tiny redacted snippet.
