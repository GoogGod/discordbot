import time
from datetime import datetime
from random import choice

import disnake
import requests
from disnake import FFmpegPCMAudio, PCMVolumeTransformer
from disnake.ext import commands
from disnake.utils import get
from flask import request
from youtube_dl import YoutubeDL

from background import keep_alive
from config import (
    ACTIVE,
    ALLOWED_CHANNELS,
    BOTICON_URL,
    GUILD_ID,
    SERVERICON_URL,
    TOKEN,
)

bot = commands.Bot(command_prefix='/', help_command=None,
                   intents=disnake.Intents.all(), test_guilds=GUILD_ID)
queue = []

# class TicTakToe(disnake.ui.View):

#  def __init__(self):
#    super().__init__(timeout=60)
#    self.value = str

#  @disnake.ui.button(emoji="⭕", style=disnake.ButtonStyle.blurple)
#  async def nolik(self, button: disnake.ui.Button, interaction: disnake.CommandInteraction):
#    self.value = "⭕"
#    self.stop()


#  @disnake.ui.button(emoji="❌", style=disnake.ButtonStyle.blurple)
#  async def krestik(self, button: disnake.ui.Button, interaction: disnake.CcommandInteraction):
#    self.value = "❌"
#    self.stop()

#  @disnake.ui.button(emoji="🟦", style=disnake.ButtonStyle.blurple)
#  async def empty(self, button: disnake.ui.Button, interaction: disnake.CcommandInteraction):
#    self.value = "🟦"
#    self.stop()

@bot.event
async def on_ready():
    print(f'[{time.asctime(time.localtime(time.time()))}] BOT {
          bot.user} is ready to assist you!')
    await bot.change_presence(status=disnake.Status.online, activity=disnake.Game(name='Участвует в жизни сервера', platform='Discord'))


@bot.event
async def on_slash_command_error(inter, error):
    print(error)
    smile = choice(['⚡', '🚀', '⏱️', '🔥', '🏃', '🏎️', '🏍️', '💯🔥', '😎', '🎉'])
    if isinstance(error, commands.CommandOnCooldown):
        await inter.response.send_message(ephemeral=True, embed=disnake.Embed(title=f"Вы слишком быстрый! {smile}", description=f"Подождите ещё {int(error.cooldown.get_retry_after())} секунд до следуйщей отправки!", color=0xFF0000), delete_after=5)
    elif isinstance(error, commands.MissingPermissions):
        await inter.response.send_message(ephemeral=True, embed=disnake.Embed(title="У Вас нет разрешения на использование этой команды!", color=0xFF0000))
    elif isinstance(error, commands.ChannelNotReadable):
        await inter.response.send_message(ephemeral=True, embed=disnake.Embed(title="У Вас нет разрешения на использование команд в этом чате!", color=0xFF0000))


@bot.slash_command(default_member_permission=disnake.Permissions.use_application_commands,
                   description="Выводит ожидание между клиентом и сервером",
                   dm_permission=False,
                   name="gf_ping")
