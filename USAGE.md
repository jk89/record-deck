# Install required frameworks on your operating system
1. Install node + npm.
2. Install python3 and venv

# Install frameworks and enviroment
In the root directory... 

Execute bash commands:
1. npm run create-venv
2. 'source env/bin/activate' (on Mac or Linux) / '. env/Scripts/activate' (on GitBash Windows)
3. npm run install-venv-deps

Mac OS additional instructions:

1. Install homebrew
  - /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. Install wget 
  - brew install wget

Windows 10 additional instructions:

1. Install GitBash to run commands.
1. Download wget from https://eternallybored.org/misc/wget/1.21.3/64/wget.exe
3. Move wget.exe to your C:\Program Files\Git\mingw64\bin

## Datasets

# Installing double pendulum dataset

- Install the IBM double pendulum dataset
  - npm run download-idm-double-pendulum

# Tracking software

## State estimation graphing software for validation:
REQUIRES: Installing double pendulum dataset.
- npm run kalman-double-pendulum --dataset=14

## Perform duty simulation
- npm run simulate-bldc