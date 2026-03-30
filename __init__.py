import asyncio
from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from .core import get_server_status, format_status
from .config import load_aliases, save_aliases

sv_mc = SV('MC状态查询')

@sv_mc.on_command('mc', block=True)
async def handle_mc_status(bot: Bot, ev: Event):
    text = ev.text.strip()
    
    if not text:
        return await bot.send('请输入服务器地址或别名！使用 mc help 查看帮助。')

    args = text.split()
    cmd = args[0]

    if cmd == 'help':
        help_text = (
            "GsMcStatus 帮助：\n"
            "1. mc <地址/别名> - 查询状态\n"
            "   示例：mc mc.frp.example:3544\n"
            "2. mc ls - 查看所有已保存别名的服务器状态\n"
            "3. mc add <别名> <地址> - 添加别名\n"
            "   示例：mc add name1 mc.frp.example:3544\n"
            "4. mc del <别名> - 删除别名\n"
            "   示例：mc del name1"
        )
        return await bot.send(help_text)

    elif cmd == 'add':
        if len(args) < 3:
            return await bot.send('参数不足！示例：mc add <别名> <地址>')
        alias_name = args[1]
        address = args[2]
        aliases = load_aliases()
        aliases[alias_name] = address
        save_aliases(aliases)
        return await bot.send(f'已成功添加别名：{alias_name} -> {address}')

    elif cmd == 'del':
        if len(args) < 2:
            return await bot.send('参数不足！示例：mc del <别名>')
        alias_name = args[1]
        aliases = load_aliases()
        if alias_name in aliases:
            del aliases[alias_name]
            save_aliases(aliases)
            return await bot.send(f'已成功删除别名：{alias_name}')
        else:
            return await bot.send(f'未找到别名：{alias_name}')

    elif cmd == 'ls':
        aliases = load_aliases()
        if not aliases:
            return await bot.send('当前没有配置任何服务器别名！请使用 mc add <别名> <地址> 添加。')

        # 封装一下用于并发的内部函数
        async def fetch_alias(alias_name, addr):
            status, _, _ = await get_server_status(addr)
            return alias_name, status
            
        # 并发获取所有服务器状态，极大提高 ls 速度
        tasks = [fetch_alias(k, v) for k, v in aliases.items()]
        results = await asyncio.gather(*tasks)
        
        # 按照在线人数从高到低排序，连不上的放到最后
        def sort_key(item):
            status = item[1]
            return status.players.online if status else -1
            
        results.sort(key=sort_key, reverse=True)
        
        info = "服务器状态列表\n----------------"
        for alias_name, status in results:
            if status:
                info_text = f"{status.latency:.1f}ms {status.players.online}/{status.players.max}人在线"
            else:
                info_text = "无法连接或已离线"
            info += f"\n{alias_name}: {info_text}"
            
        return await bot.send(info)

    else:
        # 常规的单服状态查询
        aliases = load_aliases()
        
        # 检查输入的 cmd 是否存在于别名列表中
        is_alias = cmd in aliases
        target_address = aliases.get(cmd, cmd)
        
        status, query_players, err = await get_server_status(target_address)

        if status:
            # 如果是别名查询，传入 target_address 作为实际地址显示；否则不传入
            actual_addr_to_show = target_address if is_alias else None
            msg = format_status(status, query_players, actual_addr_to_show)
            await bot.send(msg)
        else:
            await bot.send(f"无法连接到服务器：{err}")