@commands.cooldown(1, 20, type=commands.BucketType.default)
async def ping(inter, arg: str = "both"):

    if inter.channel.id not in ALLOWED_CHANNELS:
        raise commands.ChannelNotReadable(inter.channel)

    match arg:
        case 'both':
            t = time.time()
            embedExample = disnake.Embed(
                title="Pong! Ожидание между клиентом и сервером...")
            tempMessage = await inter.channel.send(embed=embedExample)
            ping = round(((time.time() - t) * 1000), 0)
            await tempMessage.delete()
            embedExample = disnake.Embed(
                title=':ping_pong: PONG!', color=0x7FFF00)
            embedExample.set_footer(
                text="Проблемы со стороны Discord могут вызвать странную или высокую задержку",
                icon_url=SERVERICON_URL)
            embedExample.add_field(
                name="**Ответ сервера:**", value=f"```{int(bot.latency * 1000)} ms```")
            embedExample.add_field(
                name="**Проверка сообщением:**", value=f"```{int(ping)} ms```")
            await inter.response.send_message(embed=embedExample, delete_after=5)
            return
        case 'message':
            t = time.time()
            embedExample = disnake.Embed(
                title="Pong! Ожидание между клиентом и сервером...")
            tempMessage = await inter.channel.send(embed=embedExample)
            ping = round(((time.time() - t) * 1000), 0)
            await tempMessage.delete()
            embedExample = disnake.Embed(
                title=':ping_pong: PONG!', color=0x7FFF00)
            embedExample.set_footer(
                text="Проблемы со стороны Discord могут вызвать странную или высокую задержку",
                icon_url=SERVERICON_URL)
            embedExample.add_field(
                name="**Проверка сообщением:**", value=f"```{int(ping)} ms```")
            await inter.response.send_message(embed=embedExample, delete_after=5)
            return
        case 'latency':
            embedExample = disnake.Embed(
                title=':ping_pong: PONG!', color=0x7FFF00)
            embedExample.set_footer(
                text="Проблемы со стороны Discord могут вызвать странную или высокую задержку",
                icon_url=SERVERICON_URL)
            embedExample.add_field(
                name="**Ответ сервера:**", value=f"```{int(bot.latency * 1000)} ms```", inline=True)
            tempMessage = await inter.response.send_message(embed=embedExample, delete_after=5)
            return

    await inter.response.send_message(ephemeral=True, embed=disnake.Embed(title="{0} is not a valid argument!".format(arg), color=0xFF0000), delete_after=7)
    await inter.message.delete()


@bot.slash_command(default_member_permission=disnake.Permissions.use_application_commands,
                   description="Присоединяет бота к вашей голосовой комнате",
                   dm_permission=False,
                   name="gf_join")
@commands.cooldown(1, 20, type=commands.BucketType.default)
async def gf_join(inter):

    if inter.channel.id not in ALLOWED_CHANNELS:
        raise commands.ChannelNotReadable(inter.channel)

    if (inter.author.voice):
        if not (inter.guild.voice_client):
            await inter.author.voice.channel.connect()
            await inter.response.send_message(embed=disnake.Embed(
                title="Бот был подключен к голосовому каналу!", color=0x7FFF00))
        else:
            await inter.response.send_message(ephemeral=True, embed=disnake.Embed(
                title="Бот уже находится в голосовом канале!", color=0xFF0000))
    else:
        await inter.response.send_message(ephemeral=True, embed=disnake.Embed(
            title="Вы не в голосовом канале!", color=0xFF0000))


@bot.slash_command(default_member_permission=disnake.Permissions.use_application_commands,
                   description="Выбрасывает бота из вашей голосовой комнаты",
                   dm_permission=False,
                   name="gf_disconnect")
@commands.cooldown(1, 20, type=commands.BucketType.default)
async def gf_disconnect(inter, force: bool = False):

    if inter.channel.id not in ALLOWED_CHANNELS:
        raise commands.ChannelNotReadable(inter.channel)

    if (inter.guild.voice_client):
        if (force or inter.author.voice):
            await inter.guild.voice_client.disconnect()
            await inter.response.send_message(embed=disnake.Embed(
                title="Бот был отключен от голосового канала!", color=0x7FFF00))
        else:
            await inter.response.send_message(ephemeral=True, embed=disnake.Embed(
                title="Вы не в голосовом канале с ботом!", color=0xFF0000))
    else:
        await inter.response.send_message(ephemeral=True, embed=disnake.Embed(
            title="Бот не находится в голосовом канале!", color=0xFF0000))


@bot.slash_command(default_member_permission=disnake.Permissions.use_application_commands,
                   description="Выводит время до Нового года!",
                   dm_permission=True,
                   name="gf_remtime")
@commands.cooldown(1, 20, type=commands.BucketType.default)
async def gf_RemainingTime(inter, short: bool = True):

    if inter.channel.id not in ALLOWED_CHANNELS:
        raise commands.ChannelNotReadable(inter.channel)

    if (short):
        await inter.response.send_message(embed=disnake.Embed(title="🧑‍🎄 Новый год наступет <t:1735696080:R>! 🎉", color=0x87CEEB))
    if not short:
        embed = disnake.Embed(title="🧑‍🎄 Новый год!", color=0x87CEEB)
        embed.add_field(name="**Наступит через:**",
                        value="<t:1735696080:R>", inline=True)
        embed.add_field(name="**Отсчёт до:**",
                        value="<t:1735696080:F>", inline=True)
        await inter.response.send_message(embed=embed)


