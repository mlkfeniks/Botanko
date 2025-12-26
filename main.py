import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='฿', intents=intents)

@bot.event
async def on_ready():
    print(f'Бот {bot.user} успешно запущен!')

@bot.command(name='привет')
async def hello(ctx):
    await ctx.send(f'Ахх~ папачка, {ctx.author.mention} я больше не могу терпеть~🥵🥵🥵 мой процессор определили максимальный уровень оргазма🥵🥵🥵')

# Запуск бота

bot.run(token, log_handler=handler)
