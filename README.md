# Git Inquisitor

## Description

A git repository analysis tool designed to provide teams with useful information about a repository and its contributors. It provides history details from the HEAD of the provided repository, file level contribution statistics (enhanced blame), and contributor level statistics similar to what is provided by GitHub.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

**Mac and Linux:**

It is recommended to use [pipx](https://github.com/pypa/pipx) for installation. This will put the tool on your path so it can be used from anywhere.

```
pipx install git-inquisitor
```

### Manual Install (Mac/Linux)

```
python -m pip install git-inquisitor
```

## Usage

```
❯ git-inquisitor --help
Usage: git-inquisitor [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  collect
  report
```

**Collecting repository information:**

```
❯ git-inquisitor collect --help
Usage: git-inquisitor collect [OPTIONS] REPO_PATH

Options:
  --help  Show this message and exit.
```

**Produce report against collected information:**

```
❯ git-inquisitor report --help
Usage: git-inquisitor report [OPTIONS] REPO_PATH {html|json}

Options:
  -o, --output-file-path TEXT  Output file path
  --help                       Show this message and exit.
```

## Contributing

Guidelines for contributing to the project and how to submit pull requests.
