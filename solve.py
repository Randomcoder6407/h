#!/usr/bin/env python3

"""
Solution for NSA Backdoor Challenge

The challenge uses smooth primes p and q where p-1 and q-1 have only small prime factors.
This makes them vulnerable to Pollard's p-1 factorization algorithm.

We can factor n = p * q using the fact that the primes are smooth, then recover the flag.
"""

from gmpy2 import *
import binascii

def pollard_p_minus_1(n, B=1000000):
    """
    Pollard's p-1 factorization algorithm
    Works when p-1 has only small prime factors (smooth number)
    """
    a = mpz(2)
    
    # Compute a^(2*3*5*7*...*primes up to B) mod n
    for p in range(2, B):
        if is_prime(p):
            # Use enough powers to handle repeated prime factors
            k = 1
            while p**k < B:
                k += 1
            a = powmod(a, p**(k-1), n)
            
            # Check if we found a factor
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
    
    print(f"n = {n}")
    print(f"c = {c}")
    print(f"n bit length: {n.bit_length()}")
    
    print("\nAttempting to factor n using Pollard's p-1...")
    
    # Try to factor n using Pollard's p-1
    factor = pollard_p_minus_1(n, B=100000)
    
    if factor:
        p = factor
        q = n // p
        print(f"Found factors!")
        print(f"p = {p}")
        print(f"q = {q}")
        print(f"p * q = {p * q}")
        print(f"Verification: p * q == n: {p * q == n}")
        
        # Calculate phi(n) = (p-1)(q-1)
        phi_n = (p - 1) * (q - 1)
        
        # Calculate the discrete log: FLAG = log_3(c) mod phi_n
        # We need to find d such that 3^d ≡ c (mod n)
        # This is equivalent to finding the modular inverse of 3 mod phi_n
        
        try:
            # Find d such that 3*d ≡ 1 (mod phi_n)
            # Then FLAG ≡ c^d (mod n)
            d = invert(mpz(3), phi_n)
            flag_int = powmod(c, d, n)
            
            print(f"\nDecrypted flag as integer: {flag_int}")
            
            # Convert to hex then to bytes
            flag_hex = hex(flag_int)[2:]  # Remove '0x' prefix
            if len(flag_hex) % 2:
                flag_hex = '0' + flag_hex
            
            try:
                flag_bytes = bytes.fromhex(flag_hex)
                flag_str = flag_bytes.decode('ascii', errors='ignore')
                print(f"Flag as hex: {flag_hex}")
                print(f"Flag as string: {flag_str}")
                
                return flag_str
            except Exception as e:
                print(f"Error decoding flag: {e}")
                return None
                
        except Exception as e:
            print(f"Error computing discrete log: {e}")
            return None
    else:
        print("Could not factor n with Pollard's p-1")
        
        # Try a more exhaustive search
        print("Trying larger bound...")
        factor = pollard_p_minus_1(n, B=1000000)
        
        if factor:
            p = factor
            q = n // p
            print(f"Found factors with larger bound!")
            print(f"p = {p}")
            print(f"q = {q}")
            # Continue with decryption...
        else:
            print("Could not factor n")
            return None

if __name__ == "__main__":
    flag = solve_smooth_rsa()
    if flag:
        print(f"\nFINAL FLAG: {flag}")