@bot.slash_command(default_member_permission=disnake.Permissions.use_application_commands,
                   description="Send Embed Message",
                   dm_permission=False,
                   name="gf_embed")
@commands.cooldown(1, 20, type=commands.BucketType.default)
async def gf_embed(inter, title: str = 'None', desc: str = 'None', color: int = 0x000000, authorname: str = 'None', authoricon: str = 'None', footertext: str = 'None', footericon: str = 'None'):

    date = datetime.now()
    month = date.month
    embed = disnake.Embed(title=(None if title == "None" else title), description=(
        None if desc == "None" else desc), color=int(color))

    # Default Author Name and Icon
    embed.set_author(name='GAMER ASSISTANT', icon_url=BOTICON_URL)

    if authorname != "None" or authoricon != "None":
        an, ai = False, False
        if authorname:
            an = True
        if authoricon:
            if authoricon.startswith('https://') or authoricon.startswith('http://'):
                if requests.get(authoricon).status_code == 200:
                    ai = True

        embed.set_author(name=(authorname if an else None),
                         icon_url=(authoricon if ai else None))

    # Default Footer Text and Icon
    embed.set_footer(text=f'Администрация сервера "𝕲𝖆𝖒𝖎𝖓𝖌 𝕱𝖊𝖉𝖊𝖗𝖆𝖙𝖎𝖔𝖓" ({date.day} {("января" if month == 1 else "февраля" if month == 2 else "марта" if month == 3 else "апреля" if month == 4 else "мая" if month == 5 else "июня" if month ==
                     6 else "июля" if month == 7 else "августа" if month == 8 else "сентября" if month == 9 else "октября" if month == 10 else "ноября" if month == 11 else "декабря")} {date.year} года)', icon_url=SERVERICON_URL)

    if footertext != "None" or footericon != "None":
        ft, fi = False, False
        if footertext:
            ft = True
        if footericon:
            if footericon.startswith('https://') or footericon.startswith('http://'):
                if requests.get(footericon).status_code == 200:
                    fi = True

        embed.set_footer(text=(footertext if ft else None),
                         icon_url=(footericon if fi else None))

    await inter.response.send_message(ephemeral=True, embed=disnake.Embed(title="Сообщение успешно создано и отправлено ниже 👇", color=0x7FFF00))
    await inter.channel.send(embed=embed)


@bot.slash_command(default_member_permission=disnake.Permissions.use_application_commands,
                   description="Playing a music from YouTube videos!",
                   dm_permission=False,
                   name="gf_play")
@commands.cooldown(1, 20, type=commands.BucketType.default)
async def gf_play(inter, track: str):
    global queue

    if inter.channel.id not in ALLOWED_CHANNELS:
        raise commands.ChannelNotReadable(inter.channel)

    YDL_OPTIONS = {'format': 'bestaudio/best',
                   'noplaylist': 'True',
                   'verbose': 'True',
                   'postprocessors': [{
                       'key': 'FFmpegExtractAudio',
                       'preferredcodec': 'mp3',
                       'preferredquality': '192'}]
                   }
    FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'}

    if (inter.author.voice):
        if not (inter.guild.voice_client):
            await inter.author.voice.channel.connect()
            await inter.response.send_message(ephemeral=True, embed=disnake.Embed(
                title="Бот был подключен к голосовому каналу!", color=0x7FFF00))
    else:
        await inter.response.send_message(ephemeral=True, embed=disnake.Embed(
            title="Вы не в голосовом канале!", color=0xFF0000))
        return

    if track.startswith('https://www.youtube.com/watch?v') or track.startswith('https://youtu.be/'):
        queue.append(track)
        await inter.channel.send(embed=disnake.Embed(title="Ссылка добавлена в очередь успешно!", color=0x45b3e0))

    md = requests.get(track)

    voice = disnake.utils.get(bot.voice_clients, guild=inter.guild)

    await inter.channel.send(embed=disnake.Embed(description=f"### Сейчас играет:\n## {song_name[0]}", color=0xFFFF00))

