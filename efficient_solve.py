#!/usr/bin/env python3

"""
Let me try to use known attacks specific to smooth numbers.
The issue might be that I'm not using the right approach for this specific backdoor.
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

def simple_dlog_search(g, h, n, max_exp=10**7):
    """Simple discrete log search with periodic reporting"""
    print(f"Searching for x where {g}^x ≡ h (mod n)")
    print(f"Max exponent to try: {max_exp}")
    
    current = mpz(1)
    for x in range(max_exp):
        if current == h:
            return x
        current = (current * g) % n
        
        if x % 1000000 == 0 and x > 0:
            print(f"  Tried up to x = {x}")
    
    return None

def efficient_solve():
    """Try the most direct approach first"""
    
    # Read challenge
    with open('/home/runner/work/h/h/output.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    n_hex = lines[0].split(' = ')[1]
    c_hex = lines[1].split(' = ')[1]
    
    n = mpz(n_hex, 16)
    c = mpz(c_hex, 16)
    
    print(f"Solving: find x such that 3^x ≡ c (mod n)")
    print(f"n has {n.bit_length()} bits")
    print(f"c has {c.bit_length()} bits")
    
    # Factor n quickly
    start_time = time.time()
    factor = pollard_p_minus_1(n, B=100000)
    factor_time = time.time() - start_time
    
    if not factor:
        print("Could not factor n")
        return None
    
    p = factor
    q = n // p
    print(f"Factored in {factor_time:.2f}s: p({p.bit_length()} bits), q({q.bit_length()} bits)")
    
    # Strategy: Since this is a CTF challenge, the flag probably has a reasonable size
    # Let's try a larger but still manageable search space
    
    print("\nAttempting direct search...")
    result = simple_dlog_search(3, c, n, max_exp=50000000)  # Try up to 50M
    
    if result is not None:
        print(f"Found solution: x = {result}")
        
        # Verify
        verify = powmod(3, result, n)
        if verify == c:
            print("Verification successful!")
            
            # Decode
            try:
                flag_hex = hex(result)[2:]
                if len(flag_hex) % 2:
                    flag_hex = '0' + flag_hex
                
                flag_bytes = bytes.fromhex(flag_hex)
                flag_str = flag_bytes.decode('ascii', errors='replace')
                
                print(f"Flag as hex: {flag_hex}")
                print(f"Flag as string: {repr(flag_str)}")
                
                # Look for picoCTF pattern
                clean_flag = ''.join(c for c in flag_str if c.isprintable())
                print(f"Clean flag: {repr(clean_flag)}")
                
                if 'picoCTF{' in clean_flag:
                    start = clean_flag.find('picoCTF{')
                    end = clean_flag.find('}', start)
                    if end > start:
                        final_flag = clean_flag[start:end+1]
                        return final_flag
                
                return clean_flag
                
            except Exception as e:
                print(f"Decode error: {e}")
                return str(result)
        else:
            print("Verification failed!")
    
    print("Direct search failed")
    return None

if __name__ == "__main__":
    print("Starting NSA Backdoor Challenge Solution")
    start_time = time.time()
    
    flag = efficient_solve()
    
    end_time = time.time()
    print(f"\nTotal time: {end_time - start_time:.2f} seconds")
    
    if flag:
        print(f"\n🎉 FINAL FLAG: {flag}")
    else:
        print("❌ Could not solve the challenge")
        print("\nThe flag might be larger than expected, or require a more sophisticated algorithm.")
        print("Consider implementing Pollard's rho for discrete logs or other advanced methods.")