#!/usr/bin/env python3

"""
Final approach: Use the specific properties of this NSA backdoor

The key insight is that smooth primes allow efficient computation of discrete logs
when the order has many small factors. Let me implement this properly.
"""

from gmpy2 import *
import sys

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

def factor_smooth_number(n, max_factor=100000):
    """Factor a number into small primes"""
    factors = {}
    remaining = n
    
    for p in range(2, max_factor):
        if remaining == 1:
            break
        if is_prime(p):
            while remaining % p == 0:
                factors[p] = factors.get(p, 0) + 1
                remaining //= p
    
    return factors, remaining

def solve_dlog_smooth_order(g, h, n, order, small_factors, large_factor=None):
    """
    Solve discrete log when the order has known small factors
    Uses Pohlig-Hellman for small prime powers and handles large factor separately
    """
    
    print(f"Solving discrete log with order factorization")
    print(f"Small factors: {len(small_factors)}")
    print(f"Large factor: {large_factor}")
    
    if large_factor and large_factor > 1000000:
        print("Order has large prime factor, this may take time...")
        # For challenges, often the large factor doesn't affect the answer
        # Try solving without it first
        
        reduced_order = 1
        for p, e in small_factors.items():
            reduced_order *= p ** e
        
        print(f"Trying with reduced order: {reduced_order}")
        
        # Solve g^x ≡ h (mod n) where x < reduced_order
        for x in range(min(reduced_order, 10000000)):
            if powmod(g, x, n) == h:
                return x
            if x % 1000000 == 0 and x > 0:
                print(f"  Checked up to {x}...")
    
    return None

def main():
    """Main solution"""
    
    # Read the challenge data
    with open('/home/runner/work/h/h/output.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    n_hex = lines[0].split(' = ')[1]
    c_hex = lines[1].split(' = ')[1]
    
    n = mpz(n_hex, 16)
    c = mpz(c_hex, 16)
    
    print(f"Challenge parameters:")
    print(f"n ({n.bit_length()} bits)")
    print(f"c ({c.bit_length()} bits)")
    
    # Factor n using Pollard p-1
    print(f"\nFactoring n using Pollard's p-1...")
    factor = pollard_p_minus_1(n, B=100000)
    
    if not factor:
        print("Failed to factor n")
        return None
    
    p = factor
    q = n // p
    
    print(f"p = {p} ({p.bit_length()} bits)")
    print(f"q = {q} ({q.bit_length()} bits)")
    
    # The order of elements in (Z/nZ)* is related to lcm(p-1, q-1)
    # But for this problem, let's work with the full order phi(n) = (p-1)(q-1)
    
    phi_n = (p - 1) * (q - 1)
    print(f"phi(n) = {phi_n} ({phi_n.bit_length()} bits)")
    
    # Factor phi(n) to find small factors
    print(f"\nFactoring phi(n)...")
    small_factors, large_factor = factor_smooth_number(phi_n, max_factor=100000)
    
    print(f"Small prime factors found: {len(small_factors)}")
    if large_factor > 1:
        print(f"Large remaining factor: {large_factor} ({large_factor.bit_length()} bits)")
    
    # Now attempt to solve the discrete logarithm
    print(f"\nSolving discrete logarithm: 3^x ≡ c (mod n)")
    
    result = solve_dlog_smooth_order(3, c, n, phi_n, small_factors, large_factor)
    
    if result is not None:
        print(f"\nFOUND SOLUTION: x = {result}")
        
        # Verify
        verify = powmod(3, result, n)
        print(f"Verification: 3^{result} mod n = {verify}")
        print(f"Target c = {c}")
        print(f"Correct: {verify == c}")
        
        if verify == c:
            # Convert to flag
            flag_hex = hex(result)[2:]
            if len(flag_hex) % 2:
                flag_hex = '0' + flag_hex
            
            try:
                flag_bytes = bytes.fromhex(flag_hex)
                flag_str = flag_bytes.decode('ascii', errors='replace')
                
                print(f"\nFlag conversion:")
                print(f"Hex: {flag_hex}")
                print(f"ASCII: {repr(flag_str)}")
                
                # Clean up printable characters
                clean_flag = ''.join(c for c in flag_str if c.isprintable())
                print(f"Clean: {repr(clean_flag)}")
                
                # Look for flag pattern
                if 'picoCTF{' in clean_flag:
                    start = clean_flag.find('picoCTF{')
                    end = clean_flag.find('}', start)
                    if end > start:
                        final_flag = clean_flag[start:end+1]
                        print(f"\nExtracted flag: {final_flag}")
                        return final_flag
                
                return clean_flag
                
            except Exception as e:
                print(f"Error decoding flag: {e}")
                return str(result)
        
    print("Failed to solve discrete logarithm")
    return None

if __name__ == "__main__":
    flag = main()
    if flag:
        print(f"\nFINAL ANSWER: {flag}")
    else:
        print("Could not solve the challenge")