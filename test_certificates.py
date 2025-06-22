#!/usr/bin/env python3
"""
Certificate Verification Script
Tests the ENAGEO CA and server certificate setup
"""

import os
import sys
from datetime import datetime
from OpenSSL import crypto

def check_file_exists(filepath, description):
    """Check if a file exists and print status"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} (NOT FOUND)")
        return False

def load_certificate(filepath):
    """Load a certificate from file"""
    try:
        with open(filepath, 'rb') as f:
            cert_data = f.read()
        return crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
    except Exception as e:
        print(f"Error loading certificate {filepath}: {e}")
        return None

def load_private_key(filepath, password=None):
    """Load a private key from file"""
    try:
        with open(filepath, 'rb') as f:
            key_data = f.read()
        if password:
            return crypto.load_privatekey(crypto.FILETYPE_PEM, key_data, password.encode())
        else:
            return crypto.load_privatekey(crypto.FILETYPE_PEM, key_data)
    except Exception as e:
        print(f"Error loading private key {filepath}: {e}")
        return None

def print_certificate_info(cert, title):
    """Print certificate information"""
    print(f"\n{title}:")
    print("-" * 50)
    
    subject = cert.get_subject()
    issuer = cert.get_issuer()
    
    print(f"Subject: {subject.CN}")
    print(f"Organization: {subject.O}")
    print(f"Organizational Unit: {subject.OU}")
    print(f"Country: {subject.C}")
    print(f"State: {subject.ST}")
    print(f"Locality: {subject.L}")
    
    print(f"\nIssuer: {issuer.CN}")
    print(f"Issuer Organization: {issuer.O}")
    
    not_before = datetime.strptime(cert.get_notBefore().decode(), '%Y%m%d%H%M%SZ')
    not_after = datetime.strptime(cert.get_notAfter().decode(), '%Y%m%d%H%M%SZ')
    
    print(f"\nValid from: {not_before}")
    print(f"Valid until: {not_after}")
    
    # Check if certificate is currently valid
    now = datetime.now()
    if not_before <= now <= not_after:
        print("✓ Certificate is currently valid")
    else:
        print("✗ Certificate is not currently valid")
    
    # Check key usage
    try:
        key_usage = cert.get_extension_by_nid(crypto.NID_KEY_USAGE)
        print(f"Key Usage: {key_usage}")
    except:
        pass
    
    # Check extended key usage
    try:
        ext_key_usage = cert.get_extension_by_nid(crypto.NID_EXT_KEY_USAGE)
        print(f"Extended Key Usage: {ext_key_usage}")
    except:
        pass

def verify_certificate_chain(server_cert, ca_cert):
    """Verify that server certificate is signed by CA"""
    print("\nCertificate Chain Verification:")
    print("-" * 50)
    
    try:
        # Create certificate store
        store = crypto.X509Store()
        store.add_cert(ca_cert)
        
        # Create verification context
        store_ctx = crypto.X509StoreContext(store, server_cert)
        
        # Verify the certificate
        store_ctx.verify_certificate()
        print("✓ Server certificate is properly signed by the CA")
        return True
    except Exception as e:
        print(f"✗ Certificate chain verification failed: {e}")
        return False

def verify_key_matching(cert, key, description):
    """Verify that certificate matches private key by comparing public keys"""
    try:
        # Get the public key from the certificate
        cert_pubkey = cert.get_pubkey()
        
        # Get the public key from the private key
        key_pubkey = key
        
        # Compare the public keys using a simple method
        # Convert both to PEM format and compare
        cert_pubkey_pem = crypto.dump_publickey(crypto.FILETYPE_PEM, cert_pubkey)
        key_pubkey_pem = crypto.dump_publickey(crypto.FILETYPE_PEM, key_pubkey)
        
        if cert_pubkey_pem == key_pubkey_pem:
            print(f"✓ {description} matches private key")
            return True
        else:
            print(f"✗ {description} does not match private key")
            return False
    except Exception as e:
        print(f"✗ {description} key matching test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("ENAGEO Certificate Verification")
    print("=" * 60)
    
    # Define file paths
    ca_cert_path = "CA/certs/ca.cert.pem"
    ca_key_path = "CA/private/ca.key.pem"
    server_cert_path = "backend/certs/server.cert.pem"
    server_key_path = "backend/certs/server.key.pem"
    backend_ca_cert_path = "backend/certs/ca.cert.pem"
    
    # Check if files exist
    print("Checking certificate files:")
    files_exist = True
    files_exist &= check_file_exists(ca_cert_path, "CA Certificate")
    files_exist &= check_file_exists(ca_key_path, "CA Private Key")
    files_exist &= check_file_exists(server_cert_path, "Server Certificate")
    files_exist &= check_file_exists(server_key_path, "Server Private Key")
    files_exist &= check_file_exists(backend_ca_cert_path, "Backend CA Certificate")
    
    if not files_exist:
        print("\nSome certificate files are missing!")
        print("Please run the certificate setup scripts:")
        print("1. create_ca.bat")
        print("2. create_server_cert.bat")
        return False
    
    # Load certificates
    print("\nLoading certificates...")
    ca_cert = load_certificate(ca_cert_path)
    server_cert = load_certificate(server_cert_path)
    
    if not ca_cert or not server_cert:
        print("Failed to load certificates")
        return False
    
    # Load private keys
    print("Loading private keys...")
    ca_key = load_private_key(ca_key_path, "password")
    server_key = load_private_key(server_key_path)
    
    if not ca_key or not server_key:
        print("Failed to load private keys")
        return False
    
    # Print certificate information
    print_certificate_info(ca_cert, "CA Certificate")
    print_certificate_info(server_cert, "Server Certificate")
    
    # Verify certificate chain
    chain_valid = verify_certificate_chain(server_cert, ca_cert)
    
    # Test key matching
    print("\nKey Matching Test:")
    print("-" * 50)
    
    server_key_match = verify_key_matching(server_cert, server_key, "Server certificate")
    ca_key_match = verify_key_matching(ca_cert, ca_key, "CA certificate")
    
    # Final result
    print("\n" + "=" * 60)
    if chain_valid and server_key_match and ca_key_match:
        print("✓ CERTIFICATE SETUP IS VALID")
        print("The backend server can now use these certificates for SSL/TLS")
    else:
        print("✗ CERTIFICATE SETUP HAS ISSUES")
        print("Please check the errors above and fix them")
    
    return chain_valid and server_key_match and ca_key_match

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nVerification cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1) 