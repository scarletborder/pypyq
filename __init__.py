from nonebot import get_driver, on_command, logger
from nonebot.plugin import PluginMetadata
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.params import CommandArg, ArgPlainText
from nonebot.adapters.onebot.v11 import Message, MessageSegment, MessageEvent

from plugins.pypyq.idl import CodePro_pb2 as pb2
from plugins.pypyq.idl import CodePro_pb2_grpc as pb2_grpc
import grpc

from .config import Config


__plugin_meta__ = PluginMetadata(
    name="pypyq",
    description="凭依绮编译并运行微服务",
    usage="/pyq (lang) - start code\n/",
    config=Config,
    type="MyUsage",
)

global_config = get_driver().config
config = Config.parse_obj(global_config)


async def isSU(event: MessageEvent):
    if str(event.user_id) in global_config.superusers:
        return True
    return False


pypyq = on_command("pyq", rule=to_me(), block=True)
pyqDis = on_command("pyqdis", rule=to_me(), permission=isSU, block=True)


@pypyq.handle()
async def pypyqfunc(state: T_State, args: Message = CommandArg()):
    # judge the language
    if lang := args.extract_plain_text():
        pass
    else:
        await pypyq.finish(
            Message(
                [MessageSegment.text("Please input your lang\ntype `exit` to exit.")]
            )
        )

    # all language is supported from pingyingqi 1.0.0_a1
    msgList: list[MessageSegment] = [
        MessageSegment.text("Now you can enjoy your " + lang)
    ]
    state["pyqLang"] = lang
    await pypyq.send(Message(msgList))


@pypyq.got("code")
async def pypycode(state: T_State, code: str = ArgPlainText()):
    if code == "exit":
        await pypyq.finish("service exited successfully")

    msgList: list[MessageSegment] = [MessageSegment.text("---凭依绮coding---\n")]
    lang = state.get("pyqLang", "scb")
    if lang == "scb":
        msgList.append(
            MessageSegment.text(
                "lang=nil\nERROR:Program language is initialized abruptly"
            )
        )
        await pypyq.finish(message=Message(msgList))
    else:
        channel = grpc.insecure_channel("127.0.0.1:28966")
        msgList.append(MessageSegment.text(f"lang={lang}\n"))
        stub = pb2_grpc.CodeProProgramerStub(channel)
        resp = stub.CodePro(pb2.CodeProRequest(code=code, lang=lang))

    # according to the code, output different info
    if resp.code == 3:
        msgList.append(
            MessageSegment.text(
                "WARNING:Your code compiled successfully but run too much time\n"
            )
        )
        msgList.append(MessageSegment.text(resp.data))
    elif resp.code == 2:
        msgList.append(
            MessageSegment.text(
                "ERROR:Your code contains some disabled package\n" + resp.data
            )
        )
    elif resp.code == 1:
        msgList.append(MessageSegment.text("ERROR:Program failed\n" + resp.data))

    elif resp.code == 0:
        msgList.append(MessageSegment.text(resp.data))
    else:
        msgList.append(MessageSegment.text("ERROR:Inner wrong\n" + resp.data))

    msgList.append(MessageSegment.text(resp.extra))
    await pypyq.finish(Message(msgList))


@pyqDis.handle()
async def pyqdisfunc(args: Message = CommandArg()):
    if lang := args.extract_plain_text():
        myList = lang.split(" ")
        if len(myList) < 2:
            await pyqDis.finish("too few args")
        data = ""
        if myList[0] == "enable":
            data += "0;"
        else:
            data += "1;"

        channel = grpc.insecure_channel("127.0.0.1:28966")
        stub = pb2_grpc.ExlangProgramerStub(channel)
        resp = stub.Dislike(pb2.DislikedPackage(pack=data + myList[1]))
        pass
    else:
        await pyqDis.finish("pack arg lost")
    if resp.code != 0:
        await pyqDis.finish("ERROR" + resp.data)
    else:
        await pyqDis.finish(resp.data)
