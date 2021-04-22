import time
import asyncio

from discord.ext import commands
import discord



out = "OUT : \n"
# context = None

color_em_code = 0x1eea31 #green
color_em_out = 0x1e8aea #blue
color_em_calcul = 0x1e62ea #blue
color_em_resultat = 0xea9a1e #orange

channel_python_allowed = [826924968854945842,825280814510112798]



def PRINT(str):  # a faire la faire avec un *args
    global out
    var = str
    out += f"{var}" + "\n"
    print(var)
    
async def ereur(channel,e):
    em_error = discord.Embed(title = "error".upper(), description = str(e), color = 0xff0000)
    await channel.send(embed = em_error)
    
async def ver_time():
    await asyncio.sleep(1)
    print('hi')
    
async def execute(channel, code,author):
    global channel_python_allowed
    global out
    if channel.id in channel_python_allowed:
        
        #print(ctx.message.content) 
        
        em_python = discord.Embed( description = f"```python\n{code}```" ,color = color_em_code)
        em_python.set_author(name = author.display_name, icon_url= author.avatar_url)
        await channel.send(embed = em_python)
        code = code.replace("print(", "PRINT(")
        code = code.replace("print (","PRINT (")
        
        try:
            print(time.time())
            await ver_time()
            exec(code)
            print(time.time())
            em_out = discord.Embed( description = f"```{out}```" ,color = color_em_out)
            await channel.send(embed = em_out)
            out = "OUT : \n"
            
            #await channel.send(f"```{out}```")
        except Exception as e :
            print("exepted")
            await ereur(channel ,e)
            
            # retour a la normal
            out = "OUT : \n"
            return None
            
    
        
        # retour a la normal
        out = "OUT : \n"
        # context = None
    else: 
        em_ = discord.Embed( description = f"vous ne pouvez pas utiliser le python dans ce channel", color = 0x7a0d23)
        await channel.send(embed = em_)
        
    
    
async def eval_py(ctx , calcule):
    try:
        em_calcul = discord.Embed(description = f"```{calcule}```", color = color_em_calcul)
        await ctx.channel.send(embed = em_calcul)
        em_resultat = discord.Embed(description = f"```{eval(calcule)}```", color = color_em_resultat)
        await ctx.channel.send(embed = em_resultat)
        
        
    except Exception as e:
        await ctx.channel.send(ereur(ctx,e)) 
        return None
        