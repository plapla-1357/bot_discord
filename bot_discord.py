import os
import functools 
import asyncio

from discord.ext import commands
import discord
from dotenv import load_dotenv

# module dans le dossier 
import sondage
import python_ececute
import info
import pendu
import use_data_base as db
import argent

load_dotenv(dotenv_path="config")

# jsp trop ce que c'est 
defalt_intent = discord.Intents.default()
defalt_intent.members = True



admin_role_name = "admin"

muted = []


game_pendu = None  # stoke l'objet pendu lorsqu'une partie est en cours


class Bot (commands.Bot):
    
    def __init__(self):
        global defalt_intent
        super().__init__(command_prefix='!',intents = defalt_intent)

    
    #@bot.event
    async def on_reaction_add(self,reaction,user):# reaction ajoutés 

        print("readtion add by : " , user.name)
        
        message = reaction.message
        try:
            if message in sondage.sondage[0]and not user.bot:
                sondage.add_to_compteur(reaction.emoji)
        except:
            pass
            
    # @bot.event
    async def on_reaction_remove(self,reaction,user): # reaction enlevé
        print("reaction remove by : ", user.name)
        message = reaction.message
        if message in sondage.sondage[0]:
            sondage.enlever_au_compteur(reaction.emoji)     

    # @bot.event
    async def on_ready(self):
        """
        quand le bot est près
        """
        print("the bot is ready !")
                
    # @bot.event
    async def on_member_join(self,member):
        print("member joined")
        general_channel = bot.get_channel(777264787037618186)
        em_join = discord.Embed(title = "quelqu'un a rejoint le server", description = f"bienvenue {member.display_name} 🎉",color = 0xf7da86)
        em_join.set_thumbnail(url = member.avatar_url)
        await general_channel.send(embed = em_join)
    
    async def on_member_remove(self,member):
        print("member leave")
        general_channel = bot.get_channel(777264787037618186)
        em_leave = discord.Embed(title = "quelqu'un a quiter le server", description = f"au revoir {member.display_name}",color = 0xf7da86)
        em_leave.set_thumbnail(url = member.avatar_url)
        await general_channel.send(embed = em_leave)
        
            
    # @bot.event
    async def on_message(self,message):
        if "```python" in message.content:
            code = message.content
            code = code.replace("```py","")
            code = code.replace("```","")
            await python_ececute.execute(message.channel,code,message.author)
            await message.delete()
            
        elif game_pendu != None and game_pendu.demande_reponce: # si le jeu de pendu demande une reponce
            if not message.author.bot:
                game_pendu.reponce = message.content
                game_pendu.demande_reponce = False
                await message.delete()
            
            
        await bot.process_commands(message)
        



bot = Bot()


async def command_by_admin(ctx):    
    if not admin_role_name in ctx.author.roles:
        await info.em_pas_permision(ctx)
        return False
    else:
        return True
  
def command_admin(func):  
    """decorateur qui verifie si la personne qui fais un commande est un admin
    Returns:
        [func] -- [nouvelle fonction avec la command uniquement si il a les drois]
    """
    @functools.wraps(func)
    async def new_func(ctx, *args, **kwargs):
        print(ctx.author.roles)   
        admin = False         
        for role in ctx.author.roles:
            if admin_role_name in role.name:
                print("a bien le role necesaire")
                await func(ctx,*args,**kwargs)          
                admin = True
                
        if not admin:
            await info.em_error(ctx, "vous n'avez pas la permision d'utiliser cette commande")
            print("n'a pas le role neccesaire")
            
            
    return new_func
          
        
                       
@bot.command(name= "hi") 
async def say_hi(ctx):#say hi
    channel = ctx.channel
    author = ctx.author.mention
    em = discord.Embed(title = "bonjour a toi")
    em.set_thumbnail(url = ctx.author.avatar_url)
    em.set_author(name = ctx.author.mention, icon_url= ctx.author.avatar_url)
    await ctx.channel.send(embed = em, delete_after = 5)
    await channel.send(f"bonjour a toi {author}", delete_after = 5)

@bot.command(name = "kill")
async def kill( ctx, mention : discord.Member):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True)
    embed = discord.Embed(title="muted", description=f"{mention.mention} was muted ", colour=discord.Colour.light_gray())
    await ctx.send(embed=embed)
    await mention.add_roles(mutedRole)
    await asyncio.sleep(100)
    await mention.remove_roles(discord.utils.get(ctx.guild.roles, name="muted")) 
    await argent.paye(ctx, mention, 50)
    
# commande du sondage   
@bot.command(name = "sondage")
async def create_sondage( ctx, title,*args):

    await sondage.crée_sondage(ctx,title,args)  
    
@bot.command(name= "end")
async def end_sondage( ctx):
    await sondage.end_sondage(ctx)


@bot.command(name ="calcul")
async def eval_py( ctx,calcule):
    await python_ececute.eval_py(ctx,calcule)

@bot.command(name = "python")
async def execute( ctx, code : str):
    print(code)
    await ctx.message.delete()
    await python_ececute.execute(ctx.channel,code,ctx.author)
    
