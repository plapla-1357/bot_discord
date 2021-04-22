import random
import asyncio

import discord


file_mot = open("pendu_data/mots.txt","r")
mots = file_mot.read().split("\n")
file_mot.close()
# print(mots)

    

class Pendu:
    def __init__(self,ctx):
        """crée une partie 

        Arguments:
            players {Discord.Member} --[list des joueur qui jouent au pendu]
        """
        global mots
        
        self.ctx = ctx
        self.channel_pendu_id = 827275859798130788
        self.vie = 10
        self.char_cache = "_ " # caracter pour cacher la lettre
        
        self.players = []
        self.mots = mots
        self.lettre_trouvé = []
        self.lettre_testé = [] 
        self.tour = 0
        self.running =True
        
        self.id_ask = None # id du message qui demande la lettre
        self.demande_reponce = False
        self.reponce = None
        
        
        
        
    async def main_pendu(self):
        self.mot = self.choose_mot()
        self.players = await self.find_players()
        print(self.players)
        
        
        while self.running:
            await self.check_word(await self.ask_letter())
            self.tour += 1    
        
        # crée la parti et determiner les joueurs
    
    async def find_players(self):
        emoji_play = "✅"
        delay = 10
        
        #message pour appeler les joueurs qui veulent jouer
        list_player = [self.ctx.message.author]
        em_demande_joueur = discord.Embed(title = f"Qui veux joueur au pendu avec {self.ctx.message.author}",
                                          description = f"mettez la reaction {emoji_play} pour jouer\n le jeu démare dans {delay} secondes",
                                          color = 0x19990c)
        message_demande_joueur = await self.ctx.channel.send(embed = em_demande_joueur)
        await message_demande_joueur.add_reaction(emoji_play)
        
        # laiser au joueur le temps de rejoindre
        for second in range(delay,-1,-1):
            await asyncio.sleep(1)
            update = discord.Embed(title = f"Qui veux joueur au pendu avec {self.ctx.message.author}",
                                          description = f"mettez la reaction {emoji_play} pour jouer\n le jeu démare dans {second} secondes",
                                          color = 0x19990c)
            await message_demande_joueur.edit(embed = update)
        
        message = await self.ctx.fetch_message(message_demande_joueur.id)  
        
        for reaction in message.reactions:
        # aficher les joueur qui vont participer 
            if reaction.emoji == emoji_play:
                text_em = ""
                
                user = await reaction.users().flatten()
                for player in user:
                    if not player.bot and player != self.ctx.message.author:
                        text_em += player.mention + "\n"
                        list_player.append(player)
                em_players = discord.Embed(title = "Les joueur qui participent au pendu sont", description = text_em, color = 0x19990c)
                await self.ctx.channel.send(embed = em_players)        
        
            
        await message_demande_joueur.delete()        
        return list_player  # member
     
       
    def choose_mot(self):
        return self.mots[random.randint(0,len(mots)-1)]
        
        
    @property 
    def mot_joueur(self): # cree le mot que peux voir le joueur et verifie si il a gagner
        new_mot = ""
       
        print(self.mot)
        for lettre in self.mot:
            if lettre in self.lettre_trouvé:
                new_mot += lettre
            else:
                new_mot +=  self.char_cache        
                
        print(new_mot) 
        return new_mot        
        # return le mot que peux voir le joueur 
        
    async def check_victoir(self):
        new_mot = self.mot_joueur
        
        if new_mot == self.mot:
            print("gagner") 
            await self.gagner() 
            self.running = False
        return new_mot == self.mot
               
        
    async def ask_letter(self):
        em_ask = discord.Embed(description = f"c'est a {self.players[self.tour%len(self.players)].mention} de choisir une lettre: \n")
        em_ask.add_field(name = "mot a trouvé:" , value = f"```{self.mot_joueur}```")
        em_ask.add_field(name = "info:", 
                         value = f"il vous reste **{self.vie}** vie \n  vous avez deja tester les lettres: \n{' | '.join(self.lettre_testé)}")
        file = discord.File(f"pendu_data/etapes/etape_{self.vie}.jpg" , filename = f"etape_{self.vie}.jpg")
        em_ask.set_thumbnail(url = f"attachment://etape_{self.vie}.jpg")
        if self.tour == 0:
            message = await self.ctx.send(file = file , embed = em_ask)
            self.id_ask = message.id
        else: 
            await self.ctx.channel.send(embed =em_ask,file = file)
            # message = await self.ctx.channel.fetch_message(self.id_ask)
            # await message.edit(file = file, embed = em_ask)
        if not await self.check_victoir():
            self.demande_reponce = True
            while self.demande_reponce:
                await asyncio.sleep(0.1)
            
            return self.reponce.lower()
        #return la lettre demander et verifie 
        else:
            return None
        
    async def check_word(self,lettre):
        if not lettre == None:
            if len(lettre) == 1:
                if lettre in self.lettre_testé:
                    em_bonne_lettre = discord.Embed(description = f"la lettre **'{lettre}'** est a deja été tester", color = 0xf8b240)
                    await self.ctx.channel.send(embed =em_bonne_lettre)
                    await self.check_word(await self.ask_letter())
                elif lettre in self.mot:
                    em_bonne_lettre = discord.Embed(description = f"la lettre **{lettre}** est bien dans le mot", color = 0xaaf786)
                    await self.ctx.channel.send(embed =em_bonne_lettre)
                    self.lettre_trouvé.append(lettre)
                    self.lettre_testé.append(lettre)
                else:
                    em_mauvaise_lettre = discord.Embed(description = f"la lettre **{lettre}** n'est pas dans le mot", color = 0xf85940)
                    await self.ctx.channel.send(embed =em_mauvaise_lettre)
                    self.lettre_testé.append(lettre)
                    self.vie -= 1 
                    if self.vie == 0:
                        await self.perdu()
                
                
    # methode fin de la game            
    async def gagner(self):
        em_victoir = discord.Embed(title ="vous avez gagné! 🎉🥇", 
                                   description = f"gg a {self.players[self.tour%len(self.players)-1].mention} qui a trouve la dernière lettre",
                                   color = 0x76d616)
        await self.ctx.channel.send(embed = em_victoir)
        self.running = False
        
    async def perdu(self):
        em_defaite = discord.Embed(title ="vous avez Perdu! 😢😡", 
                                   description = f"vous remercirez {self.players[self.tour%len(self.players)-1].mention} qui a fait la dernière erreur",
                                   color = 0xd39274)
        await self.ctx.channel.send(embed = em_defaite)
        self.running = False
    
    