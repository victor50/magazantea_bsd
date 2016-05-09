#-*- coding: utf-8 -*-

def FornitoriSalvaInICEC(my_dict):
    from magazantea.my_settings import HOST_LOC,HOST_VPN
    from magazzino.prog_servizio import EseguiQuery
    import psycopg2
    from decimal import Decimal
    try:
        conn = psycopg2.connect("dbname='magazicec' user='antea' host='"+HOST_LOC+"' password='antea'")
    except:
        try:
            conn = psycopg2.connect("dbname='magazicec' user='antea' host='"+HOST_VPN+"' password='antea'")
        except:
            print "Non riesco a connettermi al database"
    cur = conn.cursor()
    sql_cerca_in_fornitori_ICEC ='select * from fornitori where id = '+str(my_dict['id'])
    # Verifica se l'id fornitore è già in magazicec
    cur.execute(sql_cerca_in_fornitori_ICEC)
    ris = cur.fetchall()
    # Se sì, fai un update di tutte le colonne del record in magazicec previa pulizia anomalie
    if ris:
        for i in my_dict.keys():
            if my_dict[i] == None:
                my_dict[i] = ''
# PostgreSQL vuole il simbolo ' per delimitare una stringa di caratteri. Se però nella
# stringa è presente ' come accento occorre fare un escape del carattere semplicemnte
# sostituendo ' di inizio-fine stringa con $$
# Così ad es. 'PIE' DI LUCO' diventa $$PIE' DI LUCO$$
        cur.execute("UPDATE fornitori SET datains = "+"$$"+str(my_dict['data_di_inserimento']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET datamod = "+"$$"+str(my_dict['data_di_modifica']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET creato_da = "+"$$"+str(my_dict['creato_da']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET modificato_da = "+"$$"+str(my_dict['modificato_da']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET nome = "+"$$"+str(my_dict['nome']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET indirizzo = "+"$$"+str(my_dict['indirizzo']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET cap = "+"$$"+str(my_dict['cap']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET localita = "+"$$"+str(my_dict['localita']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET prov = "+"$$"+str(my_dict['provincia']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET nazione = "+"$$"+str(my_dict['nazione']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET telefono = "+"$$"+str(my_dict['telefono']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET fax = "+"$$"+str(my_dict['fax']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET cellulare = "+"$$"+str(my_dict['cellulare']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET email = "+"$$"+str(my_dict['email']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET piva = "+"$$"+str(my_dict['partita_iva']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET cf = "+"$$"+str(my_dict['cf']) +"$$ where id =" + str(my_dict['id']))
        cur.execute("UPDATE fornitori SET note = "+"$$"+str(my_dict['note']) +"$$ where id =" + str(my_dict['id']))
        conn.commit()
        print("Record "+str(my_dict['id'])+" AGGIORNATO")
    # Se no, inserisci nuovo record in magazicec previa pulizia anomalie
    else:
        for i in my_dict.keys():
            if my_dict[i] == None:
                my_dict[i] = ''
        sql = "INSERT INTO fornitori VALUES ("
        sql += str(my_dict['id'])+",$$"+str(my_dict['data_di_inserimento'])+"$$,$$"+str(my_dict['data_di_modifica'])+"$$,$$"+my_dict['creato_da']+"$$,$$"+my_dict['modificato_da']+"$$,$$"+my_dict['nome']+"$$,$$"+my_dict['indirizzo']+"$$,$$"+my_dict['cap']+"$$,$$"+my_dict['localita']+"$$,$$"+my_dict['provincia']+"$$,$$"+my_dict['nazione']+"$$,$$"+my_dict['telefono']+"$$,$$"+my_dict['fax']+"$$,$$"+my_dict['cellulare']+"$$,$$"+my_dict['email']+"$$,$$"+my_dict['partita_iva']+"$$,$$"+my_dict['cf']+"$$,$$"+my_dict['note']+"$$)"
        print sql
        cur.execute(sql)
        conn.commit()
    return


