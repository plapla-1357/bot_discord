import ast
# from operator import itemgetter

from discord.ext import commands
import discord


import use_data_base as db
from info import em_error, em_call_back


emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", 
              "5️⃣", "6️⃣", "7️⃣", "8️⃣", 
              "9️⃣", "🔟"]
emojis_gagnants = ["🥇","🥈","🥉", "4️⃣", 
              "5️⃣", "6️⃣", "7️⃣", "8️⃣", 
              "9️⃣", "🔟"]

pari = []
sondage = []
txt_choix = []
async def crée_sondage(ctx, title, args):
    global txt_choix
    if not sondage == []:  # ne pas crée plusieur sondage en même temps
        return None
    
    if len(args)>10:
        print("il ne peux pas y avoir plus de 10 proposition")
        return None
        
    
    
    infos = []
    propositions = len(args)
    
    
    text = []
    numero = 0
    for proposition in args:  # crée le text de la description 
        text.append(f"-{emojis[numero]} <=> {proposition}" ) 
        txt_choix.append(proposition)
        numero += 1   
    
    description = "\n".join(text)
        
        
    
    em = discord.Embed(title = f"   {title.upper()}" , description = description, color = 0x42bbf4)
    em.set_author(name = ctx.message.author.display_name, icon_url= ctx.message.author.avatar_url)
    
    message = await ctx.channel.send(embed = em)
    
    
    for emoji in range(len(args)):  # created emojies
        await message.add_reaction(emojis[emoji])
    
    infos.append(message) # stoke le message du sondage 
    for reponce in range(propositions):
        infos.append([reponce,0])
    print(infos)
    
    sondage.append(infos)
             
    await ctx.message.delete() # delete the command message
    
  
def second(Elem):
    return Elem[1]
      
    
async def end_sondage(ctx):
    global sondage
    global txt_choix
    color_em_resultat = 0x141ad5
    print("end songage declanger")
    print(sondage)
    await ctx.message.delete()
    sondage[0].pop(0)
    sondage[0].sort(key = second, reverse = True)
    print("the real",sondage[0])
    
    place = 0
    txt = ""   
    for proposition in sondage[0]:
        txt += f"{emojis_gagnants[place]} : **{txt_choix[proposition[0]]}** : {proposition[1]} \n"
        place += 1
    em_resultat = discord.Embed(title = "resultat du sondage:", description = txt, color = color_em_resultat)
    await ctx.channel.send(embed = em_resultat)
    txt_choix = []
    sondage = []
   
   
async def create_pari(ctx, title, propositions):
    await ctx.message.delete()
    color_em = 0xb2ea1e
    
    if len(propositions)>10:
        await ctx.channel.send("il ne peux pas y avoir plus de 10 proposition")
        return None
    
    text = "**__*Les paris sont ouvert:*__** \n \n"
    for i in range(len(propositions)):
        text += f"{emojis[i]} : {propositions[i]} \n"
    em_pari = discord.Embed(title = title, description = text, color = color_em)  
    pari = await ctx.channel.send(embed = em_pari) 
    
    
        
    # todo sauvegarder les donnée du pari  
    db.add_new_pari((pari.id,
                    ctx.channel.id,
                    title,
                    str(propositions)))
    print("pari crée")
  
            
def add_to_compteur(numero):
    nb = emojis.index(numero)+1
    sondage[0][nb][1] += 1
    
    
def enlever_au_compteur(numero):
    nb = emojis.index(numero)+1
    sondage[0][nb][1]-= 1
    # print(sondage[0][nb])