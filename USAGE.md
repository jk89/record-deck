# Install required frameworks
1. Install node + npm.
2. Install python3 and venv

# Install
In the root directory... 

Execute bash commands:
1. npm run create-venv
2. source env/bin/activate
3. npm run install-venv-deps

Mac OS additional instructions:

1. Install homebrew
  - /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. Install wget 
  - brew install wget
# Installing datasets

- Install the IBM double pendulum dataset
  - ./datasets/download-double-pendulum.sh

# Tracking software

State estimation graphing software for validation: 
- ./scripts/perform-euler-pendulum.sh