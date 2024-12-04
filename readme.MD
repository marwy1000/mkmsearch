# Introduction
The purpose of this app is to make your MKM purchase orders searchable locally using the command line. It offers one command for generating/requesting the reports in MKM, one for downloading the reports and the main function, search. The app is a bit slow because I am using a slow component that I thought seemed fun to try out. 

While this app uses webscraping I believe it still falls within the policy and rules for using the web page. I have added some delay between each commands as to not overload MKM or getting the connection broken. And in the long run it will make search better for everyone. 

It does not work with 2FA. The login information is saved in plain text in config.yaml. 

# Windows Installation
## Git
1. Download the Git installer from git-scm.com.
2. Run the downloaded .exe file and follow the setup wizard, leave default options unless specific preferences are required. Ensure the option to "Use Git from the command line and also from 3rd-party software" is selected.
3. Complete the installation and verify by opening a new terminal (Command Prompt or PowerShell) and running:

> git --version

## Python
1. Download the Python installer from python.org.
2. Run the downloaded .exe file. In the setup wizard: Check Add Python to PATH before clicking "Install Now." Follow the on-screen instructions.
3. Verify the installation by running in a terminal:

> python --version

## Get the source code
Either download it from here as a zip by pressing the green Code button and selecting Download ZIP: https://github.com/marwy1000/mkmsearch and unzip it, or:
> git clone https://github.com/marwy1000/mkmsearch.git

> cd mkmsearch

# Example usage
> python .\mkm.py generate-reports

> python .\mkm.py download

> python .\mkm.py search -s "Universes" -p "Rad"