from mcstatus import JavaServer
from mcstatus.responses import JavaStatusResponse

async def get_server_status(address: str):
    try:
        server = JavaServer.lookup(address)
        status = await server.async_status()
        
        query_players = []
        if status.players.online > 0 and not status.players.sample:
            try:
                query = await server.async_query()
                query_players = query.players.names
            except Exception:
                pass 
                
        return status, query_players, None
    except Exception as e:
        return None, [], str(e)

# 增加 actual_address 参数，默认为 None
def format_status(status: JavaStatusResponse, query_players: list, actual_address: str = None) -> str:
    motd = "".join([i.strip(" ") for i in status.motd.parsed if isinstance(i, str)])
    spliter = "--------------------"
    
    info = f"{motd}\n{spliter}\n"
    
    # 如果传入了真实地址（说明用了别名），则额外插入一行真实地址
    if actual_address:
        info += f"{actual_address}\n{spliter}\n"
        
    info += f"版本：{status.version.name}\n"
    info += f"延迟：{status.latency:.1f}ms\n"
    info += f"在线人数：{status.players.online}/{status.players.max}"
    
    if query_players:
        player_list = query_players
    else:
        player_list = [
            player.name
            for player in (status.players.sample or [])
            if player.id != "00000000-0000-0000-0000-000000000000"
        ]
    
    if player_list:
        show_ellipsis = len(player_list) > 5 or len(player_list) < status.players.online
        info += f"\n成员：{', '.join(player_list[:5])}{' ...' if show_ellipsis else ''}"
        
    return info