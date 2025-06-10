import unittest
from calculo import is_prime, find_max_prime_sequential, find_max_prime_parallel, find_next_twin_primes
from calculo import is_mersenne_prime, prime_factors, next_prime, previous_prime
from criptografia import generate_keys, encrypt, decrypt, crack_key
import time


class C1Test1IsPrime(unittest.TestCase):
    def test_is_prime_true(self):
        """Testa se números conhecidos como primos são corretamente identificados."""
        for n in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 104729]:  # Incluído primo grande
            with self.subTest(n=n):
                self.assertTrue(is_prime(n))

    def test_is_prime_false(self):
        """Testa se números compostos e triviais são corretamente rejeitados."""
        for n in [0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 100, 104730]:  # Incluído composto grande
            with self.subTest(n=n):
                self.assertFalse(is_prime(n))

    def test_is_prime_edge_cases(self):
        """Testa números negativos e limites inferiores."""
        self.assertFalse(is_prime(-7))
        self.assertFalse(is_prime(0))
        self.assertFalse(is_prime(1))


class C1Test2FindMaxPrimeSequential(unittest.TestCase):
    def test_return_type_and_is_prime(self):
        """Garante que a função retorna um número primo inteiro válido."""
        prime = find_max_prime_sequential(1)
        self.assertIsInstance(prime, int)
        self.assertTrue(is_prime(prime))

    def test_timeout_zero_returns_initial_prime(self):
        """Se o tempo for 0, a função deve devolver o valor inicial assumido (2)."""
        prime = find_max_prime_sequential(0)
        self.assertEqual(prime, 2)

    def test_short_timeout_returns_two(self):
        """Timeout muito pequeno ainda deve devolver 2 como valor mínimo aceitável."""
        prime = find_max_prime_sequential(1)
        self.assertGreaterEqual(prime, 2)
        self.assertTrue(is_prime(prime))

    def test_larger_timeout_returns_bigger_prime(self):
        """Com mais tempo, espera-se obter um primo maior que 2."""
        prime = find_max_prime_sequential(3)
        self.assertTrue(is_prime(prime))
        self.assertGreaterEqual(prime, 2)

    def test_monotonicity(self):
        """Com mais tempo de execução, o maior primo encontrado não deve ser menor."""
        prime1 = find_max_prime_sequential(1)
        prime2 = find_max_prime_sequential(3)
        self.assertGreaterEqual(prime2, prime1)


