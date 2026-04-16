import pytest
import sys
import os

# Set django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')

if __name__ == "__main__":
    with open("test_out.txt", "w") as f:
        ret = pytest.main([sys.argv[1] if len(sys.argv) > 1 else '.', '-v', '--tb=short', '--color=no'], plugins=[])
    sys.exit(ret)
