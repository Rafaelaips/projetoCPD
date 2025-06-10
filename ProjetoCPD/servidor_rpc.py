import asyncio
import websockets
import json
import inspect
import calculo
import criptografia

PORT = 8000
HOST = 'localhost'

def get_public_functions(modulos):
    funcoes = {}
    funcoes_excluir = {"candidate_generator", "worker_dynamic"}
    for modulo in modulos:
        for nome, func in inspect.getmembers(modulo, inspect.isfunction):
            if not nome.startswith("_") and nome not in funcoes_excluir:
                funcoes[nome] = func
    return funcoes

FUNCOES = get_public_functions([calculo, criptografia])

def list_functions():
    lista = []
    for nome, func in FUNCOES.items():
        assinatura = inspect.signature(func)
        parametros = list(assinatura.parameters.keys())
        doc = inspect.getdoc(func) or "Sem descrição."
        lista.append({
            "name": nome,
            "args": parametros,
            "description": doc
        })
    return lista

def criar_resposta(id_, result=None, error=None):
    resp = {
        "jsonrpc": "2.0",
        "id": id_
    }
    if error is not None:
        resp["error"] = error
    else:
        resp["result"] = result
    return resp


async def tratar_cliente(websocket):
    async for message in websocket:
        try:
            pedido = json.loads(message)

            # Suporte a batch
            if isinstance(pedido, list):
                respostas = []
                for req in pedido:
                    resp = await processar_pedido(req)
                    respostas.append(resp)
                await websocket.send(json.dumps(respostas))
            else:
                resposta = await processar_pedido(pedido)
                await websocket.send(json.dumps(resposta))

        except Exception as e:
            # Resposta de erro genérica para pedido inválido
            erro = {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32700,
                    "message": "Parse error"
                },
                "id": None
            }
            await websocket.send(json.dumps(erro))

async def processar_pedido(pedido):
    jsonrpc = pedido.get("jsonrpc")
    method = pedido.get("method")
    params = pedido.get("params", [])
    id_ = pedido.get("id")

    if jsonrpc != "2.0" or not method:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32600, "message": "Invalid Request"},
            "id": id_
        }

    try:
        if method == "list_functions":
            resultado = list_functions()
        elif method in FUNCOES:
            # Suporta params como dict ou lista
            if isinstance(params, dict):
                resultado = FUNCOES[method](**params)
            else:
                resultado = FUNCOES[method](*params)
        else:
            return {
                "jsonrpc": "2.0",
                "error": {"code": -32601, "message": "Method not found"},
                "id": id_
            }

        if isinstance(resultado, (tuple, list)):
            resultado = list(resultado)

        return {
            "jsonrpc": "2.0",
            "result": resultado,
            "id": id_
        }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)},
            "id": id_
        }


async def main():
    print(f"Servidor WebSocket a escutar em ws://{HOST}:{PORT}")
    async with websockets.serve(tratar_cliente, HOST, PORT):
        await asyncio.Future()  # roda para sempre

if __name__ == "__main__":
    asyncio.run(main())
