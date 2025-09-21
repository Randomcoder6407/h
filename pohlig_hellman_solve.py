#!/usr/bin/env python3

"""
Proper Pohlig-Hellman solution for NSA Backdoor Challenge

Using Pohlig-Hellman algorithm to solve discrete log in smooth groups
"""

from gmpy2 import *
from collections import defaultdict

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

def factor_integer(n, max_prime=1000000):
    """Factor an integer into prime powers"""
    factors = defaultdict(int)
    
    # Handle small primes first
    for p in range(2, min(max_prime, int(n**0.5) + 1)):
        if is_prime(p):
            while n % p == 0:
                factors[p] += 1
                n //= p
        if n == 1:
            break
    
    if n > 1:
        if is_prime(n):
            factors[n] = 1
        else:
            # Try harder factorization methods if needed
            factors[n] = 1  # Assume it's prime for now
    
    return dict(factors)

def baby_step_giant_step(g, h, n, order):
    """Baby-step Giant-step algorithm for discrete log"""
    m = int(order**0.5) + 1
    
    # Baby steps: store g^j for j = 0, 1, ..., m-1
    baby_steps = {}
    current = mpz(1)
    for j in range(m):
        if current == h:
            return j
        baby_steps[current] = j
        current = (current * g) % n
    
    # Giant steps: check if h * (g^(-m))^i is in baby_steps
    g_inv_m = invert(powmod(g, m, n), n)
    gamma = h
    
    for i in range(m):
        if gamma in baby_steps:
            result = i * m + baby_steps[gamma]
            if result < order:
                return result
        gamma = (gamma * g_inv_m) % n
    
    return None

def pohlig_hellman(g, h, n, order_factors, order):
    """
    Pohlig-Hellman algorithm for discrete logarithm
    Solve g^x ≡ h (mod n) where order has known factorization
    """
    print(f"Using Pohlig-Hellman with {len(order_factors)} prime factors")
    
    remainders = []
    moduli = []
    
    for p, e in order_factors.items():
        pe = p ** e
        
        # Solve x mod p^e
        print(f"Solving for prime power {p}^{e} = {pe}")
        
        # Reduce the problem to order p^e
        order_pe = pe
        g_pe = powmod(g, order // order_pe, n)
        h_pe = powmod(h, order // order_pe, n)
        
        # Use baby-step giant-step for this subproblem
        x_pe = baby_step_giant_step(g_pe, h_pe, n, order_pe)
        
        if x_pe is not None:
            print(f"Found x ≡ {x_pe} (mod {pe})")
            remainders.append(x_pe)
            moduli.append(pe)
        else:
            print(f"Failed to solve for prime power {pe}")
            return None
    
    # Combine using Chinese Remainder Theorem
    if remainders:
        print("Combining results using CRT...")
        result = remainders[0]
        modulus = moduli[0]
        
        for i in range(1, len(remainders)):
            # Solve: result ≡ r_i (mod m_i), result ≡ r_{i-1} (mod modulus)
            r_i = remainders[i]
            m_i = moduli[i]
            
            # Extended Euclidean algorithm
            g, u, v = gcdext(modulus, m_i)
            if g != 1:
                print(f"Error: moduli {modulus} and {m_i} are not coprime")
                return None
            
            # result = result + modulus * ((r_i - result) * invert(modulus, m_i))
            diff = (r_i - result) % m_i
            result = result + modulus * ((diff * invert(modulus, m_i)) % m_i)
            modulus = modulus * m_i
        
        return result % modulus
    
    return None

def solve_challenge():
    """Solve the NSA backdoor challenge"""
    
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
    
    # Calculate the order of the multiplicative group
    # For smooth primes, we use lambda(n) = lcm(p-1, q-1)
    # But we'll start with phi(n) = (p-1)(q-1)
    
    phi_n = (p - 1) * (q - 1)
    print(f"phi(n) has {phi_n.bit_length()} bits")
    
    # Factor phi(n) - this should be smooth
    print("Factoring phi(n)...")
    phi_factors = factor_integer(phi_n, max_prime=100000)
    
    print(f"Found factorization of phi(n): {phi_factors}")
    
    # Check if factorization is complete
    product = mpz(1)
    for prime, exp in phi_factors.items():
        product *= prime ** exp
    
    if product != phi_n:
        print(f"Incomplete factorization: {product} != {phi_n}")
        print(f"Missing factor: {phi_n // product}")
        # Add the missing factor (assuming it's prime)
        missing = phi_n // product
        if missing > 1:
            phi_factors[missing] = 1
    
    # Now solve the discrete log using Pohlig-Hellman
    print("\nSolving discrete logarithm using Pohlig-Hellman...")
    flag = pohlig_hellman(3, c, n, phi_factors, phi_n)
    
    if flag is not None:
        # Verify the solution
        verify = powmod(3, flag, n)
        print(f"\nVerification: 3^{flag} mod n")
        print(f"Expected: {c}")
        print(f"Got:      {verify}")
        print(f"Match: {verify == c}")
        
        if verify == c:
            print(f"FLAG as integer: {flag}")
            
            # Convert to string
            flag_hex = hex(flag)[2:]
            if len(flag_hex) % 2:
                flag_hex = '0' + flag_hex
            
            try:
                flag_bytes = bytes.fromhex(flag_hex)
                flag_str = flag_bytes.decode('ascii', errors='ignore')
                print(f"FLAG as hex: {flag_hex}")
                print(f"FLAG as string: {repr(flag_str)}")
                
                # Look for picoCTF pattern
                if 'picoCTF{' in flag_str:
                    start = flag_str.find('picoCTF{')
                    end = flag_str.find('}', start)
                    if end > start:
                        return flag_str[start:end+1]
                
                return flag_str
                
            except Exception as e:
                print(f"Error decoding flag: {e}")
                return str(flag)
        else:
            print("Verification failed")
            return None
    else:
        print("Failed to solve discrete logarithm")
        return None

if __name__ == "__main__":
    flag = solve_challenge()
    if flag:
        print(f"\nFINAL FLAG: {flag}")
    else:
        print("Failed to recover flag")