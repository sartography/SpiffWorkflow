import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
try:
    import SpiffSignal
finally:
    sys.path.pop(0)
