#!/usr/bin/env python3

"""
Let's analyze the problem step by step and try to understand what went wrong
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

def debug_solve():
    """Debug the smooth RSA challenge step by step"""
    
    # Read n and c from output
    with open('/home/runner/work/h/h/output.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    n_hex = lines[0].split(' = ')[1]
    c_hex = lines[1].split(' = ')[1]
    
    n = mpz(n_hex, 16)
    c = mpz(c_hex, 16)
    
    print(f"n = {n}")
    print(f"c = {c}")
    print(f"n bit length: {n.bit_length()}")
    print(f"c bit length: {c.bit_length()}")
    
    # Factor n
    print("\nFactoring n...")
    factor = pollard_p_minus_1(n, B=100000)
    
    if not factor:
        print("Could not factor - trying larger bound")
        factor = pollard_p_minus_1(n, B=1000000)
    
    if factor:
        p = factor
        q = n // p
        print(f"p = {p}")
        print(f"q = {q}")
        print(f"p bit length: {p.bit_length()}")
        print(f"q bit length: {q.bit_length()}")
        
        # Verify factorization
        assert p * q == n
        print("Factorization verified!")
        
        # Calculate phi(n)
        phi_n = (p - 1) * (q - 1)
        print(f"phi(n) = {phi_n}")
        
        # Check that gcd(3, phi_n) = 1
        g = gcd(3, phi_n)
        print(f"gcd(3, phi(n)) = {g}")
        
        if g != 1:
            print("ERROR: 3 and phi(n) are not coprime!")
            return None
        
        # Calculate private exponent d = 3^(-1) mod phi(n)
        d = invert(mpz(3), phi_n)
        print(f"d = {d}")
        
        # Decrypt: m = c^d mod n
        m = powmod(c, d, n)
        print(f"Decrypted message (as integer): {m}")
        
        # Verify: 3^m mod n should equal c
        verify = powmod(3, m, n)
        print(f"Verification: 3^m mod n = {verify}")
        print(f"Original c = {c}")
        print(f"Verification successful: {verify == c}")
        
        if verify != c:
            print("ERROR: Decryption verification failed!")
            return None
        
        # Now convert m to flag
        print(f"\nConverting message to flag...")
        flag_hex = hex(m)[2:]  # Remove 0x prefix
        if len(flag_hex) % 2:
            flag_hex = '0' + flag_hex
        
        print(f"Flag as hex: {flag_hex}")
        print(f"Flag hex length: {len(flag_hex)}")
        
        # Try to decode as ASCII
        try:
            flag_bytes = bytes.fromhex(flag_hex)
            print(f"Flag as bytes: {flag_bytes}")
            print(f"Flag bytes length: {len(flag_bytes)}")
            
            # Try to decode
            flag_str = flag_bytes.decode('ascii', errors='replace')
            print(f"Flag as string: {repr(flag_str)}")
            
            # Look for picoCTF pattern
            if 'picoCTF' in flag_str:
                start = flag_str.find('picoCTF')
                end = flag_str.find('}', start)
                if end > start:
                    clean_flag = flag_str[start:end+1]
                    return clean_flag
            
            # Look for any readable parts
            readable_chars = ''.join(c for c in flag_str if c.isprintable())
            print(f"Readable characters: {repr(readable_chars)}")
            
            return flag_str
            
        except Exception as e:
            print(f"Error decoding: {e}")
            return None
    
    return None

if __name__ == "__main__":
    flag = debug_solve()
    if flag:
        print(f"\nFINAL FLAG: {flag}")
    else:
        print("Could not recover flag")