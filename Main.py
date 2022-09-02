import disnake, os, json, random
from disnake.ext import commands
from scripts import utilScripts as uS
from scripts import feedbackForm as FB
from dotenv import load_dotenv
from dotenv import load_dotenv

load_dotenv()

intents = disnake.Intents.default()
intents.message_content = True
bot = commands.InteractionBot(intents=intents)


class slashCommands():
    
    @bot.after_slash_command_invoke
    async def logClean(AppCmdInt): print("\n")

    @bot.before_slash_command_invoke
    async def commandRan(AppCmdInt): uS.log(f"{AppCmdInt.user.name} invoked command {AppCmdInt.application_command.name}")

    @bot.slash_command(     description="Test the bots response time", dm_permission=True       )
    async def ping(ctx): await ctx.response.send_message(f"Pong! | {bot.latency}ms", ephemeral=True)

    @bot.slash_command(description="Van peoples")
    async def van(ctx, user : disnake.abc.Snowflake, ping : bool = False):
    # loads storage file, parses with gathered user id, updates json, sends response message
        with open("vans.json", "r") as STORAGEFILE: storagejson = json.load(STORAGEFILE)
        uS.log("read vans.json")
        try: 
            storagejson[str(user.id)] += 1
        except(KeyError): 
            uS.log("Error, Profile not found")
            storagejson[str(user.id)] = 1
            uS.log(f"Profile created for {user.id}")
        with open("vans.json", "w") as STORAGEFILE: json.dump(storagejson, STORAGEFILE, indent=4)
        uS.log(F"Van counted")
        with open("config.json", "r") as CONFIGFILE: vanGif = random.choice(json.load(CONFIGFILE)["VanGifs"])
        uS.log("Collected van gif:" + vanGif)
        if ping: vannedMember = "<@" + str(user.id) + ">" 
        else: vannedMember = user.name
        await ctx.response.send_message(f"{ctx.author.name} has vanned {vannedMember}\n{vanGif}")
        uS.log(f"Van message sent in {ctx.channel.name}")

    @bot.slash_command(description="Count total vans")
    async def count(ctx, user : disnake.abc.Snowflake = ""):
        # loads json file, sends response message
        userID = str(ctx.author.id) if user == "" else str(user.id) 
        with open("vans.json", "r") as STORAGEFILE: storagejson = json.load(STORAGEFILE)
        uS.log("vans.json read")
        try: await ctx.response.send_message(f"{user.name} has: {storagejson[userID]} vans on record")
        except(AttributeError): await ctx.response.send_message(f"{ctx.author.name} has: {storagejson[userID]} vans on record", ephemeral=True)
        except(KeyError): await ctx.response.send_message("User does not have an account")
        uS.log("Response message sent")

    @bot.slash_command(description="Add a van gif to the config")
    async def addgif(ctx, gif : str):
        # ensures user is admin, loads json, updates json, sends response message
        if ctx.author.id == 554486518543155212:
            uS.log("Validation passed")
            with open("config.json", "r") as CONFIGFILE: vanList = json.load(CONFIGFILE)
            uS.log("Read config file")
            vanList["VanGifs"].append(gif)
            with open("config.json", "w") as CONFIGFILE: json.dump(vanList, CONFIGFILE, indent=4)
            uS.log("Wrote to config")
            await ctx.response.send_message(content ="Gif added to config", ephemeral=True)
            uS.log("Response message sent")
        else:
            await ctx.response.send_message(content ="You do not have permission to access this command", ephemeral=True)
            uS.log(f"Invalid sign on by {ctx.author}")

    @bot.slash_command(description="Feed back form")
    #basic feedback form that put responses in a text document with (key:value) pairing
    async def feedback(ctx: disnake.AppCmdInter):
        await ctx.response.send_modal(modal=FB())
        uS.log("Feedback modal sent")


class textCommands():

    @bot.event
    async def on_message(message : disnake.message.Message):
        content = message.content.lower()
        with open("config.json", "r") as CONFIGFILE: config = json.load(CONFIGFILE)
        try: prefix = config["Prefixs"][str(message.guild.id)]
        except(KeyError):
            prefix = "!!"
            config["Prefixs"][message.guild.id] = "!!"
            with open("config.json", "w") as CONFIGFILE: json.dump(config, CONFIGFILE, indent=4)
            uS.log("New server prefixed added under id:" +str(message.guild.id))

        if content[:len(prefix)] == prefix:
            content = content[len(prefix):]
            uS.log(f"Command: {content} ran by {message.author.name}")

            if content[:3] == "van": 
                ids = []
                titles = ""
                while content.find("@") != -1:
                    content = content[content.find("@") + 1:]
                    ids.append(content[:content.find(">")])

                for user in ids:
                    with open("vans.json", "r") as STORAGEFILE: storagejson = json.load(STORAGEFILE)
                    try: 
                        storagejson[str(user)] += 1
                    except(KeyError): 
                        uS.log("Error, Profile not found")
                        await message.channel.send("Creating profile for:" + str(await message.guild.fetch_member(int(user))))
                        storagejson[str(user)] = 1
                    with open("config.json", "r") as CONFIGFILE: vanGif = random.choice(json.load(CONFIGFILE)["VanGifs"])
                    with open("vans.json", "w") as STORAGEFILE: storagejson = json.dump(storagejson, STORAGEFILE, indent=4)
                    titles += f" {str(await message.guild.fetch_member(user))}"
                await message.channel.send(f"{message.author.name} has vanned:{titles}\n{vanGif}")


            if content[:5] == "count":
                try: 
                    user = content[content.find("@") + 1: content.find(">")]
                    with open("vans.json", "r") as STORAGEFILE: count = json.load(STORAGEFILE)[user]
                    await message.channel.send(f"{await message.guild.fetch_member(int(user))} has: {count} vans on record")
                except(KeyError):
                    await message.channel.send("User profile does not exist") 

                    


    @bot.listen()
    async def on_ready():
        await bot.change_presence(activity=disnake.Activity(type=disnake.ActivityType.playing, name="Vanning sim 3.00.1"))
        print(f"""
        Bot Boot Log:
            Status:{bot.status}
            Commands:{len(bot.slash_commands)}
            Activity:{bot.activity}
            WebSocket:{bot.ws}
            LocalizationStore:{bot.i18n}
            Intents:{bot.intents}
            LATENCY:{bot.latency}ms
            Guilds: {[i.name for i in bot.guilds]}
        """)
        bot.allowed_mentions = disnake.AllowedMentions(everyone= True)

bot.run(os.getenv("GreyAdminBot"))
