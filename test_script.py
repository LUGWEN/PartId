import os
import sys

print("Testing output")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print("Listing files:")
for file in os.listdir("."):
    print(f"  {file}") 