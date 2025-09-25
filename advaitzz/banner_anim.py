import sys
import time

ASCII_BANNER = r"""
    ___  ____  __      __    _ _______ ___ _______ 
   / _ \/ __ \/ /     / /   (_) ___/ // / ___/ / 
  / , _/ /_/ / /__   / /__ / / /__/ _  / /__/ /  
 /_/|_|\____/____/  /____//_/\___/_//_/\___/_/   
                                                  
               ADVAITZZ - Dork & Recon Tool
"""

def print_banner():
    print(ASCII_BANNER)

def spinner(duration=1.5, message="Loading"):
    for _ in range(int(duration/0.1)):
        for sym in "|/-\\":
            sys.stdout.write(f"\r{message}... {sym}")
            sys.stdout.flush()
            time.sleep(0.1)
    sys.stdout.write("\r")
