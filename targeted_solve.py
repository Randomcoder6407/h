#!/usr/bin/env python3

"""
Alternative approach: Maybe the flag encoding is different than I thought
Let's examine what the original code does more carefully
"""

from gmpy2 import *
from binascii import hexlify

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

def analyze_flag_encoding():
    """Let's understand how the flag was encoded"""
    
    # From gen.py:
    # FLAG  = open('flag.txt').read().strip()
    # FLAG  = mpz(hexlify(FLAG.encode()), 16)
    
    # So if we have a typical flag like "picoCTF{some_text}"
    # It gets:
    # 1. Encoded to bytes: b'picoCTF{some_text}'
    # 2. Hex encoded: hexlify gives hex representation as bytes
    # 3. Converted to integer: mpz(..., 16)
    
    # Let's see what size this would be for a typical flag
    test_flags = [
        "picoCTF{test}",
        "picoCTF{a_longer_test_flag}",
        "picoCTF{this_is_a_much_longer_flag_for_testing}",
        "picoCTF{smooth_criminal}"
    ]
    
    print("Analyzing typical flag sizes:")
    for flag in test_flags:
        flag_bytes = flag.encode()
        flag_hex = hexlify(flag_bytes)
        flag_int = int(flag_hex, 16)
        print(f"'{flag}' -> {flag_int.bit_length()} bits")
    
    # This suggests flags are typically 100-400 bits
    return 400  # Upper bound estimate

def solve_with_smaller_search():
    """Try solving with a more targeted search based on flag size"""
    
    # Read challenge data
    with open('/home/runner/work/h/h/output.txt', 'r') as f:
        lines = f.read().strip().split('\n')
    
    n_hex = lines[0].split(' = ')[1]
    c_hex = lines[1].split(' = ')[1]
    
    n = mpz(n_hex, 16)
    c = mpz(c_hex, 16)
    
    print(f"n: {n.bit_length()} bits")
    print(f"c: {c.bit_length()} bits")
    
    # Factor n
    factor = pollard_p_minus_1(n, B=100000)
    if not factor:
        print("Failed to factor")
        return None
    
    p = factor
    q = n // p
    print(f"Factored: p({p.bit_length()}), q({q.bit_length()})")
    
    # Get upper bound for flag size
    max_flag_bits = analyze_flag_encoding()
    max_flag_value = 2 ** max_flag_bits
    
    print(f"\nSearching for flag up to {max_flag_bits} bits...")
    print(f"Max value: {max_flag_value}")
    
    # Try a smarter search
    # Since we're looking for something that encodes to readable text,
    # let's try different ranges
    
    ranges_to_try = [
        (1, 2**16),           # Very small flags
        (2**16, 2**24),       # Small flags  
        (2**24, 2**32),       # Medium flags
        (2**32, 2**40),       # Larger flags
    ]
    
    for start, end in ranges_to_try:
        print(f"\nTrying range {start} to {end}...")
        
        for x in range(start, min(end, start + 1000000)):  # Limit iterations
            if powmod(3, x, n) == c:
                print(f"FOUND FLAG VALUE: {x}")
                
                # Convert back to string
                flag_hex = hex(x)[2:]
                if len(flag_hex) % 2:
                    flag_hex = '0' + flag_hex
                
                try:
                    flag_bytes = bytes.fromhex(flag_hex)
                    flag_str = flag_bytes.decode('ascii', errors='replace')
                    print(f"Flag: {repr(flag_str)}")
                    
                    if 'picoCTF{' in flag_str:
                        start_idx = flag_str.find('picoCTF{')
                        end_idx = flag_str.find('}', start_idx)
                        if end_idx > start_idx:
                            return flag_str[start_idx:end_idx+1]
                    
                    return flag_str
                    
                except Exception as e:
                    print(f"Decode error: {e}")
                    return str(x)
            
            if x % 100000 == 0 and x > start:
                print(f"  Checked up to {x}")
    
    # If ranges don't work, try a different approach
    # Maybe work modulo p and q separately
    print(f"\nTrying to solve modulo p and q separately...")
    
    c_mod_p = c % p  
    c_mod_q = c % q
    
    print(f"Solving 3^x ≡ {c_mod_p} (mod {p})")
    print(f"Solving 3^x ≡ {c_mod_q} (mod {q})")
    
    # For smooth primes, try small exponents
    for x in range(1, 1000000):
        if powmod(3, x, p) == c_mod_p:
            print(f"Found x ≡ {x} (mod p)")
            # Check if this works for full problem
            if powmod(3, x, n) == c:
                print(f"This is the full solution!")
                return decode_flag(x)
            break
        
        if x % 100000 == 0:
            print(f"  Checked up to {x} mod p")
    
    return None

def decode_flag(flag_int):
    """Decode integer back to flag string"""
    try:
        flag_hex = hex(flag_int)[2:]
        if len(flag_hex) % 2:
            flag_hex = '0' + flag_hex
        
        flag_bytes = bytes.fromhex(flag_hex)
        flag_str = flag_bytes.decode('ascii', errors='replace')
        
        print(f"Decoded: {repr(flag_str)}")
        return flag_str
        
    except Exception as e:
        print(f"Decode error: {e}")
        return str(flag_int)

if __name__ == "__main__":
    flag = solve_with_smaller_search()
    if flag:
        print(f"\nFINAL FLAG: {flag}")
    else:
        print("Could not find flag")