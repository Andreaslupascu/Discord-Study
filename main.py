
import asyncio
import discord
import sqlite3
import os
from datetime import datetime
from pomobot.timer import Timer, TimerStatus
from dotenv import load_dotenv
from discord.ext import commands
import discord
import os
import requests
import json
import random
from replit import db
from keep_alive import keep_alive
client = discord.Client()


COLOR_DANGER = 0xc63333
COLOR_SUCCESS = 0x33c633



class DiscordCog(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
        self.timer = Timer()
        self.db = sqlite3.connect('pomobot.db')
        self.create_tables()


    def create_tables(self):
        cur = self.db.cursor()
        # Create table
        cur.execute('''
        CREATE TABLE IF NOT EXISTS alarms (
            id integer PRIMARY KEY AUTOINCREMENT,
            username text NOT NULL,
            start_time text NOT NULL,
            delay text NOT NULL
            )
        ''')
        self.db.commit()


    @commands.Cog.listener()
    async def on_ready(self):
        print('We have logged in as {}'.format(self.bot.user))


    @commands.command()
    async def start(self, ctx):
        if self.timer.get_status() == TimerStatus.RUNNING:
            await self.show_message(ctx, "Timer is already running! You should stop the timer before you can restart it!", COLOR_SUCCESS)    
            return

        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        cur = self.db.cursor()
        cur.execute('''
        INSERT INTO alarms (username, start_time, delay)
            VALUES (?,?,?)
        ''', [str(ctx.author),current_time,'10'])
        self.db.commit()

        cur = self.db.cursor()
        for row in cur.execute('SELECT * FROM alarms'):
            print(row)

        await self.show_message(ctx, "Time to start working!", COLOR_SUCCESS)
        self.timer.start(max_ticks=10)
        while self.timer.get_status() == TimerStatus.RUNNING:
            await asyncio.sleep(1)
            self.timer.tick()
        if self.timer.get_status() == TimerStatus.EXPIRED:
            await self.show_message(ctx, "Time to start your break!", COLOR_SUCCESS)
            self.timer.start(max_ticks=10)
            while self.timer.get_status() == TimerStatus.RUNNING:
                await asyncio.sleep(1)
                self.timer.tick()
            if self.timer.get_status() == TimerStatus.EXPIRED:
                await self.show_message(ctx, "Okay, break over!", COLOR_SUCCESS)


    async def show_message(self, ctx, title, color):
        start_work_em = discord.Embed(title=title, color=color)
        await ctx.send(embed=start_work_em)


    @commands.command()
    async def stop(self, ctx):
        if self.timer.get_status() != TimerStatus.RUNNING:
            await self.show_message(ctx, "Timer is already stopped! You should start the timer before you can stop it!", COLOR_SUCCESS)    
            return        
        await self.show_message(ctx, "Timer has been stopped!", COLOR_DANGER)
        self.timer.stop()


    @commands.command()
    async def show_time(self, ctx):
        await ctx.send(f"Current timer status is : {self.timer.get_status()}")
        await ctx.send(f"Current time is : {self.timer.get_ticks()}")


    @commands.command()
    async def show_help(self, ctx):
        help_commands = dict()
        for command in self.bot.commands:
            help_commands[command.name] = command.help
        description = "Bot commands are: {}".format(help_commands)
        show_help_em = discord.Embed(title="This is Mr Pomo Dorio, a friendly Pomodoro bot", description=description,
                                    color=COLOR_SUCCESS)
        await ctx.send(embed=show_help_em)

if "responding" not in db.keys():
  db["responding"] = True
@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  if message.author == client.user:
    return

  msg = message.content

  if msg.startswith('$inspire'):
    quote = get_quote()
    await message.channel.send(quote)

  if db["responding"]:
    options = starter_encouragements
    if "encouragements" in db.keys():
      options = options + db["encouragements"]

    if any(word in msg for word in sad_words):
      await message.channel.send(random.choice(options))

  if msg.startswith("$new"):
    encouraging_message = msg.split("$new ",1)[1]
    update_encouragements(encouraging_message)
    await message.channel.send("New encouraging message added.")

  if msg.startswith("$del"):
    encouragements = []
    if "encouragements" in db.keys():
      index = int(msg.split("$del",1)[1])
      delete_encouragment(index)
      encouragements = db["encouragements"]
    await message.channel.send(encouragements)

  if msg.startswith("$list"):
    encouragements = []
    if "encouragements" in db.keys():
      encouragements = db["encouragements"]
    await message.channel.send(encouragements)

  if msg.startswith("$responding"):
    value = msg.split("$responding ",1)[1]

    if value.lower() == "true":
      db["responding"] = True
      await message.channel.send("Responding is on.")
    else:
      db["responding"] = False
      await message.channel.send("Responding is off.")

keep_alive()
client.run(os.getenv('TOKEN'))