# codecrafters-shell

A POSIX-inspired command-line shell built from scratch in pure Python — no
external dependencies, just the standard library. Built as a solution to the
CodeCrafters **"Build Your Own Shell"** challenge.

```
$ pwd
/home/user/projects/codecrafters-shell
$ echo hello world
hello world
$ type cd
cd is a shell builtin
$ ls | grep .py | wc -l
3
```

## Features

- **REPL** — a `$ ` prompt that reads and executes commands in a loop
- **Shell builtins** — `echo`, `pwd`, `cd`, `type`, `exit`
- **External command execution** — runs any real executable found on `PATH`
- **I/O redirection** — `>`, `1>` (stdout, overwrite), `>>`, `1>>` (stdout,
  append), `2>` (stderr, overwrite), `2>>` (stderr, append)
- **Pipelines** — `cmd1 | cmd2 | cmd3`, with builtins and external commands
  freely mixable in the same pipeline
- **Tab completion** — completes commands (builtins + `PATH` executables) and
  filenames, including bash-style behavior: ring the bell on an ambiguous
  match, then list all matches on a second Tab press (any time apart —
  there's no timing window to beat). Works across both GNU `readline` and
  `libedit`-backed Python builds (the latter is common on macOS)

## Requirements

- Python **3.12+** (this project targets **3.14**, per `pyproject.toml`) —
  the code uses nested-quote f-strings (e.g. `f"{"".join(x)}"`), a syntax
  enabled by [PEP 701](https://peps.python.org/pep-0701/), which requires
  Python 3.12 or newer.
- No third-party dependencies.

## Getting Started

Clone the repo and run the shell directly:

```bash
python3 main.py
```

You'll land on a `$ ` prompt. Type `exit` to quit.

## Usage Examples

**Builtins:**
```
$ echo "hello   world"
hello   world
$ type echo
echo is a shell builtin
$ type python3
python3 is /usr/bin/python3
$ cd /tmp
$ pwd
/tmp
```

**Redirection:**
```
$ echo hello > out.txt
$ cat out.txt
hello
$ ls nonexistent 2> errors.txt
$ echo more >> out.txt
```

**Pipelines:**
```
$ cat file.txt | grep error | wc -l
$ echo hi | type ls
```

**Tab completion:** start typing a command or filename and press `Tab`. If
it's unambiguous, it completes right away. If multiple options match, the
first `Tab` rings the bell — press `Tab` again (no need to rush) to see the
full list of matches, the same way bash does.

## Project Structure

Everything lives in a single file, `main.py`, organized into a few logical
sections:

| Section | Responsibility |
|---|---|
| `commandType()` | Implements the `type` builtin |
| `directorySwitch()` | Implements the `cd` builtin |
| `execute_pipeline()` | Parses and runs any command containing `\|` |
| `_list_executables()`, `_longest_common_prefix()`, `_completer()` | Power tab completion |
| `main()` | The REPL loop — reads input and dispatches to the right handler |

## Design Highlights

- **Builtins vs. external commands are treated as fundamentally different
  code paths.** Builtins are Python logic executed directly in-process;
  external commands are launched as separate OS processes via `subprocess`,
  since they're real files that live on disk.
- **Pipelines wire real OS pipes between processes**, the same mechanism the
  shell itself uses — builtins are given a small bridge process (`echo -n
  <output>`) so their in-memory string output can be piped into the next
  stage exactly like any external command's output would be.
- **Redirect operators are checked longest-first** (`2>>` before `2>` before
  `>>`/`1>>` before `>`/`1>`) since shorter operators are always substrings
  of the longer ones — checking in the wrong order would misparse commands.
- **The prompt is passed directly into `input("$ ")`** rather than printed
  separately, so `readline` can correctly track where the prompt ends and
  editable text begins (this is what keeps backspace and line redraws
  aligned with what's actually on screen).
- **Double-Tab detection is state-based, not time-based** — it checks
  whether the previous keypress was a "first Tab" on the exact same,
  unmodified text, with no reliance on how quickly the two presses happened.

## Known Limitations

- Redirect detection is a simple substring check, so a literal `>` inside a
  quoted argument (e.g. `echo "a > b"`) would be misinterpreted as a
  redirect.
- No support for `&&`, `||`, or `;` command chaining — only pipelines and
  single commands.
- No exit-code tracking between commands.
- The list of `PATH` executables used for tab completion is cached once at
  startup and won't reflect changes made to `PATH` mid-session.
- Detecting the `readline` backend (GNU readline vs. `libedit`) relies on the
  substring `"libedit"` appearing in `readline.__doc__` — a widely-used
  convention, but not a guaranteed API contract across every Python build.

## Acknowledgments

Built as part of the [CodeCrafters](https://codecrafters.io) "Build Your Own
Shell" challenge.