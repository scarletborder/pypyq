import asyncio
import grpc
import idl.exlang as exlang
import idl.exlang_pb2 as pb2
import idl.exlang_pb2_grpc as pb2g
import grpclib.client


async def func():
    channel = grpc.insecure_channel("127.0.0.1:28966")
    stub = pb2g.ExlangProgramerStub(channel)
    resp = stub.PyPro(pb2.ExlangRequest(code="print(10)"))
    print(resp)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(func())
