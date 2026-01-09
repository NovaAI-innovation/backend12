#!/usr/bin/env python3
"""
Password Verification Utility
Tests if a password matches the stored hash, or generates a new hash.
"""
import bcrypt
import sys
import os
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.auth import verify_password, hash_password


def verify_password_from_hash(password: str, hash_value: str) -> bool:
    """Verify a password against a hash."""
    try:
        return verify_password(password, hash_value)
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False


def main():
    """Main function."""
    print("=" * 60)
    print("Password Hash Utility")
    print("=" * 60)
    print()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python verify_password.py <hash>           - Test password against hash")
        print("  python verify_password.py --generate       - Generate new hash")
        print("  python verify_password.py --test <hash>    - Interactive test mode")
        print()
        print("Examples:")
        print("  python verify_password.py '$2b$12$...'")
        print("  python verify_password.py --generate")
        print("  python verify_password.py --test '$2b$12$...'")
        return
    
    if sys.argv[1] == "--generate":
        # Generate new hash
        import getpass
        password = getpass.getpass("Enter new password: ")
        if not password:
            print("❌ Error: Password cannot be empty")
            return
        
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("❌ Error: Passwords do not match")
            return
        
        hashed = hash_password(password)
        print("\n✅ Generated hash:")
        print(f"ADMIN_PASSWORD_HASH={hashed}")
        print("\nCopy this to your .env file")
        
    elif sys.argv[1] == "--test" and len(sys.argv) >= 3:
        # Interactive test mode
        hash_value = sys.argv[2]
        import getpass
        
        print(f"Hash: {hash_value[:20]}...")
        print()
        
        while True:
            password = getpass.getpass("Enter password to test (or 'quit' to exit): ")
            if password.lower() == 'quit':
                break
            
            if verify_password_from_hash(password, hash_value):
                print("✅ Password matches!")
                break
            else:
                print("❌ Password does not match. Try again.")
                print()
    
    elif len(sys.argv) >= 2:
        # Test password against hash
        hash_value = sys.argv[1]
        import getpass
        
        print(f"Testing against hash: {hash_value[:30]}...")
        print()
        password = getpass.getpass("Enter password to test: ")
        
        if verify_password_from_hash(password, hash_value):
            print("\n✅ Password matches!")
        else:
            print("\n❌ Password does not match.")
            print("\nIf you've forgotten the password, you can:")
            print("1. Generate a new hash: python verify_password.py --generate")
            print("2. Update ADMIN_PASSWORD_HASH in your .env file")


if __name__ == "__main__":
    main()
