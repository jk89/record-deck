# Install required frameworks on your operating system
1. Install node + npm.
2. Install python3 and venv

# OS specific instructions

## Mac OS instructions:

1. Install homebrew
  - /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. Install wget 
  - brew install wget

## Windows 10 instructions:

1. Install GitBash to run commands.
1. Download wget from https://eternallybored.org/misc/wget/1.21.3/64/wget.exe
3. Move wget.exe to your C:\Program Files\Git\mingw64\bin

## Linux (tested on Ubuntu)

The PS4 library has only been tested on Ubuntu and requires joystick:
1. sudo apt-get install joystick

# Install frameworks and enviroment
In the root directory... 

Execute Bash(or GitBash) commands:
1. npm run create-venv
2. 'source env/bin/activate' (on Mac or Linux) / '. env/Scripts/activate' (on GitBash Windows)
3. npm run install-venv-deps

