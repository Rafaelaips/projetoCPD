## Componente 2 - Criptografia e Quebra Paralela

import random
import math
from multiprocessing import Process, Value, Event
import time
from typing import Tuple

from calculo import is_prime, next_prime

#funções auxiliares
def mdc(a: int, b: int) -> int:
    """Calcula o máximo divisor comum (MDC) entre dois inteiros a e b."""
    if not isinstance(a, int) or not isinstance(b, int):
        raise TypeError("mdc: os argumentos devem ser inteiros.")

    while b != 0:
        a, b = b, a % b
    return a


def inverso_modular(e: int, phi: int) -> int:
    """Calcula o inverso modular de e módulo phi, ou seja, x tal que (e * x) % phi = 1."""
    if not isinstance(e, int) or not isinstance(phi, int):
        raise TypeError("inverso_modular: e e phi devem ser inteiros.")
    if phi <= 0:
        raise ValueError("inverso_modular: phi deve ser positivo.")


    # Algoritmo de Euclides estendido
    def egcd(a, b):
        if b == 0:
            return a, 1, 0
        g, x1, y1 = egcd(b, a % b)
        x = y1
        y = x1 - (a // b) * y1
        return g, x, y

    g, x, _ = egcd(e, phi)
    if g != 1:
        raise ValueError("e e phi não são coprimos")
    return x % phi


def generate_keys(bits: int) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """Gera um par de chaves RSA públicas e privadas. Introduz um int!"""
    if not isinstance(bits, int) or bits < 4:
        raise ValueError("generate_keys: bits deve ser um inteiro ≥ 4.")

    # Escolhe p e q primos distintos, aproximadamente metade dos bits cada
    while True:
        p = next_prime(random.getrandbits(bits // 2) | (1 << (bits // 2 - 1)) | 1)
        q = next_prime(random.getrandbits(bits // 2) | (1 << (bits // 2 - 1)) | 1)
        if p != q:
            break

    n = p * q
    phi = (p - 1) * (q - 1)

    e = 65537
    if mdc(e, phi) != 1:
        # Se não forem coprimos, escolher próximo primo até encontrar
        candidate = 3
        while candidate < phi:
            if mdc(candidate, phi) == 1:
                e = candidate
                break
            candidate = next_prime(candidate + 1)

    d = inverso_modular(e, phi)

    return (n, e), (n, d)


def encrypt(mensagem: int, public_key: Tuple[int, int]) -> int:
    """Encripta uma mensagem usando a chave pública RSA.Insira um inteiro para a mensagem, e um tuplo para a chave pública (ex: (3233, 17)). Atenção: mensagem deve ser > 0 e < n."""
    if not isinstance(mensagem, int):
        raise TypeError("encrypt: mensagem deve ser um inteiro.")
    if not isinstance(public_key, tuple) or len(public_key) != 2:
        raise TypeError("encrypt: chave pública deve ser um tuplo (n, e).")
    n, e = public_key
    if not isinstance(n, int) or not isinstance(e, int):
        raise TypeError("encrypt: chave pública deve conter inteiros.")
    if not (0 < mensagem < n):
        raise ValueError("encrypt: mensagem deve estar entre 1 e n-1.")

    n, e = public_key
    if not (0 < mensagem < n):
        raise ValueError("Mensagem deve ser maior que 0 e menor que n")
    return pow(mensagem, e, n)


def decrypt(cifra: int, private_key: Tuple[int, int]) -> int:
    """Desencripta uma mensagem usando a chave privada RSA.  Insira um inteiro para a cifra e um tuplo para a chave privada (ex: (3233, 2753))."""
    if not isinstance(cifra, int):
        raise TypeError("decrypt: cifra deve ser um inteiro.")
    if not isinstance(private_key, tuple) or len(private_key) != 2:
        raise TypeError("decrypt: chave privada deve ser um tuplo (n, d).")
    n, d = private_key
    if not isinstance(n, int) or not isinstance(d, int):
        raise TypeError("decrypt: chave privada deve conter inteiros.")


    n, d = private_key
    return pow(cifra, d, n)


def _worker_factor(n: int, start: int, step: int, found: Value, stop_event: Event):
    limite = int(math.isqrt(n)) + 1
    for i in range(start, limite, step):
        if stop_event.is_set():
            return
        if n % i == 0:
            with found.get_lock():
                found.value = i
            stop_event.set()
            return


def crack_key(n: int, e: int, timeout: int = 15) -> Tuple[int, int]:
    """
        Tenta fatorar n para obter a chave privada a partir da chave pública (n, e). Insira o valor de n e e da chave pública.
        Timeout é opcional (em segundos). O "e" tem de ser menor que n!! (pode testar por exemplo n=143, e=7)"""


    if not isinstance(n, int) or n <= 1:
        raise ValueError("O valor de n deve ser um inteiro maior que 1.")
    if not isinstance(e, int) or e <= 0:
        raise ValueError("O valor de e deve ser um inteiro positivo.")
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ValueError("Timeout deve ser um número positivo.")

    found = Value('q', 0)
    stop_event = Event()

    n_processes = 4
    step = 2 * n_processes  # apenas números ímpares

    procs = []
    for i in range(n_processes):
        start = 3 + 2 * i
        p = Process(target=_worker_factor, args=(n, start, step, found, stop_event))
        p.start()
        procs.append(p)

    start_time = time.time()
    while time.time() - start_time < timeout and not stop_event.is_set():
        time.sleep(0.1)

    stop_event.set()
    for p in procs:
        p.join()

    if found.value == 0:
        raise TimeoutError("Fatoração não concluída no tempo limite")

    p = found.value
    q = n // p
    phi = (p - 1) * (q - 1)
    d = inverso_modular(e, phi)

    # Verificação simples
    test_msg = 42
    if decrypt(encrypt(test_msg, (n, e)), (n, d)) != test_msg:
        raise ValueError("Chave privada inválida após fatoração")

    return n, d

""""""""""""""""""""""""""""""""

if __name__ == "__main__":
    print("### Testes simples de criptografia e quebra ###\n")

    # Testar generate_keys
    print("generate_keys:")
    pub1, priv1 = generate_keys(16)
    pub2, priv2 = generate_keys(16)
    print(f"  Chave pública 1: {pub1}, privada 1: {priv1}")
    print(f"  Chave pública 2: {pub2}, privada 2: {priv2}\n")

    # Testar encrypt e decrypt
    print("encrypt e decrypt:")
    mensagem1 = 42
    mensagem2 = 99
    cifra1 = encrypt(mensagem1, pub1)
    decifrada1 = decrypt(cifra1, priv1)
    cifra2 = encrypt(mensagem2, pub2)
    decifrada2 = decrypt(cifra2, priv2)
    print(f"  Mensagem: {mensagem1} -> Cifra: {cifra1} -> Decifrada: {decifrada1}")
    print(f"  Mensagem: {mensagem2} -> Cifra: {cifra2} -> Decifrada: {decifrada2}\n")

    # Testar crack_key
    print("crack_key (tentativa de quebra da chave):")
    # Vamos usar uma chave pequena para conseguir quebrar rapidamente
    pub3, priv3 = generate_keys(16)
    n3, e3 = pub3
    print(f"  Chave pública a quebrar: {pub3}")
    try:
        cracked_n, cracked_d = crack_key(n3, e3, timeout=10)
        print(f"  Quebra bem-sucedida! Chave privada recuperada: (n={cracked_n}, d={cracked_d})")
    except TimeoutError:
        print("  Tempo limite excedido na quebra da chave.")
    print()

    print("### Fim dos testes ###")
