# Install required frameworks on your operating system:
1. Install node (> v16.16.0) + npm (8.17.0).
2. Install python3 and venv
3. Install Arduino and Teensy dependencies
   1. Download latest Arduino from https://www.arduino.cc/en/software which Teensy supports currently arduino-1.8.19
   2. Extract to {home}/bin/
   3. Follow instructions to configure Arduino IDE for Teensy https://www.pjrc.com/teensy/td_download.html

# OS specific instructions

## Mac OS instructions:

1. Install homebrew
  - `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. Install wget 
  - `brew install wget`

## Windows 10 instructions:

1. Install Windows linux sub-system WSL use this to create python virtual environments (does not work for spark)

TODO better instructions!

## Linux (tested on Ubuntu)

The PS4-controller library has only been tested on Ubuntu and requires joystick:
1. `sudo apt-get install joystick`

If latex is needed e.g. for state-model sympy lib:
1. `sudo apt install texlive-latex-extra dvipng`

Python deps
1. `sudo apt-get install libcairo2-dev libjpeg-dev libgif-dev`
2. `sudo apt install libgirepository1.0-dev`

# Cross platform instructions:

## Install/activate frameworks and environment:
In the root directory... 

## Execute Bash(or GitBash) commands:
1. `npm install`
2. `npm run install:venv`
3. `source env/bin/activate` (on Mac or Linux) / `. env/Scripts/activate` (on GitBash Windows)
4. `npm run install:venv-deps`

## For each Bash(or GitBash) session instance you will need to re-activate your virtual environment.
- `source env/bin/activate` (on Mac or Linux)
- `. env/Scripts/activate` (on GitBash Windows)

## Spark Ubuntu:
 - Install spark, start a worker and a master.
 - where you want to run pyspark
  - `sudo apt-get install default-jdk -y`
  - `sudo apt-get install gcc libpq-dev -y`
  - `sudo apt-get install python3-dev python3-pip python3-venv python3-wheel -y`
  - pip3 install wheel
  - pip3 install pandas
  - pip3 install PyArrow
  - pip3 install pyspark

## Spark Windows:

Todo
export PATH="/c/Program Files/Java/jdk-18.0.1.1/bin:$PATH"
https://sparkbyexamples.com/pyspark/how-to-install-and-run-pyspark-on-windows/

## Spark Mac

Todo
