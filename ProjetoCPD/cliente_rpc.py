import asyncio
import websockets
import json
import ast

class RPCClientWS:
    def __init__(self, uri="ws://localhost:8000"):
        self.uri = uri
        self._next_id = 1

    def _get_id(self):
        # gera ids únicos para cada chamada
        id_ = self._next_id
        self._next_id += 1
        return id_

    async def invoke(self, method, params=None):
        id_ = self._get_id()
        pedido = {
            "jsonrpc": "2.0",
            "method": method,
            "id": id_
        }
        if params is not None:
            pedido["params"] = params

        async with websockets.connect(self.uri) as websocket:
            await websocket.send(json.dumps(pedido))
            resposta = await websocket.recv()
            resposta_json = json.loads(resposta)

            # Validação básica da resposta
            if resposta_json.get("id") != id_:
                raise Exception("ID da resposta não coincide com o pedido")

            if "result" in resposta_json:
                return resposta_json["result"]
            elif "error" in resposta_json:
                raise Exception(f"Erro remoto: {resposta_json['error']}")
            else:
                raise Exception("Resposta inválida do servidor.")

    async def menu_dinamico(self):
        funcoes = await self.invoke("list_functions")

        while True:
            print("\n=== Menu Dinâmico ===")
            for idx, f in enumerate(funcoes):
                nome = f.get("name", "<sem nome>")
                parametros = f.get("args", [])
                doc = f.get("description", "(sem descrição)")
                print(f"{idx + 1}. {nome} ({len(parametros)} arg(s)) - {doc}")
            print("0. Sair")

            escolha = input("Escolha uma função: ").strip()
            if escolha == "0":
                print("A terminar cliente.")
                break

            if not escolha.isdigit() or not (1 <= int(escolha) <= len(funcoes)):
                print("Opção inválida.")
                continue

            funcao = funcoes[int(escolha) - 1]
            nome = funcao.get("name")
            parametros = funcao.get("args", [])
            args = []

            if parametros == ["args"]:
                num = input("Quantos argumentos pretende fornecer? ").strip()
                if not num.isdigit() or int(num) <= 0:
                    print("Número inválido de argumentos.")
                    continue
                for i in range(int(num)):
                    val = input(f"Argumento {i + 1}: ")
                    try:
                        args.append(ast.literal_eval(val))
                    except Exception:
                        args.append(val)
                params = args  # Enviar como lista posicional
            else:
                params = {}
                for param in parametros:
                    val = input(f"Insira valor para argumento '{param}': ")
                    try:
                        valor_convertido = ast.literal_eval(val)
                    except Exception:
                        valor_convertido = val
                    params[param] = valor_convertido

            try:
                resultado = await self.invoke(nome, params)
                print("Resultado:", resultado)
            except Exception as e:
                print("Erro:", e)


if __name__ == "__main__":
    client = RPCClientWS()
    print("\n=== A iniciar cliente RPC (WebSocket) ===")
    asyncio.run(client.menu_dinamico())
