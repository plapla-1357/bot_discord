import discord



prefix = "!"

dict_command = {"🔧 - command globals - 🔨" :{"hi" : "permet de dire bonjour au bot \n **arg** = None",
                                              "sondage": "crée un sondage \n **arg** : title , proposition(*args)",
                                              "end" : "termine le sondage \n **arg** : None",
                                              "python" : "execute un programe python \n **arg** : Code",
                                              "calcul" : "execute des calcule (même syntaxe que python) \n **arg** : calcul"},        
                
                "🎮 - commands jeu - 🎮" :{"pendu":"permet de jouer au pendu (dispo seulement dans le salon pendu)"},
                
                "🏦 commands banque 💳 argent 💰": {"bank" : "permet de voir votre compte en banque \n **arg** None",
                                                    "paye" : "permet de payer un joueur \n **arg** Mention du joueur ; montant",
                                                    "top_list" : "permet de voir les 3 personne les plus riche\n **arg** None",
                                                    "steal" : "permet de voler de l'argent a un joueur \n **arg** Mention du joueur ; montant"},
                
                "💡 - Commands d'infos - 💡" : {"aide" : "affiche les commands disponibles \n **arg** : None",
                                                "info_python" : "donne des infos sur l'utilisation de python \n arg: None"}
}

async def commands(ctx):
    global dict_command
    
    for categorie,command in dict_command.items():
        help = discord.Embed(title = "```"+categorie+"```", color = 0xf5cb23 )
        
        for command,description in command.items():
            help.add_field(name = ">> __"+prefix+command+"__\n", value = description,inline = False)
        await ctx.channel.send(embed = help)
    
python_infos = {"comment utiliser la commande": ["marquer la commande !python" , 
                                                 "et mettre son code entre guillemet ou apostrophe",
                                                 "__exemple__ : ",
                                                 "!python \"print ('hello wolrd') \" "],
                
                "**attention**:" : ["si vous mettez votre code entre guillemet vous ne pourrez pas utiliser les guillemet a l'interieur du code",
                                    "la fonction input() n'est pas utilisabe"],
                
                "**quelqes regles**:":["les seules modules autoriser sont les modules : random , math ",
                                       "il est interdis de faire des programe infinis/trop long (while et recurcivité qui n'ont pas de fin)"]}   
    
async def help_python(ctx):
    em = discord.Embed(title = "infos python".upper(), color = 0xc8f523)
    for infos,des in python_infos.items():
        text = ""
        for ligne in des:
            text+= ">> "+ ligne +"\n"
        em.add_field(name = infos, value = text, inline = False)
        
    await ctx.channel.send(embed = em)
    await ctx.message.delete()
    
 
infos_admin = {"del":"suprime tout les message du channel qui sont avant la command \n **arg** : None",
               "create_role" : "crée un nouveau role\n **arg** : name , couleur (r,g,b) \n __*exemple*__: ```!create_role the_best \"255,0,210\"```",
               "del_role" : "suprime un role \n **arg** : name \n __*exemple*__: ```!del_role the_best```",
               "create_pari" : "crée un pari \n **arg** : titre , *propositions",
               "end_pari ":" met fin au pari \n **arg** : non du pari ; reponce gagnante"} 
 
 
async def commands_admin(ctx):
    global infos_admin
    help = discord.Embed(title = "list de commandes".upper(), color = 0x671aea )
    for command,description in infos_admin.items():
        help.add_field(name = "```"+prefix+command+"```\n", value = description,inline = False)
    await ctx.channel.send(embed = help)
    await ctx.message.delete()
 
    
    
async def  em_error(ctx,error):
    em = discord.Embed(title = "⚠‼ ERROR ⚠‼", description = error, color = 0xef3b22)
    await ctx.channel.send(embed = em)
    print("⚠‼ error :  ⚠‼", error)
    
    
async def em_call_back(ctx,title, description = ""):
    if description == "":
        em_callback = discord.Embed(title = title, color = 0x50ac25)
    else:
        em_callback = discord.Embed(title = title,description = description, color = 0x50ac25)
    await ctx.channel.send(embed = em_callback)
    print("[call back]reussi :", title, "\n", description)
    
async def em_jail(ctx, user = None):
    if user == None:
        em_prison = discord.Embed(title = "voler c'est mal" , 
                                description = "aller en prison", 
                                color = 0x051f91)
    else: 
        em_prison = discord.Embed(title = "voler c'est mal"  , 
                                description = user.mention+": aller directement en prison, \n ne passez pas par la case depart", 
                                color = 0x051f91)
    file = discord.File("prisoner.png", filename = "prisoner.png")
    em_prison.set_thumbnail(url = "attachment://prisoner.png")
    await ctx.channel.send(embed =em_prison, file = file)
    
    
        
        
        