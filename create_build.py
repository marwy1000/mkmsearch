import subprocess
import sys

menu_options = [
    "Optimized (onedir) with PyInstaller",
    "Onefile with PyInstaller"
]

def build(option):
    print(f"🔨 Building executable (Option {option})...")

    if option == 1:
        cmd = [
            "pyinstaller",
            "--onedir",
            "--noconfirm",
            "--disable-windowed-traceback",
            "--noupx",
            "--optimize", "1",
            "--log-level", "ERROR",
            "--name", "mkm",
            "--distpath", "./",
            "./mkm.py"
        ]
    elif option == 2:
        cmd = [
            "pyinstaller",
            "--onefile",
            "--noconfirm",
            "--disable-windowed-traceback",
            "--noupx",
            "--optimize", "1",
            "--name", "mkm",
            "--distpath", "./mkm",
            "./mkm.py"
        ]
    else:
        print(f"❌ Invalid option. Please provide a number 1-{len(menu_options)}.")
        sys.exit(1)

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("✅ Build successful.")
    else:
        print("❌ Build failed with exit code", result.returncode)
        sys.exit(result.returncode)

def get_option_from_user():
    print("Select build type:")
    counter = 1
    for line in menu_options:
        print(counter, line)
        counter += 1
    try:
        return int(input(f"Enter option [1-{len(menu_options)}]: ").strip())
    except ValueError:
        return 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            option = int(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid option. Please provide a number 1-{len(menu_options)}.")
            sys.exit(1)
    else:
        option = get_option_from_user()

    build(option)



