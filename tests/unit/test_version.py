import sys
import os

# Add src to the Python path to allow importing 'shared' directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from shared.version import __version__

def test_global_version():
    """
    Test that the global version identifier is strictly initialized to '1.00'.
    """
    assert __version__ == "1.00", f"Expected version '1.00', but got '{__version__}'"
