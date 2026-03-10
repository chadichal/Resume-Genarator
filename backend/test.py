# test.py
import sys
print("Python path:", sys.path)

try:
    from backend.app import create_app
    print("✓ Successfully imported create_app")
    
    app = create_app()
    print("✓ Successfully created app")
    print("✓ Setup is correct!")
    
except Exception as e:
    print("✗ Error:", e)
    print("\nCurrent directory contents:")
    import os
    for item in os.listdir('.'):
        print(f"  - {item}")