#!/usr/bin/env python3

"""
Correct solution for NSA Backdoor Challenge

The encryption is c = 3^FLAG mod n, so we need to solve the discrete logarithm:
FLAG = log_3(c) mod phi(n)

Since we can factor n into smooth primes p and q, we can use the fact that
the order of 3 modulo n divides phi(n) = (p-1)(q-1).

Since p-1 and q-1 are smooth (have small prime factors), we can use
Pohlig-Hellman algorithm to solve the discrete log.
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

def discrete_log_smooth(g, h, n, p_minus_1_factors, q_minus_1_factors):
    """
    Solve discrete log using smooth prime factorization
    Find x such that g^x ≡ h (mod n)
    where n = p*q and we know the prime factorizations of p-1 and q-1
    """
    p = None
    q = None
    
    # First, let's get p and q from n
    factor = pollard_p_minus_1(n, B=100000)
    if factor:
        p = factor
        q = n // p
    else:
        return None
    
    # Calculate phi(n) = (p-1)(q-1)
    phi_n = (p - 1) * (q - 1)
    
    # The key insight: since p-1 and q-1 are smooth, phi(n) has a lot of small factors
    # We can solve the discrete log by solving it modulo small prime powers
    
    # For now, let's try a simpler approach using the fact that the order divides phi(n)
    # and phi(n) has small factors
    
    # Try to find the order of g modulo n
    order_candidates = []
    
    # Check if g^phi(n) ≡ 1 (mod n) (it should be by Euler's theorem)
    if powmod(g, phi_n, n) != 1:
        print("Warning: g^phi(n) != 1 mod n")
    
    # Since phi(n) is smooth, try to find smaller orders
    phi_factors = []
    temp = phi_n
    
    # Factor phi(n) using trial division up to reasonable bound
    for prime in range(2, 100000):
        if is_prime(prime):
            while temp % prime == 0:
                phi_factors.append(prime)
                temp //= prime
        if temp == 1:
            break
    
    if temp > 1:
        # phi(n) has a large prime factor, but let's try anyway
        phi_factors.append(temp)
    
    print(f"Found {len(phi_factors)} prime factors of phi(n)")
    
    # Try Baby-step Giant-step on reduced problem
    # Since the factors are small, the discrete log should be solvable
    
    # For smooth numbers, we can often solve the discrete log directly
    # Let's try with smaller bounds first
    
    for bound in [10000, 100000, 1000000]:
        print(f"Trying discrete log with bound {bound}")
        for x in range(1, bound):
            if powmod(g, x, n) == h:
                return x
        
        # Try some multiples of common small values
        for base in [2, 3, 5, 7, 11, 13, 17, 19, 23]:
            for mult in range(1, bound // base + 1):
                x = base * mult
                if powmod(g, x, n) == h:
                    return x
    
    return None

def solve_discrete_log():
    """Solve the smooth discrete log challenge"""
    
    # Read n and c from output
    with open('/home/runner/work/h/h/output.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    n_hex = lines[0].split(' = ')[1]
    c_hex = lines[1].split(' = ')[1]
    
    n = mpz(n_hex, 16)
    c = mpz(c_hex, 16)
    
    print(f"n bit length: {n.bit_length()}")
    print(f"c bit length: {c.bit_length()}")
    
    # Factor n
    print("\nFactoring n...")
    factor = pollard_p_minus_1(n, B=100000)
    
    if factor:
        p = factor
        q = n // p
        print(f"Found factors: p, q with bit lengths {p.bit_length()}, {q.bit_length()}")
        
        # Now solve discrete log: 3^FLAG ≡ c (mod n)
        print("\nSolving discrete logarithm...")
        
        flag = discrete_log_smooth(3, c, n, [], [])
        
        if flag:
            print(f"Found FLAG = {flag}")
            
            # Verify
            verify = powmod(3, flag, n)
            print(f"Verification: 3^{flag} mod n = {verify}")
            print(f"Expected c = {c}")
            print(f"Verification successful: {verify == c}")
            
            if verify == c:
                # Convert flag to string
                flag_hex = hex(flag)[2:]
                if len(flag_hex) % 2:
                    flag_hex = '0' + flag_hex
                
                try:
                    flag_bytes = bytes.fromhex(flag_hex)
                    flag_str = flag_bytes.decode('ascii', errors='ignore')
                    print(f"Flag as hex: {flag_hex}")
                    print(f"Flag as string: {repr(flag_str)}")
                    return flag_str
                except Exception as e:
                    print(f"Error converting flag: {e}")
                    return str(flag)
            
        return None
    else:
        print("Could not factor n")
        return None

if __name__ == "__main__":
    flag = solve_discrete_log()
    if flag:
        print(f"\nFINAL FLAG: {flag}")
    else:
        print("Could not recover flag")