@bot.command(name = "steal")
async def steal(ctx , user : discord.Member):
    await argent.steal(ctx, user)
    
@bot.command(name="catch")
async def catch(ctx, user : discord.Member):
    print("catch")
    await argent.catch(ctx, user)

@bot.command(name = "bank") 
async def show_money(ctx):
    await argent.show_money(ctx)
    
@bot.command(name = "bank_of") 
async def show_money(ctx, user:discord.User):
    await argent.show_money_of(ctx, user)
    
@bot.command(name = "top_list")
async def top_list( ctx):
    await argent.top_list(ctx)
    
@bot.command(name = "pari")
async def pari(ctx, title , reponce , amount):
    await argent.pari(ctx, title , reponce , amount)
    
@bot.command(name = "paye")
async def paye(ctx, mention : discord.User , amount : int):
    if not amount <= 0 :
        await argent.paye(ctx, mention, amount)
    else:
        await info.em_error(ctx,"vous tenter de voler de l'argent ( c'est interdit ) ⛔")

@bot.command(name = "pendu")
async def create_pendu( ctx):
    global game_pendu
    game_pendu = pendu.Pendu(ctx)
    if ctx.channel == ctx.guild.get_channel(game_pendu.channel_pendu_id):
        await game_pendu.main_pendu()
        game_pendu = None




@bot.command(name = "aide")
async def help (ctx):
    await info.commands(ctx)
    await ctx.message.delete()

@bot.command(name = "info_python")
async def info_python( ctx):
    await info.help_python(ctx)
    
    


@bot.command(name = "create_role") 
async def crée_role( ctx,name, color ): # crée un nouveau role
    if command_by_admin:
        print("demarer") 
        print(color.split(","))
        r,g,b =color.split(",")
        r,g,b = int(r),int(g), int(b)
        # col = int(color,16)
        # print(col)
        await ctx.guild.create_role(name = name, color = discord.Color.from_rgb(r,g,b))
        em = discord.Embed(description = f"le role {name} a bien été crée" , color = discord.Color.from_rgb(r,g,b))
        await ctx.channel.send(embed = em)
    
    
@bot.command(name = "del_role")
async def del_role( ctx,name):
    if command_by_admin:
        roles = await ctx.guild.fetch_roles()
        for role in roles:
            if role.name == name:
                await role.delete()
                em_del = discord.Embed(description = f"le role : {role.name} a bien été suprimé", color = 0xff0000)
                await ctx.channel.send(embed = em_del) 
                
@bot.command(name = "mute")
@command_admin
async def mute(ctx, mention : discord.Member):
    guild = ctx.guild
    mutedRole = discord.utils.get(guild.roles, name="muted")

    if not mutedRole:
        mutedRole = await guild.create_role(name="muted")

        for channel in guild.channels:
            await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=True, read_messages=True)
    embed = discord.Embed(title="muted", description=f"{mention.mention} was muted ", colour=discord.Colour.light_gray())
    await ctx.send(embed=embed)
    await mention.add_roles(mutedRole)


@bot.command(name = "unmute")
async def unmute(ctx, mention : discord.Member):
    await mention.remove_roles(discord.utils.get(ctx.guild.roles, name="muted"))                

@bot.command(name='del')
async def delete( ctx):#delete all the message of a channel
    if command_by_admin:
        async for mess in ctx.channel.history(): 
            await mess.delete()
            
    embed = discord.Embed(description = f"{ctx.author.mention} à clear le salon", color = 0xdd31fc)
    await ctx.channel.send(embed = embed, delete_after = 15)  

 
@bot.command(name = "create_pari")
@command_admin 
async def create_pari( ctx,title, *proposition):
    await sondage.create_pari(ctx,title,proposition) 
@bot.command(name = "end_pari")   
@command_admin
async def end_pari(ctx,question, reponce):
    await argent.end_pari(ctx,question,reponce)    
    

@bot.command(name ="add_money")
@command_admin
async def add_money(ctx , user : discord.User , amount):
    complete = db.add_money(user.id, amount)
    print(complete)
    if complete:
        await info.em_call_back(ctx,f"{amount} $ a bien été distribué")
    else:
        await info.em_error(ctx,"cette personne n'as pas asser d'argent pour payer")
        
@bot.command(name = "birthday")
@command_admin
async def birthday(ctx , user : discord.User):
    em_aniv = discord.Embed(title = f"🎁 c'est l'aniversaire de {user.display_name} 🎂",
                            description = "🎂 tous le monde doit lui donner minimum 10 $ comme cadeau d'anniversaire 🎁",
                            color= 0x48ee4b)
    em_aniv.set_thumbnail(url = user.avatar_url)
    await ctx.channel.send(embed =em_aniv)
    db.add_money(user,25)
    
     
    
@bot.command(name = "info_admin")
@command_admin
async def info_admin( ctx):
    await info.commands_admin(ctx)  

# token dans un dosier config (a ne pas mettre sur git hub)  
bot.run(os.getenv("TOKEN"))











