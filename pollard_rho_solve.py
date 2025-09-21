#!/usr/bin/env python3

"""
Final attempt using Pollard's rho for discrete logarithms
This is designed for smooth groups where the order has many small factors
"""

from gmpy2 import *
import time
import random

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

def pollard_rho_dlog(g, h, n, order_bound=None):
    """
    Pollard's rho algorithm for discrete logarithm
    Find x such that g^x ≡ h (mod n)
    """
    if order_bound is None:
        order_bound = n  # Conservative bound
    
    print(f"Using Pollard's rho for discrete log")
    print(f"Order bound: {order_bound.bit_length()} bits")
    
    # Define the iteration function f(x) = g^a * h^b * x
    # We'll use a simple partitioning function
    
    def f(x, a, b):
        """Iteration function for Pollard's rho"""
        remainder = x % 3
        
        if remainder == 0:
            return (x * x) % n, (2 * a) % order_bound, (2 * b) % order_bound
        elif remainder == 1:
            return (x * g) % n, (a + 1) % order_bound, b
        else:  # remainder == 2
            return (x * h) % n, a, (b + 1) % order_bound
    
    # Initialize
    x1, a1, b1 = mpz(1), mpz(0), mpz(0)
    x2, a2, b2 = mpz(1), mpz(0), mpz(0)
    
    iterations = 0
    max_iterations = min(1000000, int(order_bound ** 0.5) * 100)
    
    while iterations < max_iterations:
        # Single step for x1
        x1, a1, b1 = f(x1, a1, b1)
        
        # Double step for x2
        x2, a2, b2 = f(*f(x2, a2, b2))
        
        iterations += 1
        
        if x1 == x2:
            # Found collision: g^a1 * h^b1 ≡ g^a2 * h^b2 (mod n)
            # This gives us: g^(a1-a2) ≡ h^(b2-b1) (mod n)
            # So: g^(a1-a2) ≡ h^(b2-b1) (mod n)
            
            da = (a1 - a2) % order_bound
            db = (b2 - b1) % order_bound
            
            print(f"Found collision after {iterations} iterations")
            print(f"da = {da}, db = {db}")
            
            if db == 0:
                print("db = 0, no useful information")
                # Restart with different initial values
                x1, a1, b1 = mpz(random.randint(1, 1000)), mpz(0), mpz(0)
                x2, a2, b2 = mpz(random.randint(1, 1000)), mpz(0), mpz(0)
                continue
            
            # Solve: h^db ≡ g^da (mod n)
            # So: h ≡ g^(da/db) (mod n)
            # We need da/db mod order
            
            try:
                db_inv = invert(db, order_bound)
                result = (da * db_inv) % order_bound
                
                # Verify
                if powmod(g, result, n) == h:
                    print(f"Found solution: {result}")
                    return result
                else:
                    # Try different multiples due to order issues
                    for k in range(10):
                        test_result = (result + k * order_bound // 10) % order_bound
                        if powmod(g, test_result, n) == h:
                            print(f"Found solution with adjustment: {test_result}")
                            return test_result
                    
                    print("Verification failed, continuing search...")
                    
            except Exception as e:
                print(f"Error solving linear equation: {e}")
                continue
        
        if iterations % 100000 == 0:
            print(f"  Iterations: {iterations}")
    
    print("Pollard's rho failed to find solution")
    return None

def final_attempt():
    """Final comprehensive attempt"""
    
    # Read challenge
    with open('/home/runner/work/h/h/output.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    n_hex = lines[0].split(' = ')[1]
    c_hex = lines[1].split(' = ')[1]
    
    n = mpz(n_hex, 16)
    c = mpz(c_hex, 16)
    
    print("=== FINAL ATTEMPT: NSA BACKDOOR CHALLENGE ===")
    print(f"Target: 3^x ≡ c (mod n)")
    print(f"n: {n.bit_length()} bits")
    print(f"c: {c.bit_length()} bits")
    
    # Factor n
    print("\n1. Factoring n...")
    factor = pollard_p_minus_1(n, B=100000)
    
    if not factor:
        print("Failed to factor n")
        return None
    
    p = factor
    q = n // p
    print(f"   p: {p.bit_length()} bits")
    print(f"   q: {q.bit_length()} bits")
    
    # Calculate order bound
    phi_n = (p - 1) * (q - 1)
    print(f"   phi(n): {phi_n.bit_length()} bits")
    
    # Try Pollard's rho
    print("\n2. Attempting Pollard's rho for discrete log...")
    result = pollard_rho_dlog(3, c, n, phi_n)
    
    if result is not None:
        print(f"\n3. SOLUTION FOUND: x = {result}")
        
        # Verify
        verify = powmod(3, result, n)
        print(f"   Verification: 3^{result} mod n")
        print(f"   Expected: {c}")
        print(f"   Got:      {verify}")
        print(f"   Match: {verify == c}")
        
        if verify == c:
            print("\n4. Decoding flag...")
            try:
                flag_hex = hex(result)[2:]
                if len(flag_hex) % 2:
                    flag_hex = '0' + flag_hex
                
                flag_bytes = bytes.fromhex(flag_hex)
                flag_str = flag_bytes.decode('ascii', errors='replace')
                
                print(f"   Hex: {flag_hex}")
                print(f"   String: {repr(flag_str)}")
                
                clean = ''.join(c for c in flag_str if c.isprintable())
                print(f"   Clean: {repr(clean)}")
                
                if 'picoCTF{' in clean:
                    start = clean.find('picoCTF{')
                    end = clean.find('}', start)
                    if end > start:
                        return clean[start:end+1]
                
                return clean
                
            except Exception as e:
                print(f"   Decode error: {e}")
                return str(result)
    
    print("\n❌ All methods failed")
    return None

if __name__ == "__main__":
    start_time = time.time()
    
    flag = final_attempt()
    
    end_time = time.time()
    print(f"\nTotal execution time: {end_time - start_time:.2f} seconds")
    
    if flag:
        print(f"\n🎉 SUCCESS! FINAL FLAG: {flag}")
    else:
        print("\n❌ CHALLENGE NOT SOLVED")
        print("The discrete logarithm may be too large for current methods.")
        print("Consider using specialized tools or a different approach.")