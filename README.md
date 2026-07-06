# GekokuAI
Status:
v0.4

a self-written local LLM Launcher directly from your CLI alone.
currently supports all linux distro that uses APT, pacman, and DNF as its package manager
## Installation

- `git clone https://github.com/isauinu/GekokuAI/`
- `cd GekokuAI`
- `chmod +x setup.sh`
- `./setup.sh`

Additionally depending on your shell export the following into your shell environment, example:

`echo 'export PATH="$HOME/.gekokuai/bin:$PATH"' >> ~/.bashrc`

and then refresh your shell environment, example

`source ~/.bashrc`

## Commands
- gekoku serve [MODEL]
- gekoku pull [REPO]
- gekoku status
- gekoku info
- gekoku remove [MODEL]
- gekoku doctor
- gekoku list
- gekoku stop
- gekoku load
- gekoku unload
- gekoku logs   

## License
This project is licensed under the "MIT License". See the `license` file for further details