import subprocess
import sys

def build():
    print("🔨 Building executable...")

    cmd = [
        "pyinstaller",
        "--onefile",
        "--clean",
        "--noconfirm",
        "--disable-windowed-traceback",
        "--noupx",
        "--optimize", "2",
        "--name", "mkm",
        "./mkm.py"
    ]

    result = subprocess.run(cmd)

    if result.returncode == 0:
        print("✅ Build successful.")
    else:
        print("❌ Build failed with exit code", result.returncode)
        sys.exit(result.returncode)

if __name__ == "__main__":
    build()
