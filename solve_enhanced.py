#!/usr/bin/env python3

"""
Solution for NSA Backdoor Challenge - Enhanced Version

The challenge uses smooth primes p and q where p-1 and q-1 have only small prime factors.
This makes them vulnerable to Pollard's p-1 factorization algorithm.
"""

from gmpy2 import *
import binascii

def pollard_p_minus_1(n, B=1000000):
    """Pollard's p-1 factorization algorithm"""
    a = mpz(2)
    
    for p in range(2, B):
        if is_prime(p):
            k = 1
            while p**k < B:
                k += 1
            a = powmod(a, p**(k-1), n)
            
            g = gcd(a - 1, n)
            if 1 < g < n:
                return g
    
    return None

def solve_smooth_rsa():
    """Solve the smooth RSA challenge"""
    
    # Read n and c from output
    with open('/home/runner/work/h/h/output.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    n_hex = lines[0].split(' = ')[1]
    c_hex = lines[1].split(' = ')[1]
    
    n = mpz(n_hex, 16)
    c = mpz(c_hex, 16)
    
    print(f"n bit length: {n.bit_length()}")
    
    print("\nAttempting to factor n using Pollard's p-1...")
    
    factor = pollard_p_minus_1(n, B=100000)
    
    if factor:
        p = factor
        q = n // p
        print(f"Found factors!")
        print(f"Verification: p * q == n: {p * q == n}")
        
        # Calculate phi(n) = (p-1)(q-1)
        phi_n = (p - 1) * (q - 1)
        
        # The encryption was c = 3^FLAG mod n
        # So we need FLAG = log_3(c) mod phi_n
        # Which means we need d such that 3^d ≡ 1 (mod phi_n)
        # Then FLAG ≡ c^d (mod n)
        
        try:
            # Find the multiplicative inverse of 3 modulo phi_n
            d = invert(mpz(3), phi_n)
            flag_int = powmod(c, d, n)
            
            print(f"\nDecrypted flag as integer: {flag_int}")
            
            # Convert to hex
            flag_hex = hex(flag_int)[2:]
            if len(flag_hex) % 2:
                flag_hex = '0' + flag_hex
            
            print(f"Flag as hex: {flag_hex}")
            
            # Try different interpretations
            print("\nTrying different interpretations:")
            
            # Method 1: Direct hex to bytes
            try:
                flag_bytes = bytes.fromhex(flag_hex)
                flag_str = flag_bytes.decode('ascii', errors='ignore')
                print(f"Method 1 - Direct decode: {repr(flag_str)}")
            except:
                pass
            
            # Method 2: Remove leading zeros and try again
            flag_hex_trimmed = flag_hex.lstrip('0')
            if len(flag_hex_trimmed) % 2:
                flag_hex_trimmed = '0' + flag_hex_trimmed
            
            try:
                flag_bytes = bytes.fromhex(flag_hex_trimmed)
                flag_str = flag_bytes.decode('ascii', errors='ignore')
                print(f"Method 2 - Trimmed zeros: {repr(flag_str)}")
            except:
                pass
            
            # Method 3: Look for picoCTF pattern
            # Find the rightmost part that might contain readable text
            for i in range(0, len(flag_hex), 2):
                try:
                    substr = flag_hex[i:]
                    if len(substr) % 2:
                        substr = '0' + substr
                    flag_bytes = bytes.fromhex(substr)
                    flag_str = flag_bytes.decode('ascii', errors='ignore')
                    if 'picoCTF' in flag_str or 'pico' in flag_str.lower():
                        print(f"Method 3 - Found picoCTF pattern: {repr(flag_str)}")
                        return flag_str
                except:
                    continue
            
            # Method 4: Try interpreting as little endian
            try:
                # Convert to bytes and reverse
                flag_bytes = bytes.fromhex(flag_hex)
                flag_bytes_rev = flag_bytes[::-1]
                flag_str = flag_bytes_rev.decode('ascii', errors='ignore')
                print(f"Method 4 - Little endian: {repr(flag_str)}")
                if 'picoCTF' in flag_str:
                    return flag_str
            except:
                pass
            
            # Method 5: Try different starting points
            for start in [0, 2, 4, 6, 8]:
                try:
                    substr = flag_hex[start:]
                    if len(substr) % 2:
                        substr = '0' + substr
                    flag_bytes = bytes.fromhex(substr)
                    flag_str = flag_bytes.decode('ascii', errors='replace')
                    if 'picoCTF{' in flag_str:
                        print(f"Method 5 - Found flag at offset {start}: {repr(flag_str)}")
                        # Extract just the flag part
                        start_idx = flag_str.find('picoCTF{')
                        if start_idx >= 0:
                            end_idx = flag_str.find('}', start_idx)
                            if end_idx >= 0:
                                flag_clean = flag_str[start_idx:end_idx+1]
                                return flag_clean
                except:
                    continue
            
            # Return the best guess
            try:
                flag_bytes = bytes.fromhex(flag_hex_trimmed)
                flag_str = flag_bytes.decode('ascii', errors='ignore')
                return flag_str
            except:
                return None
                
        except Exception as e:
            print(f"Error computing discrete log: {e}")
            return None
    else:
        print("Could not factor n")
        return None

if __name__ == "__main__":
    flag = solve_smooth_rsa()
    if flag:
        print(f"\nFINAL FLAG: {flag}")
    else:
        print("Could not recover flag")