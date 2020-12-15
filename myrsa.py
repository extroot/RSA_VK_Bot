import random


def get_primes(start, stop):
    primes = [2]
    if start >= stop:
        return []

    for n in range(3, stop + 1, 2):
        for p in primes:
            if n % p == 0:
                break
        else:
            primes.append(n)

    while primes and primes[0] < start:
        del primes[0]

    return primes


def are_relatively_prime(a, b):
    for n in range(2, min(a, b) + 1):
        if a % n == b % n == 0:
            return False
    return True


def make_key_pair(length):
    n_min = 1 << (length - 1)
    n_max = (1 << length) - 1

    start = 1 << (length // 2 - 1)
    stop = 1 << (length // 2 + 1)
    primes = get_primes(start, stop)
    # print(length, start, stop, primes)

    while primes:
        p = random.choice(primes)
        primes.remove(p)
        q_candidates = [q for q in primes
                        if n_min <= p * q <= n_max]
        if q_candidates:
            q = random.choice(q_candidates)
            break
    else:
        raise Exception('Something went wrong...')

    stop = (p - 1) * (q - 1)
    for e in range(3, stop, 2):
        if are_relatively_prime(e, stop):
            break
    else:
        raise Exception('Something went wrong...')

    for d in range(3, stop, 2):
        if d * e % stop == 1:
            break
    else:
        raise Exception('Something went wrong...')

    return (p * q, e), (p * q, d)


def encoding(key, text):
    return ''.join([chr(pow(ord(x), key[1], key[0])) for x in text])
