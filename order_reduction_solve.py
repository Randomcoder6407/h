#!/usr/bin/env python3

"""
Correct solution using smooth number properties

The key insight: Since p-1 and q-1 are smooth, we can solve the discrete log
by working modulo small prime factors of the order.
"""

from gmpy2 import *

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

def baby_giant_step(g, h, n, order_bound):
    """Baby-step Giant-step with reasonable bound"""
    m = int(order_bound ** 0.5) + 1
    if m > 1000000:  # Limit memory usage
        m = 1000000
    
    # Baby steps
    table = {}
    gamma = mpz(1)
    for j in range(m):
        if gamma == h:
            return j
        table[gamma] = j
        gamma = (gamma * g) % n
    
    # Giant steps
    factor = invert(powmod(g, m, n), n)
    gamma = h
    
    for i in range(m):
        if gamma in table:
            ans = i * m + table[gamma]
            if ans < order_bound:
                return ans
        gamma = (gamma * factor) % n
    
    return None

def solve_using_order_reduction():
    """Use the fact that the order has many small factors"""
    
    # Read challenge data
    with open('/home/runner/work/h/h/output.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    n_hex = lines[0].split(' = ')[1]
    c_hex = lines[1].split(' = ')[1]
    
    n = mpz(n_hex, 16)
    c = mpz(c_hex, 16)
    
    print(f"Challenge: solve 3^x ≡ c (mod n)")
    print(f"n: {n.bit_length()} bits")
    print(f"c: {c.bit_length()} bits")
    
    # Factor n
    factor = pollard_p_minus_1(n, B=100000)
    if not factor:
        print("Failed to factor")
        return None
    
    p = factor
    q = n // p
    print(f"p: {p.bit_length()} bits")
    print(f"q: {q.bit_length()} bits")
    
    # Key insight: Try to find the actual order of 3 modulo n
    # The order divides lcm(p-1, q-1)
    
    p_minus_1 = p - 1
    q_minus_1 = q - 1
    
    # Find gcd to compute lcm
    g = gcd(p_minus_1, q_minus_1)
    lcm_val = (p_minus_1 * q_minus_1) // g
    
    print(f"lcm(p-1, q-1) = {lcm_val} ({lcm_val.bit_length()} bits)")
    
    # Check if 3^lcm ≡ 1 (mod n)
    test = powmod(3, lcm_val, n)
    print(f"3^lcm mod n = {test}")
    
    if test == 1:
        print("lcm is a valid upper bound for the order")
        
        # Try to find a smaller order by testing divisors
        # Since p-1 and q-1 are smooth, their lcm has many small factors
        
        print("Looking for smaller order by testing small divisors...")
        
        # Try dividing by small primes
        current_order = lcm_val
        
        for small_prime in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]:
            while current_order % small_prime == 0:
                test_order = current_order // small_prime
                if powmod(3, test_order, n) == 1:
                    current_order = test_order
                    print(f"  Reduced order by factor {small_prime}: {current_order.bit_length()} bits")
                else:
                    break
        
        print(f"Found order bound: {current_order} ({current_order.bit_length()} bits)")
        
        # Now try baby-step giant-step with this order
        if current_order.bit_length() <= 40:  # Reasonable for BSGS
            print("Attempting baby-step giant-step...")
            result = baby_giant_step(3, c, n, current_order)
            
            if result is not None:
                print(f"Found discrete log: {result}")
                
                # Verify
                verify = powmod(3, result, n)
                if verify == c:
                    print("Verification successful!")
                    return result
                else:
                    print("Verification failed")
        else:
            print("Order still too large for BSGS")
    
    # Alternative: Try working modulo p and q separately
    print("\nTrying to solve modulo p and q separately...")
    
    # Solve 3^x ≡ c (mod p)
    c_mod_p = c % p
    print(f"Solving 3^x ≡ {c_mod_p} (mod p)")
    
    # Use baby-step giant-step modulo p
    result_p = baby_giant_step(3, c_mod_p, p, p_minus_1)
    
    if result_p is not None:
        print(f"Found x ≡ {result_p} (mod p)")
        
        # Check if this is the full solution
        if powmod(3, result_p, n) == c:
            print("This works for the full problem!")
            return result_p
        
        # Otherwise, solve modulo q too
        c_mod_q = c % q
        result_q = baby_giant_step(3, c_mod_q, q, q_minus_1)
        
        if result_q is not None:
            print(f"Found x ≡ {result_q} (mod q)")
            
            # Combine using Chinese Remainder Theorem
            # We need x such that:
            # x ≡ result_p (mod ord_p)
            # x ≡ result_q (mod ord_q)
            # where ord_p, ord_q are the orders of 3 mod p, q respectively
            
            # For simplicity, assume the orders are p-1 and q-1
            # (this might not be exact, but often works for challenges)
            
            def extended_gcd(a, b):
                if a == 0:
                    return b, 0, 1
                gcd, x1, y1 = extended_gcd(b % a, a)
                x = y1 - (b // a) * x1
                y = x1
                return gcd, x, y
            
            gcd_val, u, v = extended_gcd(p_minus_1, q_minus_1)
            
            if (result_q - result_p) % gcd_val == 0:
                lcm_orders = (p_minus_1 * q_minus_1) // gcd_val
                combined = (result_p + p_minus_1 * u * ((result_q - result_p) // gcd_val)) % lcm_orders
                
                # Verify
                if powmod(3, combined, n) == c:
                    print(f"Combined solution works: {combined}")
                    return combined
    
    return None

def decode_result(result):
    """Convert result back to flag"""
    if result is None:
        return None
    
    try:
        flag_hex = hex(result)[2:]
        if len(flag_hex) % 2:
            flag_hex = '0' + flag_hex
        
        flag_bytes = bytes.fromhex(flag_hex)
        flag_str = flag_bytes.decode('ascii', errors='replace')
        
        print(f"Result: {result}")
        print(f"Hex: {flag_hex}")
        print(f"String: {repr(flag_str)}")
        
        return flag_str
        
    except Exception as e:
        print(f"Decode error: {e}")
        return str(result)

if __name__ == "__main__":
    result = solve_using_order_reduction()
    if result is not None:
        flag = decode_result(result)
        print(f"\nFINAL FLAG: {flag}")
    else:
        print("Could not solve the discrete logarithm")