# Introduction

The purpose of this app is to make your MKM purchase orders searchable locally using the command line. You can download the purchase orders yourself or automatically, which requires that you login through the app.

While this app uses web scraping I believe it still falls within the policy and rules for using the web page. I have added some delay between each commands as to not overload MKM or getting the connection broken. And in the long run it will make search better for everyone.

# Features

* Search on product name, set name, user name, date of purchase and if its foil. There are preset columns to select between to show more or less information.
* Generate reports and download them automatically

# Windows Installation

## Prerequisites

### Git

1. Download the Git installer from git-scm.com.
2. Run the downloaded .exe file and follow the setup wizard, leave default options unless specific preferences are required. Ensure the option to "Use Git from the command line and also from 3rd-party software" is selected.
3. Complete the installation and verify by opening a new terminal (Command Prompt or PowerShell) and running:

> git --version

### Python

1. Download the Python installer from python.org.
2. Run the downloaded .exe file. In the setup wizard: Check Add Python to PATH before clicking "Install Now." Follow the on-screen instructions.
3. Verify the installation by running in a terminal:

> python --version

## Get the source code

Either download it from here as a zip by pressing the green Code button and selecting Download ZIP: https://github.com/marwy1000/mkmsearch and unzip it, or:

> git clone https://github.com/marwy1000/mkmsearch.git

> cd mkmsearch

## Install Packages

1. Install required packages from the cloned directory

```powershell
pip install -r requirements.txt
```

# Usage

## Build an exe

From the cloned directory:

```powershell
python create_build.py 1
```

Then verify it and try it out:

```powershell
cd mkm
.\mkm.exe --help
```

## Available commands

> .\mkm.exe generate-reports

> .\mkm.exe download

> .\mkm.exe search -s "Universes" -p "Rad"

## Download reports manually

* First they need to be generated. Go here: https://www.cardmarket.com/en/Magic/Account/Statistics
* Only modify year and date under Purchased Orders, click Export (.csv)
* Reports can be downloaded manually here: https://www.cardmarket.com/en/Magic/Account/Downloads
* Place the reports in a sub directory, call it "csv_files"

# Upgrade from previous version
```
pip uninstall bs4
pip install --upgrade -r requirements.txt
```

# Release process
Run

```powershell
black .\src .\mkm.py
pylint .\src .\mkm.py
```
# Changes

## 0.3.0 / 2025-12-29
* Updated packages
* Added versioning
* Added support for 2FA
* Improved parsing based on naming change of sets
* Improved printout of search results
* Code refactoring

# TODO
-dc options 1-5 need to make sense, i.e. going from 1 to 5 should give incremental difference
add version option
running the generate-reports option without any options just logs you in
Test create_build.py, run black and pylint since its blocked currently