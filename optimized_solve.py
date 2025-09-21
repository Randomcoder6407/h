#!/usr/bin/env python3

"""
Optimized solution for NSA Backdoor Challenge

The key insight is that we have smooth primes p and q, making p-1 and q-1 
have many small factors. We can use this to solve the discrete log efficiently.
"""

from gmpy2 import *
import time

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

def get_small_factors(n, limit=100000):
    """Get all prime factors of n up to limit"""
    factors = {}
    for p in range(2, min(limit, int(n**0.5) + 1)):
        if n % p == 0 and is_prime(p):
            count = 0
            while n % p == 0:
                n //= p
                count += 1
            factors[p] = count
        if n == 1:
            break
    return factors, n

def solve_challenge_optimized():
    """Optimized solution"""
    
    # Read n and c from output
    with open('/home/runner/work/h/h/output.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    n_hex = lines[0].split(' = ')[1]
    c_hex = lines[1].split(' = ')[1]
    
    n = mpz(n_hex, 16)
    c = mpz(c_hex, 16)
    
    print(f"n bit length: {n.bit_length()}")
    
    # Factor n
    print("Factoring n...")
    factor = pollard_p_minus_1(n, B=100000)
    
    if not factor:
        print("Failed to factor n")
        return None
    
    p = factor
    q = n // p
    print(f"Found p ({p.bit_length()} bits) and q ({q.bit_length()} bits)")
    
    # Instead of working with phi(n), let's use the fact that we can solve
    # the discrete log modulo p and modulo q separately, then combine using CRT
    
    print("\nSolving discrete log mod p and mod q...")
    
    # Solve 3^x ≡ c (mod p)
    print("Solving mod p...")
    c_p = c % p
    
    # Try brute force first for small exponents
    for x in range(1, 1000000):
        if powmod(3, x, p) == c_p:
            x_p = x
            print(f"Found x ≡ {x_p} (mod p)")
            break
    else:
        print("Could not solve mod p with brute force")
        return None
    
    # Solve 3^x ≡ c (mod q)  
    print("Solving mod q...")
    c_q = c % q
    
    for x in range(1, 1000000):
        if powmod(3, x, q) == c_q:
            x_q = x
            print(f"Found x ≡ {x_q} (mod q)")
            break
    else:
        print("Could not solve mod q with brute force")
        return None
    
    # Now we have:
    # x ≡ x_p (mod p)
    # x ≡ x_q (mod q)
    # But we need to be more careful about the actual moduli
    
    # The order of 3 modulo p divides p-1, and similarly for q
    # Let's find the orders
    
    order_p = p - 1
    order_q = q - 1
    
    # Verify our solutions are in the right range
    print(f"x_p = {x_p}, order_p = {order_p}")
    print(f"x_q = {x_q}, order_q = {order_q}")
    
    # Use Chinese Remainder Theorem to combine
    # We need to solve:
    # x ≡ x_p (mod order_p)  
    # x ≡ x_q (mod order_q)
    
    # But first check if our solutions work modulo n
    test_x_p = powmod(3, x_p, n)
    test_x_q = powmod(3, x_q, n) 
    
    print(f"Testing: 3^{x_p} mod n = {test_x_p}")
    print(f"Testing: 3^{x_q} mod n = {test_x_q}")
    print(f"Target c = {c}")
    
    if test_x_p == c:
        flag = x_p
    elif test_x_q == c:
        flag = x_q
    else:
        # Need to use CRT properly
        print("Using CRT to combine solutions...")
        
        # Extended Euclidean algorithm
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd_val, u, v = extended_gcd(order_p, order_q)
        
        if (x_q - x_p) % gcd_val != 0:
            print("No solution exists via CRT")
            return None
        
        lcm_val = (order_p * order_q) // gcd_val
        flag = (x_p + order_p * u * ((x_q - x_p) // gcd_val)) % lcm_val
    
    # Verify final solution
    verify = powmod(3, flag, n)
    print(f"\nFinal verification:")
    print(f"3^{flag} mod n = {verify}")
    print(f"Target c = {c}")
    print(f"Match: {verify == c}")
    
    if verify == c:
        print(f"SUCCESS! FLAG = {flag}")
        
        # Convert to string
        flag_hex = hex(flag)[2:]
        if len(flag_hex) % 2:
            flag_hex = '0' + flag_hex
        
        try:
            flag_bytes = bytes.fromhex(flag_hex)
            flag_str = flag_bytes.decode('ascii', errors='replace')
            print(f"FLAG as hex: {flag_hex}")
            print(f"FLAG as string: {repr(flag_str)}")
            
            # Clean up the flag
            clean_chars = ''.join(c for c in flag_str if c.isprintable())
            print(f"Printable characters: {repr(clean_chars)}")
            
            return clean_chars
            
        except Exception as e:
            print(f"Error decoding: {e}")
            return str(flag)
    
    return None

if __name__ == "__main__":
    start_time = time.time()
    flag = solve_challenge_optimized()
    end_time = time.time()
    
    if flag:
        print(f"\nFINAL FLAG: {flag}")
    else:
        print("Failed to recover flag")
    
    print(f"Time taken: {end_time - start_time:.2f} seconds")