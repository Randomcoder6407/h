#!/usr/bin/env python3

"""
Smart solution using properties of smooth numbers
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

def smart_solve():
    """Use the structure of the challenge"""
    
    # Read values
    with open('/home/runner/work/h/h/output.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    n_hex = lines[0].split(' = ')[1]
    c_hex = lines[1].split(' = ')[1]
    
    n = mpz(n_hex, 16)
    c = mpz(c_hex, 16)
    
    print(f"n = {n}")
    print(f"c = {c}")
    
    # Factor n
    factor = pollard_p_minus_1(n, B=100000)
    if not factor:
        print("Failed to factor")
        return None
    
    p = factor
    q = n // p
    print(f"\nFactored n:")
    print(f"p = {p}")
    print(f"q = {q}")
    
    # Let's think about this differently
    # The flag was converted to an integer via hexlify
    # So FLAG_int = int(hexlify(FLAG_string), 16)
    # Then c = 3^FLAG_int mod n
    
    # Given the challenge is about NSA backdoors and the structure,
    # let's check if the flag might be relatively small
    
    # Try to estimate the flag size
    # A typical picoCTF flag might be 20-40 characters
    # That's 160-320 bits when hex-encoded
    
    max_flag_bits = 512  # Be generous
    max_flag_value = 2 ** max_flag_bits
    
    print(f"\nTrying discrete log with flag up to {max_flag_bits} bits...")
    
    # Use a more efficient approach - Baby Step Giant Step
    # But adapted for the smooth number structure
    
    # Since p and q are smooth, let's try working modulo their orders
    # The order of 3 modulo p divides p-1, and p-1 is smooth
    
    # Let's try a hybrid approach
    print("Analyzing the multiplicative order of 3...")
    
    # Check the order of 3 modulo p and q
    order_p = p - 1
    order_q = q - 1
    
    # Try to find a smaller order by testing divisors
    def find_order(g, n, max_order):
        """Find the multiplicative order of g modulo n"""
        for i in range(1, min(max_order, 10000)):
            if powmod(g, i, n) == 1:
                return i
        return max_order
    
    actual_order_p = find_order(3, p, order_p)
    actual_order_q = find_order(3, q, order_q)
    
    print(f"Order of 3 mod p: {actual_order_p} (max: {order_p})")
    print(f"Order of 3 mod q: {actual_order_q} (max: {order_q})")
    
    # Now try a targeted approach
    # Since this is a challenge, the flag is probably "reasonable" size
    
    print("\nTrying baby-step giant-step with reasonable flag size...")
    
    # Baby-step Giant-step specifically for this problem
    m = int(2**20)  # Try up to about 1M
    
    print(f"Baby steps up to {m}...")
    baby_steps = {}
    g_power = mpz(1)
    
    for i in range(m):
        if g_power == c:
            print(f"Found flag directly: {i}")
            return convert_flag_to_string(i)
        
        baby_steps[g_power] = i
        g_power = (g_power * 3) % n
        
        if i % 100000 == 0 and i > 0:
            print(f"  Computed {i} baby steps...")
    
    print(f"Giant steps...")
    gamma = c
    g_inv_m = invert(powmod(3, m, n), n)
    
    for j in range(m):
        if gamma in baby_steps:
            flag = j * m + baby_steps[gamma]
            print(f"Found flag: {flag}")
            
            # Verify
            verify = powmod(3, flag, n)
            if verify == c:
                print("Verification successful!")
                return convert_flag_to_string(flag)
            else:
                print("Verification failed, continuing...")
        
        gamma = (gamma * g_inv_m) % n
        
        if j % 10000 == 0 and j > 0:
            print(f"  Completed {j} giant steps...")
    
    print("Baby-step Giant-step failed")
    return None

def convert_flag_to_string(flag_int):
    """Convert flag integer back to string"""
    try:
        flag_hex = hex(flag_int)[2:]
        if len(flag_hex) % 2:
            flag_hex = '0' + flag_hex
        
        flag_bytes = bytes.fromhex(flag_hex)
        flag_str = flag_bytes.decode('ascii', errors='replace')
        
        print(f"Flag as integer: {flag_int}")
        print(f"Flag as hex: {flag_hex}")
        print(f"Flag as string: {repr(flag_str)}")
        
        # Look for picoCTF pattern
        if 'picoCTF{' in flag_str:
            start = flag_str.find('picoCTF{')
            end = flag_str.find('}', start)
            if end > start:
                return flag_str[start:end+1]
        
        return flag_str
        
    except Exception as e:
        print(f"Error converting flag: {e}")
        return str(flag_int)

if __name__ == "__main__":
    flag = smart_solve()
    if flag:
        print(f"\nFINAL FLAG: {flag}")
    else:
        print("Could not recover flag")