from random import randint
import ast
import asyncio
import time


import discord

from info import em_error, em_call_back, em_jail
import use_data_base as db 

async def pari(ctx, title , reponce , amount):
    call_back = db.add_pari((ctx.message.author.id, title, reponce, amount))
    
    if call_back : 
        await em_call_back(ctx,f"votre pari de {amount} $ a bien été enregistré")
    else:
        await em_error(ctx,f"vous n'avez pas asser d'argent pour parier {amount} $")


async def show_money(ctx):
    argent_par_default = 500
    argent = db.search("argent_user", "id_discord", ctx.author.id, "argent")
    if not argent:
        db.add_user(ctx.author.id, argent_par_default)
        argent = (argent_par_default,)
    argent = int(argent[0])
    em_money = discord.Embed(title = "🏦 __Compte en banque__ 💰" ,
                             description = f"{ctx.author.display_name} a : **{argent}** $",
                             color = 0x24c6c8)
    em_money.set_thumbnail(url = ctx.author.avatar_url)
    await ctx.channel.send(embed = em_money)

async def show_money_of(ctx, user):
    argent_par_default = 500
    argent = db.search("argent_user", "id_discord", user.id, "argent")
    if not argent:
        db.add_user(user.id, argent_par_default)
        argent = (argent_par_default,)
    argent = int(argent[0])
    em_money = discord.Embed(title = "🏦 __Compte en banque__ 💰" ,
                             description = f"{user.display_name} a : **{argent}** $",
                             color = 0x24c6c8)
    em_money.set_thumbnail(url = ctx.author.avatar_url)
    await ctx.channel.send(embed = em_money)
    
async def top_list(ctx):
    top_list = db.execute_search("SELECT * FROM argent_user ORDER BY argent DESC LIMIT 3", ())
    one,two,tree = top_list
    text = f"""
    
    🥇 {ctx.guild.get_member(one[1]).mention}
        ➥ : **{one[2]}** $
        
    🥈 {ctx.guild.get_member(two[1]).mention}
        ➥ : **{two[2]}** $ 
        
    🥉 {ctx.guild.get_member(tree[1]).mention}
     ➥ : **{tree[2]}** $
    """
    print(text)
    em_top_list = discord.Embed(title = "🏦 - Liste des personne les plus riches - 💰",
                                description = text, 
                                color = 0x24c6c8)
    await ctx.channel.send(embed = em_top_list)
    

async def end_pari(ctx,title,reponce_gagnante):
    """met fin au paris et distribut l'argent au personne qui ont parier

    Arguments:
        ctx {contxt} --  
        title {str} -- titre du sondage que l'on veux arreter
        reponce_gagnante {int} -- numero de la reponce gagnante (commence a partir de 1)
    """
    id_message = db.search("pari", "question" ,title,"id_message_discord")
    channel_id = db.search("pari", "question" ,title,"channel_id")
    channel_id = int(channel_id[0])
    if id_message == None:
        await em_error(ctx," il n'y a pas de pari qui porte ce titre")
    elif ctx.channel.id != channel_id:
        await em_error(ctx,f"ce paris n'existe pas dans ce channel cherche dans le channel{ctx.guild.get_channel(channel_id).name}")
    else: 
        gagnants = db.execute_search("SELECT * FROM historique_pari WHERE question = ? AND reponce = ?", (title,reponce_gagnante))
        #print(gagnants)
        perdant = db.execute_search("SELECT amount FROM historique_pari WHERE question = ? AND NOT reponce = ?", (title,reponce_gagnante))
        list_perte = [int(argent[0]) for argent in perdant]
        list_argent_pari_won = [int(info[4]) for info in gagnants]
        print(list_perte)
        argent_pari_won = sum(list_argent_pari_won)
        perte = sum(list_perte)
        #print(argent_pari_won)
        print("[end_sondage] perte :",perte) 
        
        #   todo redistribuer l'argent / suprimer les data sur ce pari 
        
        # redistribuer l'argent : 
        for gagnant in gagnants: 
            amount_bet = int(gagnant[4])
            amount_win = amount_bet / argent_pari_won
            print("[end_sondage] amount_win : ",amount_win)
            argent_user = db.search("argent_user", "id_discord", gagnant[1] , "argent")
            print("[end_sondage] argent de celui qui a parier",int(argent_user[0]))
            money_win =int(argent_user[0]) + int(amount_win*(perte+argent_pari_won)+1)
            print("[end_sondage] money_win",money_win)
            db.update_value("argent_user", "argent",money_win, "id_discord", gagnant[1])
            
        # info pari
        info_pari = db.execute_search("SELECT * FROM pari WHERE question = ? ", (title,))
        reponce =  ast.literal_eval(info_pari[0][4])[int(reponce_gagnante) -1]
        # delete data 
        db.delete("historique_pari", "question = ?" , (title,))
        db.delete("pari", "question = ?" , (title,))
        
        
        
        await em_call_back(ctx,f"le pari {title} est finis", description = f"finalement la reponce est : \n  - {reponce}")
        
        
        
             



