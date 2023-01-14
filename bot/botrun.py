import sqlite3
import string
import json
import discord
from discord.ext import commands
import os
import asyncio

bot = commands.Bot(command_prefix='.', intents=discord.Intents.all())
base = None
cursor = None


@bot.event
async def on_ready():
    print('Я банан')
    global base, cursor
    base = sqlite3.connect('BaseData.db')
    cursor = base.cursor()
    if base:
        print('BaseData - connected')


@bot.event
async def on_message(message):
    await bot.process_commands(message)
    talk = discord.utils.get(message.author.guild.roles, name='Talk')
    mute = discord.utils.get(message.author.guild.roles, name='Mute')
    with open("bad_words.json", "r", encoding='utf8') as file:
        bad_words = set(json.load(file)['bad_words'])
    msg = message.content.lower()
    msg_list = msg.split(' ')
    msg_set = set()
    for i in msg_list:
        msg_set.add(i.translate(i.maketrans('', '',
                                            string.punctuation)))  # maketrans - это правило translate и make trans не разлучны(',' , ' '#одинаковая длинна) # string.punctuation - все символы а значит аргумент1, аргумент2,после стринг

    if bad_words.intersection(msg_set) != set():
        await message.delete()
        cursor.execute('CREATE TABLE IF NOT EXISTS warning(userid INT, count INT, mute INT)')
        base.commit()
        warnings = cursor.execute('SELECT * FROM warning WHERE userid == ?', (message.author.id,)).fetchone()
        if warnings[1] == 0:
            cursor.execute('UPDATE warning SET count == ?, mute == ? WHERE userid == ?', (1, 0, message.author.id))
            base.commit()
            await message.channel.send(f'{message.author.mention} получил 1-ое предупреждение, на 3 бан!')
        elif warnings[1] == 1:
            cursor.execute('UPDATE warning SET count == ?, mute == ? WHERE userid == ?', (2, 1, message.author.id))
            base.commit()
            await message.channel.send(f'{message.author.mention} получил 2-ое предупреждение')
            await message.author.add_roles(mute)
            await message.author.remove_roles(talk)
            await asyncio.sleep(600)
            await message.author.add_roles(talk)
            await message.author.remove_roles(mute)
            #здесь был мут

        elif warnings[1] == 2:
            cursor.execute('UPDATE warning SET count == ? WHERE userid == ?', (3,message.author.id))
            base.commit()
            await message.channel.send(f'ban user{message.author.mention}')
            await message.author.ban(reason='Сквернословие ')
    elif 'дела' in message.content.lower():
        await message.channel.send('пшл нх')


@bot.event
async def on_member_join(member):
    await member.send('Welcome')
    guild = bot.get_guild(1046820226056069221)
    channel = guild.get_channel(1046820226056069223)
    await channel.send('Приятного путешествия в Казахстан')
    talk = discord.utils.get(member.guild.roles, name='Talk')
    mute = discord.utils.get(member.guild.roles, name='Mute')
    cursor.execute('CREATE TABLE IF NOT EXISTS warning(userid INT, count INT, mute INT)')
    base.commit()
    check = cursor.execute('SELECT * FROM warning WHERE userid == ?', (member.id,)).fetchone()
    if check is None:
        cursor.execute('INSERT INTO warning VALUES (?, ?, ?)', (member.id, 0, 0))
        base.commit()
        await member.add_roles(talk)
    elif check[2] == 0:
        await member.add_roles(talk)
    elif check[2] == 1:
        await member.add_roles(mute)




@bot.event
async def on_member_remove(member):
    guild = bot.get_guild(member.guild.id)  # 2-способ
    for i in guild.text_channels:
        if i.name == 'игры':
            await bot.get_channel(i.id).send(f'Не велика потеря, {member.mention}')


@bot.command()
async def test(message):
    await message.send('В пути')
    #await message.author.send('В пути') #ообщение в личку


@bot.command()
async def info(message, *, arg):
    await message.send(arg)


@bot.command()
async def repeat(message, arg=None):
    author = message.message.author
    if arg == None:
        await message.send(f'{author.mention} Ты правила не читал что ли!!!')
    elif arg == 'общая':
        await message.send(f'{author} Я My_bot#4270 участник c 28 ноября 2022')
    elif arg == 'команды':
        await message.send(f'{author} .info - Повторю любое слово\n.test - Проверить работаю ли я ')


@bot.command()
async def clear(message, amount=3):
    await message.channel.purge(limit=100)


@bot.command(pass_context=True)
@commands.has_permissions(administrator=True)
async def banan(message, member: discord.Member, *, reason=None):
    await message.channel.purge(limit=1)
    await member.ban(reason=reason)
    await message.message.send(f'ban user{member.mention}')

@bot.command()
async  def status(message, member: discord.Member):
    check = cursor.execute('SELECT * FROM warning WHERE userid == ?', (member.id,)).fetchone()
    #await message.message.send(f'count user{member.mention}')
    if check[1] == 0:
        await message.channel.send(f'У {member.mention} НЕТ предупреждений')
    else:
        await message.channel.send(f'Не чиста твоя душа')
    #elif check[1] == 1:
        #await message.channel.send(f'У {member.mention} 1 предупреждение')
    #elif check[1] == 2:
        #await message.channel.send(f'У {member.mention} 2 предупреждение')

bot.run('MTA0NjgyMDc4NjEyNTY4NDg5Ng.Gtb8PD.510n1EtRpijaZ-RRz248YkImT0TgV2uaUzwNHw')


#remove rols