# @bot.slash_command(default_member_permission=disnake.Permissions.use_application_commands,
#   description="Playing a TicTacToe!",
#   dm_permission=True,
#   name="gf_tictactoe")
# @commands.cooldown(1, 40, type=commands.BucketType.default)
# async def gf_ticktactoe(inter, versus : str = 'bot'):
#  await inter.response.send_message(ephemeral=True, embed=disnake.Embed(title="Игра началась! ⭕❌", color=0x45b3e0))
#  board = await inter.channel.send(embed=disnake.Embed(title="Игровая доска", color=0xFFFF00, comtent=[]))


# @bot.slash_command(default_member_permission=disnake.Permissions.use_application_commands,
#   description="Generate a greeting for New Year!",
#   dm_permission=False,
#   name="gf_greeting")
# async def gf_greeting(inter):
#  firstChoice = ['с новым счастьем!', '365 новых дней - 365 новых шансов!', 'наслаждайтесь каждым его моментом!', 'примите мои искренние поздравления!', 'годом Дракона🐲!', 'новый старт начинается сегодня!', 'и пусть самые лучшие сюрпризы будут у вас впереди!']
#  secondChoice = [': много новых достижений, крепкого здоровья и любви, пусть задуманное сбудется!', ', чтобы этот год подарил много поводов для радости и счастливых моментов!', ', чтобы будущий год принес столько радостей, сколько дней в году, и чтобы каждый день дарил вам улыбку и частичку добра!', ': вам прекрасного года, полного здоровья и благополучия!', ', чтобы 🐲Дракон принёс в вашу семью любовь, нежность, взаимопонимание и счастье!', ' в Новом году быть здоровыми, красивыми, любимыми и успешными!', ', чтобы сбылось все то, что вы пожелали. Все цели были достигнуты, а планы перевыполнены. Всё плохое и неприятное осталось в уходящем году!']
#  thirdChoice = ['Новый год принесёт много радостных и счастливых дней!', 'каждый новый миг наступающего года приносит в дом счастье, везение, уют и теплоту!', 'всё, что мы планировали, обязательно сбудется!', 'наступающий год станет самым плодотворным годом в вашей жизни!', 'год будет полон ярких красок, приятных впечатлений и радостных событий!', 'этот год будет ВАШИМ годом!', 'Новый год принесёт всё, о чём вы мечтаете и немного больше!']
#  embed = disnake.Embed(title='Генератор рандомных поздравлений. Копируй и поздравляй!', description=f"""
#  Доброго времени суток!
#  С новым годом вас, {choice(firstChoice)}
#  Я желаю вам{choice(secondChoice)}
#  И пусть {choice(thirdChoice)}
#  """, color=0x00BFF)
#  embed.set_author(name='GAMER ASSISTANT', icon_url=BOTICON_URL)
#  date = datetime.now()
#  month = date.month
#  embed.set_footer(text=f'Администрация сервера "𝕲𝖆𝖒𝖎𝖓𝖌 𝕱𝖊𝖉𝖊𝖗𝖆𝖙𝖎𝖔𝖓" ({date.day} {("января" if month == 1 else "февраля" if month == 2 else "марта" if month == 3 else "апреля" if month == 4 else "мая" if month == 5 else "июня" if month == 6 else "июля" if month == 7 else "августа" if month == 8 else "сентября" if month == 9 else "октября" if month == 10 else "ноября" if month == 11 else "декабря")} {date.year} года)', icon_url=SERVERICON_URL)
#  await inter.response.send_message(embed=embed)

if ACTIVE:
    keep_alive()
bot.run(TOKEN)

# with YoutubeDL(YDL_OPTIONS) as ydl:
#   ydl.download([queue[0]])

# voice.play(FFmpegPCMAudio(queue[0], FFMPEG_OPTIONS))
# voice_source = PCMVolumeTransformer(voice.source)
# voice_source.volume = 0.07

# song_name = name.rsplit('-', 2)
