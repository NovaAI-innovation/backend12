#!/usr/bin/env python3
"""
Password Hash Generator
Generates bcrypt password hashes for CMS authentication.
Run this script to create the ADMIN_PASSWORD_HASH for your .env file.
"""
import bcrypt
import getpass


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: Plain text password
    
    Returns:
        Hashed password string
    """
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds is secure and performant
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def main():
    """Main function to generate password hash."""
    print("=" * 60)
    print("CMS Admin Password Hash Generator")
    print("=" * 60)
    print()
    print("This will generate a bcrypt hash for your admin password.")
    print("Copy the output to your .env file as ADMIN_PASSWORD_HASH")
    print()
    
    # Get password securely (won't echo to screen)
    password = getpass.getpass("Enter admin password: ")
    
    if not password:
        print("\n❌ Error: Password cannot be empty")
        return
    
    # Confirm password
    password_confirm = getpass.getpass("Confirm password: ")
    
    if password != password_confirm:
        print("\n❌ Error: Passwords do not match")
        return
    
    print("\n⏳ Generating hash (this may take a moment)...")
    
    try:
        hashed = hash_password(password)
        
        print("\n✅ Success! Copy this line to your .env file:\n")
        print(f"ADMIN_PASSWORD_HASH={hashed}")
        print()
        print("⚠️  Keep this hash secret and never commit it to version control!")
        print()
        
    except Exception as e:
        print(f"\n❌ Error generating hash: {str(e)}")


if __name__ == "__main__":
    main()

