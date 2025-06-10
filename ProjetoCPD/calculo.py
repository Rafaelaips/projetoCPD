## Componente 1 - Módulo de Cálculo Paralelizado
import multiprocessing
import math
import time
from multiprocessing import Queue, Value, Lock, Process
from queue import Empty
import random

from typing import Optional, Tuple, List



def is_prime(n: int) -> bool:
    """Verifica se o número inteiro n é primo. True se n for primo, False caso contrário."""
    if not isinstance(n, int):
        raise TypeError("O argumento n deve ser um inteiro.")

    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0 or n % 3 == 0 or n % 5 == 0:
        return n == 2 or n == 3 or n == 5

    # Testar números da forma 6k ± 1 até √n
    limit = int(math.isqrt(n)) + 1
    for i in range(5, limit, 6):
        if n % i == 0 or n % (i + 2) == 0:
            return False
    return True



def find_max_prime_sequential(timeout: int,start_base:int =3) -> int:
    """Encontra o maior primo possível dentro do tempo limite (sequencialmente). (start_base é o nr a partir do qual começa a procurar(padrão=3)."""
    if not isinstance(timeout, int) or timeout < 0:
        raise ValueError("timeout deve ser um inteiro positivo.")
    start_time = time.time()
    max_prime = 2
    n = start_base if start_base % 2 == 1 else start_base + 1
    while time.time() - start_time < timeout:
        if is_prime(n):
            max_prime = n
        n += 2  # só testa ímpares
    return max_prime

def _candidate_generator(queue: Queue, stop_event: multiprocessing.Event, base: int = 10_000_001):
    n = base if base % 2 == 1 else base + 1
    while not stop_event.is_set():
        queue.put(n)
        n += 2

def _worker_dynamic(queue: Queue, max_prime: Value, lock: Lock, stop_event: multiprocessing.Event):
    while not stop_event.is_set():
        try:
            n = queue.get(timeout=0.1)
            if is_prime(n):
                with lock:
                    if n > max_prime.value:
                        max_prime.value = n
        except Empty:
            continue

def find_max_prime_parallel(timeout: int, n_workers: int = 4) -> int:
    if not isinstance(timeout, int) or timeout < 0:
        raise ValueError("timeout deve ser um inteiro positivo.")
    if not isinstance(n_workers, int) or n_workers < 1:
        raise ValueError("n_workers deve ser um inteiro positivo.")

    queue = Queue(maxsize=1000)  # Limitar para evitar uso excessivo de memória
    max_prime = Value('q', 2)
    lock = Lock()
    stop_event = multiprocessing.Event()

    # Começa em números maiores conforme timeout cresce (mais dígitos)
    start_base = 10 ** (6 + timeout // 4)

    generator = Process(target=_candidate_generator, args=(queue, stop_event, start_base))
    generator.start()

    workers = []
    for _ in range(n_workers):
        p = Process(target=_worker_dynamic, args=(queue, max_prime, lock, stop_event))
        p.start()
        workers.append(p)

    time.sleep(timeout)
    stop_event.set()

    generator.join()
    for p in workers:
        p.join()

    return max_prime.value




def find_next_twin_primes(n: int) -> Optional[Tuple[int, int]]:
    """Devolve o próximo par de primos gémeos(se a diferença entre eles é 2) após o número n. """

    k = max(n + 1, 3)
    if k % 2 == 0:
        k += 1  # Começa pelo próximo ímpar

    while True:
        if is_prime(k) and is_prime(k + 2):
            return (k, k + 2)
        k += 2  # Testa apenas ímpares



def is_mersenne_prime(n: int) -> bool:
    """Verifica se n é um primo de Mersenne.Um primo de Mersenne é da forma n = 2^p - 1, com p primo."""
    if n < 2:
        return False
    p = 1
    while (2 ** p - 1) < n:
        p += 1
    if (2 ** p - 1) == n and is_prime(p) and is_prime(n):
        return True
    return False

def prime_factors(n: int) -> List[int]:
    """Decompõe n nos seus fatores primos, em ordem crescente."""
    if not isinstance(n, int):
        raise TypeError("n deve ser um inteiro.")


    n = abs(n)  # Usa valor absoluto para lidar com negativos
    factors = []
    divisor = 2
    while divisor * divisor <= n:
        while n % divisor == 0:
            factors.append(divisor)
            n //= divisor
        divisor += 1
    if n > 1:
        factors.append(n)
    return factors

def next_prime(n: int) -> int:
    """Devolve o menor número primo estritamente maior do que n."""
    if not isinstance(n, int):
        raise TypeError("n deve ser um inteiro.")

    candidate = n + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate

from typing import Optional

def previous_prime(n: int) -> Optional[int]:
    """Devolve o maior número primo estritamente menor do que n."""
    if not isinstance(n, int):
        raise TypeError("n deve ser um inteiro.")

    candidate = n - 1
    while candidate >= 2:
        if is_prime(candidate):  # Usa a função is_prime existente
            return candidate
        candidate -= 1
    return None

""""""""""""""""""""""""""""""""

if __name__ == "__main__":
    print("### Testes simples das funções do módulo ###\n")

    # Testar is_prime
    print("is_prime:")
    for n in [1, 2, 17, 18, 25]:
        print(f"  is_prime({n}) = {is_prime(n)}")
    print()

    # Testar find_max_prime_sequential (curto prazo)
    print("find_max_prime_sequential (5s):")
    prime_seq = find_max_prime_sequential(timeout=5)
    print(f"  Maior primo sequencial encontrado: {prime_seq}\n")

    # Testar find_max_prime_parallel (5s, 4 workers)
    print("find_max_prime_parallel (5s, 4 workers):")
    prime_par = find_max_prime_parallel(timeout=5, n_workers=4)
    print(f"  Maior primo paralelo encontrado: {prime_par}\n")
    print("anabuebfujebu")
    print("5 segundos:", find_max_prime_parallel(5, 4))
    print("10 segundos:", find_max_prime_parallel(10, 4))
    print("15 segundos:", find_max_prime_parallel(15, 4))

    prime_par11=find_max_prime_parallel(timeout=10,n_workers=4)
    print(f"primo paralelo encontrado: {prime_par11}\n ")
    # Testar find_next_twin_primes
    print("find_next_twin_primes:")
    for start in [3, 100]:
        twins = find_next_twin_primes(start)
        print(f"  Próximos primos gémeos após {start}: {twins}")
    print()

    # Testar is_mersenne_prime
    print("is_mersenne_prime:")
    for n in [3, 7, 15, 31]:
        print(f"  is_mersenne_prime({n}) = {is_mersenne_prime(n)}")
    print()

    # Testar prime_factors
    print("prime_factors:")
    for n in [60, 13, -45]:
        factors = prime_factors(n)
        print(f"  prime_factors({n}) = {factors}")
    print()

    # Testar next_prime e previous_prime
    print("next_prime e previous_prime:")
    for n in [3, 11, 2]:
        np = next_prime(n)
        pp = previous_prime(n)
        print(f"  next_prime({n}) = {np}")
        print(f"  previous_prime({n}) = {pp}")
    print()

    """for n in [2, 4, 8, 12, 16]:
        print(f"Testando com {n} workers:")
        start = time.time()
        p = find_max_prime_parallel(10, n)
        dur = time.time() - start
        print(f"  Primo: {p} ({len(str(p))} dígitos), tempo: {dur:.2f}s\n")"""

    print("### Fim dos testes ###")
