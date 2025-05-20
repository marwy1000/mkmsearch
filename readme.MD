# Introduction

The purpose of this app is to make your MKM purchase orders searchable locally using the command line. These data for the purchase orders can be downloaded either manually or optionally by using this app.

While this app uses web scraping I believe it still falls within the policy and rules for using the web page. I have added some delay between each commands as to not overload MKM or getting the connection broken. And in the long run it will make search better for everyone.

It does not work with 2FA. The login information is saved in plain text in config.yaml.

# Features

* Search on product name, set name, user name, date of purchase and if its foil. There are preset columns to select between to show more or less information.
* Generate reports and download them automatically

# Download reports manually

* First they need to be generated. Go here: https://www.cardmarket.com/en/Magic/Account/Statistics
* Only modify year and date under Purchased Orders, click Export (.csv)
* Reports can be downloaded manually here: https://www.cardmarket.com/en/Magic/Account/Downloads
* Place the reports in a sub directory under the scripts, call it "csv_files"

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

# Usage

## Build an exe

From the cloned directory:

```powershell
python create_build.py
```

Then verify it and try it out:

```powershell
cd dist
.\mkm.exe --help
```

> .\mkm.exe generate-reports

> .\mkm.exe download

> .\mkm.exe search -s "Universes" -p "Rad"

# TODO

Generate reports should not generate reports for dates in the future, ex. -y 2025, should stop at may
How does handling of several reports for the same month work?
