import sqlite3
import functools

nom_table = "argent_user"


def connect(func):
    
    @functools.wraps(func)
    def new_func(*arg, connection = None,cursor = None):
        print(func.__name__)
        if connection == None:
            #print("connection = None")
            try:
                connection = sqlite3.connect("info_members.db")
                #print(arg)
                cursor = connection.cursor()# initialise le curseur
                returned_value = func(*arg,connection = connection,cursor = cursor)
                connection.close()
                return returned_value
            except Exception as e :
                print("[ERROR]", e)
        else:
            #print("connected")
            cursor = connection.cursor()# initialise le curseur
            returned_value = func(*arg,connection = connection,cursor = cursor)
            return returned_value
    return new_func
  
  
# fonction primaire
#@connect
def search_conected(table,colomns, value, colomns_returned, connection = None,cursor = None):
    """recherche un valeur dans une table données
    Arguments:
        table {str} -- non de la tablee ou l'on cherche un donnée
        colomns {str} -- nom de la colonm concerner par la recherche
        value {all} -- valeur recherchée
        colomns_returned {str} -- colons retouré aprés la recherche 

    Keyword Arguments:
        connection {} -- connection avec db (default: {None})
        cursor {} -- curseur de la db (default: {None})

    Returns:
        [all] -- [value return by the search]
    """
    value = (value,)
    cursor.execute(f"SELECT {colomns_returned} FROM {table} WHERE {colomns} = ?" , value)
    valeur = cursor.fetchone()
    return valeur 

@connect
def search(table,colomns, value, colomns_returned, connection = None,cursor = None):
    """recherche un valeur dans une table données
    Arguments:
        table {str} -- non de la tablee ou l'on cherche un donnée
        colomns {str} -- nom de la colonm concerner par la recherche
        value {all} -- valeur recherchée
        colomns_returned {str} -- colons retouré aprés la recherche )
    Returns:
        [all] -- [value return by the search]
    """
    value = (value,)
    cursor.execute(f"SELECT {colomns_returned} FROM {table} WHERE {colomns} = ? " , value)
    valeur = cursor.fetchone()
    return valeur 


@connect
def update_value(table,colomns,new_value, colone_repert, value_repert, connection = None,cursor = None):
    """upadate une valeur avec une condition = 

    Arguments:
        table {str} -- nom de la table
        colomns {str} -- colone concerner par le changement
        new_value {all} -- nouvelle value a mettre
        colone_repert {str} -- colone pour la condition
        value_repert {all} -- valeur de la condition
    """
    try:
        values = (new_value, value_repert)
        cursor.execute(f"UPDATE {table} SET {colomns} = ? WHERE {colone_repert} = ?", values)
        connection.commit()
    except Exception as e :
        print("[ERROR /update_value/ ] : \n",e)

@connect
def execute_search(str, value, connection = None,cursor = None):
    """execute une requete sql

    Arguments:
        str {str} -- request sql
        value {tuple} -- valeur a mettre a la place des "?"

    Returns:
        [tuple] -- [value retourné par la requete]
    """
    try:
        req = cursor.execute(str, value) # todo
        return req.fetchall()
    except Exception as e :
        print("[ERROR]", e)
    


@connect
def show_table(row = None, connection = None,cursor = None):
    if row == None:
        req = cursor.execute("SELECT * FROM argent_user")
        for row in req.fetchall():
            print(row)
    elif type(row) == list:
        pass
   
@connect 
def add_item(table_name, values, auto_increment_id, connection = None,cursor = None):
    """add_item in a databose

    Arguments:
        table_name {str} -- nom de la table
        values {tuple} -- value a asigner pour chaques colones
        auto_increment_id {bool} -- if we add an auto_increment id in the tuple
    """
    if auto_increment_id :
        values = (cursor.lastrowid,) + values
    print(values)
    cursor.execute(f"INSERT INTO {table_name} VALUES({'?'+',?'*(len(values)-1)})", values)
    connection.commit()
    
        
        
          
 # fonction complexes
@connect
def add_user(id_discord ,argent, connection = None,cursor = None):
    """ajoute un utilisateur a la base de données
    Arguments:
        id_discord {int} -- id de l'utilisateur sur discord
        argent {int} -- argent que possède l'utilisateur
    """
    new_user = (cursor.lastrowid,id_discord,argent)
    cursor.execute(f"INSERT INTO {nom_table} VALUES(?,?,?)", new_user)
    connection.commit()
    print("un nouvelle utilisateur a été ajouter")
    
    

@connect
def add_new_pari(data,connection = None,cursor = None):
    """ajoute un pari a la database

    Arguments:
        data {tuple} -- donnés a enregistrer
    """
    try:
        #print(data)
        id_message,id_channel, title, props = data
        data_in_db = (cursor.lastrowid,id_message,id_channel,title,props)
        table_pari = "pari"
        cursor.execute(f"INSERT INTO {table_pari} VALUES(?,?,?,?,?)", data_in_db)
        connection.commit()
        
    except Exception as e :
        print("[ERROR]", e)
        connection.rollback()
        

@connect
def add_pari(data,connection = None,cursor = None):
    """ajoute une nouveau pari dans l'historique
    Arguments:
        data {tuple} -- id_discord , question , reponce , amount

    Keyword Arguments:
        connection {[type]} -- [description] (default: {None})
        cursor {[type]} -- [description] (default: {None})
    """
    print(data)
    id_discord, question, reponce ,amount = data
    reponce = int(reponce)
    amount = int(amount)
    try:
        id_pari = search_conected("pari","question", question,"id_pari", connection = connection,cursor = cursor) # ?, connection = connection,cursor = cursor
        id_pari = int(id_pari[0])
        print(id_pari)
        add_money(id_discord,amount*-1,connection = connection,cursor = cursor)
        data_in_db = (id_discord,id_pari,question,amount, reponce)
        table_pari = "historique_pari"
        cursor.execute(f"INSERT INTO {table_pari} (id_discord, id_pari, question, amount, reponce) VALUES(?,?,?,?,?)", data_in_db)
        connection.commit()
        return True
            
    except Exception as e :
        print("[ERROR: /add_pari/ ]", e)
        connection.rollback()
        return False
        
@connect   
def add_money(id_discord, amount, connection = None, cursor = None):
    """ajoute ou eleve de l'argent au joueur

    Arguments:
        id_discord {int} -- id de la personne sur discord
        amont {int} -- quantité gagné / perdu (pour enlever de l'argent amount dois etre negatif)

    Returns:
        Bool -- return false if the person dont have enought money 
    """
    argent_par_default = 500
    values = (id_discord,)
    cursor.execute("SELECT argent FROM argent_user WHERE id_discord = ?" ,values)
    player_money = cursor.fetchone()
    if player_money == None:
        add_user(id_discord, argent_par_default) #?, connection = connection,cursor = cursor
        player_money = (argent_par_default,)
    
    player_money = int(player_money[0])
    new_money = player_money+ int(amount)
    if new_money<0:
        return False
    else:
        update_value("argent_user","argent", new_money, "id_discord", id_discord)
        return True 


@connect
def delete(table, condition,values,connection = None, cursor = None):
    """permet de delete des ligne en fonction d'une condition

    Arguments:
        table {str} -- nom de la table 
        condition {str} -- condition
        values {tuple} -- valeurs utiliser a la place des "?"
    """
    try:
        cursor.execute(f"DELETE FROM {table} WHERE {condition} ", values)
        connection.commit()
    except Exception as e :
        print("[ERROR /delete/ ]", e)
        connection.rollback()
        