class C1Test3ComparacaoSequencialParalelo(unittest.TestCase):
    def test_algoritmo_paralelo_tem_mais_digitos(self):
        """Garante que em todas as execuções o paralelo encontra primos com mais ou iguais dígitos que o sequencial."""
        timeout = 3
        for _ in range(3):
            p_seq = find_max_prime_sequential(timeout)
            p_par = find_max_prime_parallel(timeout)

            d_seq = len(str(p_seq))
            d_par = len(str(p_par))

            print(f"Seq: {p_seq} ({d_seq} dígitos), Par: {p_par} ({d_par} dígitos)")
            self.assertGreaterEqual(d_par, d_seq)

    def test_mais_tempo_gera_primos_maiores(self):
        """Compara a média de dígitos de primos obtidos em 5s vs 10s na versão paralela."""
        resultados_5s = [find_max_prime_parallel(5) for _ in range(3)]
        resultados_10s = [find_max_prime_parallel(10) for _ in range(3)]

        media_5s = sum(len(str(p)) for p in resultados_5s) / 3
        media_10s = sum(len(str(p)) for p in resultados_10s) / 3

        print(f"Média dígitos (5s): {media_5s:.2f}")
        print(f"Média dígitos (10s): {media_10s:.2f}")

        self.assertGreater(media_10s, media_5s)

    def test_paralelo_aumenta_digitos_em_relacao_ao_sequencial(self):
        """Verifica se o paralelo encontra, em média, mais dígitos que o sequencial em 10s."""
        timeout = 10
        n_execucoes = 3

        digitos_seq = []
        digitos_par = []

        for _ in range(n_execucoes):
            p_seq = find_max_prime_sequential(timeout)
            p_par = find_max_prime_parallel(timeout)

            digitos_seq.append(len(str(p_seq)))
            digitos_par.append(len(str(p_par)))

        media_seq = sum(digitos_seq) / n_execucoes
        media_par = sum(digitos_par) / n_execucoes

        print(f"Média dígitos (seq, 10s): {media_seq:.2f}")
        print(f"Média dígitos (par, 10s): {media_par:.2f}")

        self.assertGreaterEqual(media_par, 1.25 * media_seq)
        self.assertGreaterEqual(media_par, 1.5 * media_seq)
        self.assertGreaterEqual(media_par, 1.75 * media_seq)
        self.assertGreaterEqual(media_par, 2 * media_seq)
        self.assertGreaterEqual(media_par, 2.25 * media_seq)

    def test_tempo_execucao_respeita_timeout(self):
        """Garante que ambas as funções terminam aproximadamente no timeout definido (±0.5s)."""
        timeout = 5
        margem = 0.5

        inicio_seq = time.perf_counter()
        find_max_prime_sequential(timeout)
        duracao_seq = time.perf_counter() - inicio_seq

        inicio_par = time.perf_counter()
        find_max_prime_parallel(timeout)
        duracao_par = time.perf_counter() - inicio_par

        print(f"Tempo seq: {duracao_seq:.2f}s")
        print(f"Tempo par: {duracao_par:.2f}s")

        self.assertAlmostEqual(duracao_seq, timeout, delta=margem)
        self.assertAlmostEqual(duracao_par, timeout, delta=margem)


class C1Test4FindNextTwinPrimes(unittest.TestCase):
    def test_pares_conhecidos(self):
        """Testa alguns pares de primos gémeos conhecidos."""
        self.assertEqual(find_next_twin_primes(10), (11, 13))
        self.assertEqual(find_next_twin_primes(14), (17, 19))
        self.assertEqual(find_next_twin_primes(100), (101, 103))
        self.assertEqual(find_next_twin_primes(1000), (1019, 1021))

    def test_com_inicio_negativo(self):
        """Testa que funciona corretamente com entrada negativa."""
        self.assertEqual(find_next_twin_primes(-5), (3, 5))

    def test_entre_gemeos(self):
        """Testa comportamento quando n está entre dois primos gémeos."""
        self.assertEqual(find_next_twin_primes(12), (17, 19))

    def test_numero_que_eh_primeiro_gemeo(self):
        """Testa comportamento quando n é o primeiro número de um par gémeo."""
        self.assertEqual(find_next_twin_primes(11), (17, 19))


class C1Test5IsMersennePrime(unittest.TestCase):
    def test_large_prime_not_mersenne(self):
        """Testa um número primo grande que não é de Mersenne."""
        self.assertFalse(is_mersenne_prime(104729))  # Primo, mas não 2^p - 1

    def test_mersenne_primes(self):
        """Testa números que são conhecidos primos de Mersenne."""
        self.assertTrue(is_mersenne_prime(3))    # 2^2 - 1
        self.assertTrue(is_mersenne_prime(7))    # 2^3 - 1
        self.assertTrue(is_mersenne_prime(31))   # 2^5 - 1
        self.assertTrue(is_mersenne_prime(127))  # 2^7 - 1

    def test_non_mersenne_numbers(self):
        """Testa números que não são primos de Mersenne."""
        self.assertFalse(is_mersenne_prime(15))    # 2^4 - 1, mas não primo
        self.assertFalse(is_mersenne_prime(2047))  # 2^11 - 1, mas não primo
        self.assertFalse(is_mersenne_prime(20))    # 21 não é potência de 2
        self.assertFalse(is_mersenne_prime(2))     # Não é da forma 2^p - 1

    def test_large_mersenne_prime(self):
        """Testa um primo de Mersenne maior conhecido (2^13 - 1 = 8191)."""
        self.assertTrue(is_mersenne_prime(8191))


