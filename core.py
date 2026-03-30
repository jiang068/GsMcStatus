from mcstatus import JavaServer
from mcstatus.responses import JavaStatusResponse

async def get_server_status(address: str):
    try:
        server = JavaServer.lookup(address)
        status = await server.async_status()
        return status, None
    except Exception as e:
        return None, str(e)

def format_status(status: JavaStatusResponse) -> str:
    # 提取 MOTD
    motd = "".join([i.strip(" ") for i in status.motd.parsed if isinstance(i, str)])
    spliter = "--------------------"
    
    info = f"{motd}\n{spliter}\n"
    info += f"版本：{status.version.name}\n"
    info += f"延迟：{status.latency:.1f}ms\n"
    info += f"在线人数：{status.players.online}/{status.players.max}"
    
    # 提取玩家列表
    player_list = [
        player.name
        for player in (status.players.sample or [])
        if player.id != "00000000-0000-0000-0000-000000000000"
    ]
    
    if player_list:
        info += f"\n成员：{', '.join(player_list)}"
        
    return info