async def paye(ctx, mention, amount): 
    try :
        argent_author = db.search("argent_user", "id_discord", ctx.message.author.id, "argent")
        argent_author = int(argent_author[0])
        if argent_author >= amount:
            db.update_value("argent_user","argent", argent_author - amount, "id_discord", ctx.message.author.id)  # enlever l'argent_user
            print("l'argent a été enlevé")
            argent_receveur = db.search("argent_user", "id_discord", mention.id, "argent")
            argent_receveur = int(argent_receveur[0])
            db.update_value("argent_user", "argent", argent_receveur + amount , "id_discord", mention.id)# donner l'argent_user
            await em_call_back(ctx,
                            f"Vous venez de donner {amount} $ a {mention.display_name}",
                            description = f"vous avez maintenant : {argent_author -amount} $")
        else:
            await em_error(ctx,f"vous n'avez pas l'argent pour payer {amount} $")
            
    except Exception as e :
        await em_error(ctx, e)    
        return False
    
is_catch = {} # tuple (user, bool)
async def catch(ctx, stealer):
    global is_catch
    if stealer in is_catch:
        print(stealer.name , " part en prison")
        is_catch[stealer] = True
        await em_jail(ctx, user = stealer)
        del is_catch[stealer]
    else:
        await em_error(ctx, 
                       "cette personne n'est pas un vouleur (pour le moment)")
        
def add_steal_in_db(id, steal_time: float):
    table_name = "steal_history"
    time_last_steal = db.search(table_name, "id_discord", id, "time_last_steal")
    if time_last_steal == None:
        db.add_item(table_name, (id, steal_time), True)
        return True
    elif time_last_steal[0] + 3_600 <= time.time(): # 1 heure de delais entre chaques voles
        db.update_value(table_name, 
                        "time_last_steal",
                        float(time.time()),
                        "id_discord",
                        id)
        return True
    else:
        return False
        
        
    
        
        
async def steal(ctx, user):
    """steal money

    Arguments:
        ctx {context} -- ...
        user {discord.User} -- user who lose his money
    """
    if ctx.message.author == user:
        await em_error(ctx, "vous ne pouvez pas vous voulez vous même")
        return None
    
    success = add_steal_in_db(ctx.message.author.id, time.time())
    if success:
        global is_catch
        rand_int_try = randint(1, 10)
        if rand_int_try != 5:
            print("stealing")
            amount = randint(1, 100)
            await em_call_back(ctx, ctx.message.author.name + " a voler de l'argent a : " + user.name,
                            description=user.mention + "fait la command !catch " + ctx.message.author.mention +" pour l'envoyer en prison") #todo finish taht
            is_catch[ctx.message.author] = False
            await asyncio.sleep(60) 
            try:
                catch = is_catch[ctx.message.author]
            except KeyError:
                catch = True
            if not catch : 
                await em_call_back(ctx, ctx.message.author.name+ " a reussi son vole, il gagne donc "+ amount+ "€")
                # steal money
                
                # todo verifier que l'argent ne passe pas en negatif
                if db.search("argent_user", "id_discord", user.id, "argent")-amount >=0:
                    db.add_money(user.id, -amount) # retirer l'argent
                    db.add_money(ctx.message.author.id, amount)
                else:
                    print(user.name, "a eu les yeux plus gros que le ventre")
                    await em_error(ctx, "la personne que vous vollez n'as pas asser d'argent")
            else:
                return None
        else: 
            print(ctx.message.author.name, " a rater son vole, il part en prison")   
            await em_jail(ctx)
            db.update_value("steal_history", "time_last_steal", 0, "id_discord", ctx.message.author.name)
    else:
        await em_error(ctx, "vous devez vous reposer au moins 1h entre chaques voles")
            
            