class C1Test6PrimeFactors(unittest.TestCase):

    def test_fatores_comuns(self):
        """Testa decomposição de números com fatores repetidos e distintos."""
        self.assertEqual(prime_factors(60), [2, 2, 3, 5])
        self.assertEqual(prime_factors(84), [2, 2, 3, 7])
        self.assertEqual(prime_factors(210), [2, 3, 5, 7])

    def test_numeros_primos(self):
        """Testa que um número primo devolve apenas ele próprio."""
        self.assertEqual(prime_factors(17), [17])
        self.assertEqual(prime_factors(97), [97])

    def test_potencias_de_primos(self):
        """Testa potências de primos como 2^n ou 3^n."""
        self.assertEqual(prime_factors(8), [2, 2, 2])
        self.assertEqual(prime_factors(27), [3, 3, 3])
        self.assertEqual(prime_factors(625), [5, 5, 5, 5])

    def test_fatores_grandes(self):
        """Testa número com fator primo grande no fim."""
        self.assertEqual(prime_factors(2 * 3 * 101), [2, 3, 101])

    def test_um_e_zero(self):
        """Testa entrada com 0 e 1."""
        self.assertEqual(prime_factors(1), [])
        self.assertEqual(prime_factors(0), [])

    def test_negativos(self):
        """Testa que números negativos devolvem os fatores do valor absoluto."""
        self.assertEqual(prime_factors(-60), [2, 2, 3, 5])


class C1Test7NextPrime(unittest.TestCase):

    def test_apos_primos_pequenos(self):
        """Testa os primos imediatamente a seguir a valores pequenos."""
        self.assertEqual(next_prime(2), 3)
        self.assertEqual(next_prime(3), 5)
        self.assertEqual(next_prime(5), 7)

    def test_valores_medios(self):
        """Testa próximos primos para valores médios."""
        self.assertEqual(next_prime(17), 19)
        self.assertEqual(next_prime(24), 29)
        self.assertEqual(next_prime(89), 97)

    def test_valores_nao_primos(self):
        """Testa entradas que não são primos."""
        self.assertEqual(next_prime(0), 2)
        self.assertEqual(next_prime(1), 2)
        self.assertEqual(next_prime(100), 101)

    def test_grande_valor(self):
        """Testa próximo primo para número maior."""
        self.assertEqual(next_prime(1000), 1009)


class C1Test8PreviousPrime(unittest.TestCase):

    def test_valores_comuns(self):
        """Testa o primo anterior para valores típicos."""
        self.assertEqual(previous_prime(17), 13)
        self.assertEqual(previous_prime(10), 7)
        self.assertEqual(previous_prime(5), 3)

    def test_limites_inferiores(self):
        """Testa comportamento para limites onde não há primo anterior."""
        self.assertIsNone(previous_prime(2))
        self.assertIsNone(previous_prime(1))
        self.assertIsNone(previous_prime(0))
        self.assertIsNone(previous_prime(-5))

    def test_valor_exato_primo(self):
        """Testa que devolve o primo anterior mesmo quando n é primo."""
        self.assertEqual(previous_prime(19), 17)
        self.assertEqual(previous_prime(3), 2)


class C2Test1GenerateKeysBits(unittest.TestCase):

    def test_chaves_8_bits(self):
        """Testa geração e funcionamento com chaves de 8 bits."""
        pub, priv = generate_keys(8)
        self._verifica_chaves(pub, priv, bits=8)

    def test_chaves_16_bits(self):
        """Testa geração e funcionamento com chaves de 16 bits."""
        pub, priv = generate_keys(16)
        self._verifica_chaves(pub, priv, bits=16)

    def test_chaves_32_bits(self):
        """Testa geração e funcionamento com chaves de 32 bits."""
        pub, priv = generate_keys(32)
        self._verifica_chaves(pub, priv, bits=32)

    def test_chaves_64_bits(self):
        """Testa geração e funcionamento com chaves de 64 bits."""
        pub, priv = generate_keys(64)
        self._verifica_chaves(pub, priv, bits=64)

    def _verifica_chaves(self, pub, priv, bits=16):
        """
        Testa se m = decrypt(encrypt(m)) com chaves fornecidas
        e se n tem pelo menos (bits - 1) bits.
        """
        n, e = pub
        _, d = priv
        m = 42
        c = pow(m, e, n)
        m2 = pow(c, d, n)
        self.assertEqual(m, m2)
        self.assertGreaterEqual(n.bit_length(), bits - 1)


