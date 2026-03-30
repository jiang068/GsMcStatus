from mcstatus import JavaServer
from mcstatus.responses import JavaStatusResponse

async def get_server_status(address: str):
    try:
        server = JavaServer.lookup(address)
        status = await server.async_status()
        
        # 后备方案：如果有人在线但没拿到 sample 名单，尝试使用 Query 协议获取
        query_players = []
        if status.players.online > 0 and not status.players.sample:
            try:
                # 注意：这需要服务器在 server.properties 中开启 enable-query=true
                query = await server.async_query()
                query_players = query.players.names
            except Exception:
                pass # 如果没开 Query 或者报错，直接忽略
                
        return status, query_players, None
    except Exception as e:
        return None, [], str(e)

def format_status(status: JavaStatusResponse, query_players: list) -> str:
    # 提取 MOTD
    motd = "".join([i.strip(" ") for i in status.motd.parsed if isinstance(i, str)])
    spliter = "--------------------"
    
    info = f"{motd}\n{spliter}\n"
    info += f"版本：{status.version.name}\n"
    info += f"延迟：{status.latency:.1f}ms\n"
    info += f"在线人数：{status.players.online}/{status.players.max}"
    
    # 优先使用 query 获取到的完整名单，如果没有再用 ping 的 sample 名单
    if query_players:
        player_list = query_players
    else:
        player_list = [
            player.name
            for player in (status.players.sample or [])
            if player.id != "00000000-0000-0000-0000-000000000000"
        ]
    
    if player_list:
        # 仿照原版插件，如果超过 5 个人，或者获取到的名单少于实际在线人数，加个省略号
        show_ellipsis = len(player_list) > 5 or len(player_list) < status.players.online
        info += f"\n成员：{', '.join(player_list[:5])}{' ...' if show_ellipsis else ''}"
        
    return info