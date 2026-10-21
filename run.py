"""Rebuild the analysis and chart from public source snapshots."""
import argparse
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--download', action='store_true', help='download/validate source snapshots first')
    parser.add_argument('--force-download', action='store_true', help='replace existing source snapshots')
    args = parser.parse_args()
    if args.download or args.force_download:
        command = [sys.executable, str(ROOT / 'download_data.py')]
        if args.force_download:
            command.append('--force')
        subprocess.run(command, cwd=ROOT, check=True)
    for script in ('analyze_cities.py', 'build_dashboard_data.py', 'plot_cities.py'):
        subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, check=True)
    print(f'Analysis tables: {ROOT / "analysis"}')
    print(f'Chart: {ROOT / "outputs" / "Australian_cities_climate_2026.png"}')