class C2Test2Encrypt(unittest.TestCase):

    def setUp(self):
        """Gerar um par de chaves pequeno para usar nos testes."""
        self.pub, self.priv = generate_keys(16)

    def test_encriptacao_valida(self):
        """Verifica que encrypt funciona com uma mensagem válida."""
        m = 42
        c = encrypt(m, self.pub)
        self.assertIsInstance(c, int)
        self.assertNotEqual(c, m)  # deve mudar a mensagem
        # Desencripta para garantir reversibilidade
        n, d = self.priv
        m2 = pow(c, d, n)
        self.assertEqual(m, m2)

    def test_mensagem_zero(self):
        """Mensagem igual a zero deve causar erro."""
        with self.assertRaises(ValueError):
            encrypt(0, self.pub)

    def test_mensagem_negativa(self):
        """Mensagem negativa não é permitida."""
        with self.assertRaises(ValueError):
            encrypt(-5, self.pub)

    def test_mensagem_maior_que_n(self):
        """Mensagem >= n não pode ser encriptada."""
        n, _ = self.pub
        with self.assertRaises(ValueError):
            encrypt(n, self.pub)
        with self.assertRaises(ValueError):
            encrypt(n + 1, self.pub)


class C2Test3DecryptBits(unittest.TestCase):

    def _test_com_bits(self, bits):
        """Gera chaves com N bits, encripta e desencripta uma mensagem."""
        pub, priv = generate_keys(bits)
        n, e = pub
        _, d = priv
        m = 42
        c = encrypt(m, (n, e))
        m2 = decrypt(c, (n, d))
        self.assertEqual(m, m2)
        self.assertGreaterEqual(n.bit_length(), bits - 1)

    def test_8_bits(self):
        """Testa encriptação e desencriptação com chave de 8 bits."""
        self._test_com_bits(8)

    def test_16_bits(self):
        """Testa encriptação e desencriptação com chave de 16 bits."""
        self._test_com_bits(16)

    def test_32_bits(self):
        """Testa encriptação e desencriptação com chave de 32 bits."""
        self._test_com_bits(32)

    def test_64_bits(self):
        """Testa encriptação e desencriptação com chave de 64 bits."""
        self._test_com_bits(64)


