from gsuid_core.sv import SV
from gsuid_core.bot import Bot
from gsuid_core.models import Event

from .core import get_server_status, format_status
from .config import load_aliases, save_aliases

# 直接像 GsJrys 那样定义服务，去掉所有的 Plugins 注册代码
sv_mc = SV('MC状态查询')

# 使用 on_command 并且加上 block=True 拦截消息
@sv_mc.on_command('mc', block=True)
async def handle_mc_status(bot: Bot, ev: Event):
    # ev.text 会自动去除前面的指令 'mc'
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
            "2. mc add <别名> <地址> - 添加别名\n"
            "   示例：mc add name1 mc.frp.example:3544\n"
            "3. mc del <别名> - 删除别名\n"
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

    else:
        # 如果不是上面三个特殊指令，就当作是在查询服务器
        aliases = load_aliases()
        target_address = aliases.get(cmd, cmd)
        
        status, err = await get_server_status(target_address)

        if status:
            msg = format_status(status)
            await bot.send(msg)
        else:
            await bot.send(f"无法连接到服务器：{err}")