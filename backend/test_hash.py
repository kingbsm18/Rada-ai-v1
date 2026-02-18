"""
Test script to verify password hashing works correctly.
Run this from your backend directory:
  python test_hash.py
"""

import sys
sys.path.insert(0, '.')

from app.security import hash_password

def test_password_hashing():
    """Test that password hashing works with various inputs."""
    
    test_cases = [
        "admin123",
        "a" * 50,   # 50 character password
        "a" * 100,  # 100 character password (over 72 bytes)
        "émoji🎉" * 20,  # Multi-byte UTF-8 characters
    ]
    
    print("Testing password hashing...\n")
    
    for i, password in enumerate(test_cases, 1):
        try:
            byte_length = len(password.encode('utf-8'))
            print(f"Test {i}: Password length = {len(password)} chars, {byte_length} bytes")
            
            hashed = hash_password(password)
            print(f"  ✓ Success! Hash: {hashed[:50]}...")
            
        except Exception as e:
            print(f"  ✗ Failed: {type(e).__name__}: {e}")
        
        print()
    
    print("All tests completed!")

if __name__ == "__main__":
    test_password_hashing()