class C2Test4CrackKey(unittest.TestCase):

    def test_crack_key_timeout(self):
        """
                Testa se a função crack_key eleva a exceção TimeoutError quando o tempo
                limite definido é muito curto para fatorar a chave. Este teste verifica
                o tratamento de timeouts pela função.
                """
        public_key, _ = generate_keys(64)
        n, e = public_key
        with self.assertRaises(TimeoutError):
            crack_key(n, e, timeout=1)

    def test_crack_difficult_n(self):
        """
                Testa o comportamento da função crack_key com um valor de 'n' que é primo
                (e, portanto, não pode ser fatorado em dois primos) ou que teria fatores
                muito grandes para serem encontrados rapidamente. Este teste verifica o
                tratamento de casos onde a fatoração é improvável de sucesso dentro do timeout.
                """
        # n é um primo grande (improvável de fatorar rapidamente)
        n = 281474976710677  # Um primo
        e = 65537
        with self.assertRaises(TimeoutError):
            crack_key(n, e, timeout=5)

    def test_crack_medium_key(self):
        """
                Testa se a função crack_key consegue fatorar uma chave RSA de tamanho médio
                dentro de um limite de tempo mais extenso. Este teste visa verificar o
                comportamento para casos um pouco mais realistas, mas ainda tratáveis em teste.
                """
        public_key, _ = generate_keys(32)
        n, e = public_key
        start_time = time.time()
        cracked_n, cracked_d = crack_key(n, e, timeout=60)
        end_time = time.time()
        self.assertEqual(n, cracked_n)
        self.assertIsNotNone(cracked_d)
        print(f"Teste de chave média levou {end_time - start_time:.2f} segundos.")

    def test_fatoracao_sucesso(self):
        """
        Testa se a função crack_key consegue fatorar corretamente uma chave RSA de 16 bits.
        """
        public, private = generate_keys(16)
        n, e = public
        n_crack, d_crack = crack_key(n, e, timeout=10)
        self.assertEqual(n_crack, n)
        self.assertEqual(d_crack, private[1])

    def test_respeito_timeout(self):
        """
        Testa se a função crack_key respeita o tempo limite ao tentar fatorar uma chave RSA de 64 bits.
        """
        public, _ = generate_keys(64)
        n, e = public
        start_time = time.time()
        with self.assertRaises(TimeoutError):
            crack_key(n, e, timeout=1)
        end_time = time.time()
        self.assertLessEqual(end_time - start_time, 2, "A função não respeitou o tempo limite.")

    def test_entrada_invalida(self):
        """
        Testa o comportamento da função crack_key com entradas inválidas.
        """
        with self.assertRaises(ValueError):
            crack_key(-15, 3, timeout=10)
        with self.assertRaises(ValueError):
            crack_key(0, 3, timeout=10)

    def test_consistencia_resultados(self):
        """
        Testa se a função crack_key retorna resultados consistentes para a mesma entrada.
        """
        public, private = generate_keys(16)
        n, e = public
        resultado1 = crack_key(n, e, timeout=10)
        resultado2 = crack_key(n, e, timeout=10)
        self.assertEqual(resultado1, resultado2)

    def test_desempenho_tempo_limite(self):
        """
        Testa se é possível quebrar uma chave RSA de 16 bits dentro de 5 segundos.
        """
        bits = 16
        time_limit = 5  # segundos
        public_key, private_key = generate_keys(bits)
        n, e = public_key

        start_time = time.time()
        try:
            n_crack, d_crack = crack_key(n, e, timeout=time_limit)
            end_time = time.time()
            elapsed_time = end_time - start_time

            self.assertEqual(n_crack, n, "O valor de n quebrado não corresponde ao original.")
            self.assertEqual(d_crack, private_key[1], "O valor de d quebrado não corresponde ao original.")
            self.assertLessEqual(elapsed_time, time_limit, "A quebra da chave excedeu o tempo limite.")
        except TimeoutError:
            self.fail(f"Não foi possível quebrar a chave de {bits} bits dentro de {time_limit} segundos.")

    def test_varios_tamanhos_chave(self):
        """
        Testa a função crack_key para diferentes tamanhos de chave e tempos limites.
        """
        tamanhos_chave = [16, 24, 32]   # bits
        tempos_limite = [5, 10, 15]     # segundos

        for bits, tempo in zip(tamanhos_chave, tempos_limite):
            with self.subTest(bits=bits, tempo=tempo):
                public_key, private_key = generate_keys(bits)
                n, e = public_key

                start_time = time.time()
                try:
                    n_crack, d_crack = crack_key(n, e, timeout=tempo)
                    end_time = time.time()
                    elapsed_time = end_time - start_time

                    self.assertEqual(n_crack, n,
                                     f"O valor de n quebrado não corresponde ao original para chave de {bits} bits.")
                    self.assertEqual(d_crack, private_key[1],
                                     f"O valor de d quebrado não corresponde ao original para chave de {bits} bits.")
                    self.assertLessEqual(elapsed_time, tempo, f"A quebra da chave de {bits} bits excedeu "
                                                              f"o tempo limite de {tempo} segundos.")
                except TimeoutError:
                    self.fail(f"Não foi possível quebrar a chave de {bits} bits dentro de {tempo} segundos.")


if __name__ == '__main__':
    unittest.main()
