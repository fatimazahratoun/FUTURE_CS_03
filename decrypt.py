#!/usr/bin/env python3
"""
Standalone Decryption Tool for Secure File Sharing System
Usage: python decrypt.py encrypted_file.enc key_file.key
"""

import sys
import os
import base64
from Crypto.Cipher import AES

def print_banner():
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║         🔐 SECURE FILE SHARING - DECRYPTION TOOL         ║
    ║          AES-256-GCM • Offline Decryption                ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)

def load_key(key_file):
    """Load encryption key from .key file"""
    try:
        with open(key_file, 'r') as f:
            # Find the key in the file (might be in a text file with instructions)
            content = f.read()
            lines = content.strip().split('\n')
            
            # Look for base64 key (typically the longest base64 string)
            key_base64 = None
            for line in lines:
                line = line.strip()
                if 'Key (base64):' in line:
                    key_base64 = line.split('Key (base64):')[1].strip()
                    break
                elif len(line) > 40 and '=' in line:  # Likely base64
                    key_base64 = line
                    break
            
            if not key_base64:
                # Try to find any base64 string
                for line in lines:
                    if len(line) > 20 and all(c.isalnum() or c in '+/=' for c in line):
                        key_base64 = line
                        break
            
            if not key_base64:
                print("❌ Could not find encryption key in the key file.")
                print("   Make sure you're using the correct .key file from the system.")
                return None
            
            return base64.b64decode(key_base64)
            
    except FileNotFoundError:
        print(f"❌ Key file not found: {key_file}")
        return None
    except Exception as e:
        print(f"❌ Error loading key: {e}")
        return None

def decrypt_file(encrypted_file, key):
    """Decrypt an .enc file"""
    try:
        with open(encrypted_file, 'rb') as f:
            encrypted_data = f.read()
        
        if len(encrypted_data) < 32:
            print(f"❌ File too small ({len(encrypted_data)} bytes).")
            print("   This doesn't appear to be a valid AES-GCM encrypted file.")
            return None
        
        # Extract components
        nonce = encrypted_data[:16]
        tag = encrypted_data[16:32]
        ciphertext = encrypted_data[32:]
        
        print(f"   File size: {len(encrypted_data)} bytes")
        print(f"   Nonce: {nonce.hex()[:16]}...")
        print(f"   Tag: {tag.hex()[:16]}...")
        print(f"   Ciphertext: {len(ciphertext)} bytes")
        
        # Create cipher and decrypt
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        
        print(f"   ✅ Decryption successful!")
        print(f"   ✅ Integrity verified (GCM tag validated)")
        
        return plaintext
        
    except FileNotFoundError:
        print(f"❌ Encrypted file not found: {encrypted_file}")
        return None
    except ValueError as e:
        print(f"❌ Decryption failed: {e}")
        print("   Possible reasons:")
        print("   - Wrong encryption key")
        print("   - File corrupted")
        print("   - Not an AES-GCM encrypted file")
        return None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return None

def save_decrypted_file(decrypted_data, original_filename):
    """Save decrypted data to file"""
    # Remove .enc extension if present
    if original_filename.endswith('.enc'):
        output_filename = original_filename[:-4]
    else:
        output_filename = original_filename + '_decrypted'
    
    # Avoid overwriting
    counter = 1
    final_filename = output_filename
    while os.path.exists(final_filename):
        name, ext = os.path.splitext(output_filename)
        if not ext:
            ext = '.decrypted'
        final_filename = f"{name}_{counter}{ext}"
        counter += 1
    
    with open(final_filename, 'wb') as f:
        f.write(decrypted_data)
    
    return final_filename

def main():
    print_banner()
    
    if len(sys.argv) != 3:
        print("📖 USAGE:")
        print("  python decrypt.py <encrypted_file.enc> <key_file.key>")
        print()
        print("📝 EXAMPLES:")
        print("  python decrypt.py document.pdf.enc document.key")
        print("  python decrypt.py secret.txt.enc 123abc_key.txt")
        print()
        print("ℹ️  You can download encrypted files (.enc) and key files")
        print("   from the Secure File Sharing web interface.")
        print()
        
        # Interactive mode
        if len(sys.argv) == 1:
            enc_file = input("Enter path to encrypted file (.enc): ").strip()
            key_file = input("Enter path to key file (.key or .txt): ").strip()
            
            if not enc_file or not key_file:
                return
        else:
            return
    
    else:
        enc_file = sys.argv[1]
        key_file = sys.argv[2]
    
    print(f"\n🔍 Starting decryption process...")
    print(f"   Encrypted file: {enc_file}")
    print(f"   Key file: {key_file}")
    
    # Check if files exist
    if not os.path.exists(enc_file):
        print(f"❌ Encrypted file not found: {enc_file}")
        return
    
    if not os.path.exists(key_file):
        print(f"❌ Key file not found: {key_file}")
        return
    
    # Load key
    print(f"\n🗝️  Loading encryption key...")
    key = load_key(key_file)
    if key is None:
        return
    
    print(f"   Key loaded: {len(key)} bytes")
    print(f"   Key (hex): {key.hex()[:32]}...")
    
    # Decrypt file
    print(f"\n🔓 Decrypting file...")
    decrypted_data = decrypt_file(enc_file, key)
    
    if decrypted_data is None:
        return
    
    # Save decrypted file
    print(f"\n💾 Saving decrypted file...")
    original_name = os.path.basename(enc_file)
    output_file = save_decrypted_file(decrypted_data, original_name)
    
    # Show file info
    file_size = len(decrypted_data)
    if file_size < 1024:
        size_str = f"{file_size} bytes"
    elif file_size < 1048576:
        size_str = f"{file_size/1024:.2f} KB"
    else:
        size_str = f"{file_size/1048576:.2f} MB"
    
    print(f"\n🎉 DECRYPTION COMPLETE!")
    print(f"   Original: {enc_file}")
    print(f"   Decrypted: {output_file}")
    print(f"   Size: {size_str}")
    
    # Try to detect file type
    if file_size < 1000:  # Small text file
        try:
            text_preview = decrypted_data[:100].decode('utf-8', errors='ignore')
            print(f"\n📄 Preview (first 100 chars):")
            print(f"   {text_preview}...")
        except:
            pass
    
    print(f"\n✅ File successfully decrypted and saved as: {output_file}")
    print(f"\n🔒 Security reminder:")
    print("   - Keep your decrypted files secure")
    print("   - Delete the key file after use")
    print("   - Consider encrypting sensitive files again for storage")

if __name__ == "__main__":
    main()