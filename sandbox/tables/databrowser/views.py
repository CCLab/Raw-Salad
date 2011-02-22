from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import Context, loader
from django.utils import simplejson as json

import psycopg2
import psycopg2.extras



def main_page( request ):
    return render_to_response( "databrowser.html" )

def first_table( request ):
    data = get_data_i()
    return HttpResponse( json.dumps( data ));

def second_table( request ):
    data = get_data_ii()
    return HttpResponse( json.dumps( data ));


def get_data_i():
#postgres select + group by
    conn_postgres = psycopg2.connect("user='postgres' host='localhost' password='marcinbarski' dbname='cclpoll'")
    cur = conn_postgres.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT k.plec AS "_id_kand_plec", k.typ AS "_id_kand_typ", k.jednostka AS "_id_kand_jednostka", k.szczebel AS "_id_kand_szczebel",
                SUM(k.l_glosow) AS "value_kand_glosow_total", COUNT(*) as "value_rec_count"
        FROM kandydaci_rady k
        GROUP BY k.plec, k.typ, k.jednostka, k.szczebel
        ORDER BY value_kand_glosow_total DESC, k.plec, k.typ, k.jednostka, k.szczebel
    """)
    rows = cur.fetchall()
    out= []
    for row in rows:
        dict_id= {'kand_plec':row['_id_kand_plec'], 'kand_typ':row['_id_kand_typ'], 'kand_jednostka':row['_id_kand_jednostka'], 'kand_szczebel':row['_id_kand_szczebel']}
        dictval= {'kand_glosow_total':row['value_kand_glosow_total'], 'rec_count':row['value_rec_count']}
        dictrow= {'_id':dict_id, 'value':dictval}
        out.append(dictrow)
    conn_postgres.close()
    return out
#plain table
"""
    return [{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"slaskie","kand_szczebel":"sejmik"},"value":{"kand_glosow_sum":856271,"recs":505}},{"_id":{"kand_plec":"K","kand_typ":"partia","kand_jednostka":"slaskie","kand_szczebel":"sejmik"},"value":{"kand_glosow_sum":386308,"recs":241}},{"_id":{"kand_plec":"M","kand_typ":"organizacja","kand_jednostka":"slaskie","kand_szczebel":"sejmik"},"value":{"kand_glosow_sum":108105,"recs":82}},{"_id":{"kand_plec":"M","kand_typ":"wyborczy","kand_jednostka":"slaskie","kand_szczebel":"sejmik"},"value":{"kand_glosow_sum":46457,"recs":132}},{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"Czestochowa","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":44538,"recs":129}},{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"Katowice","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":38399,"recs":158}},{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"Sosnowiec","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":34586,"recs":114}},{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"bielski","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":30805,"recs":124}},{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"bedzinski","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":28641,"recs":112}},{"_id":{"kand_plec":"M","kand_typ":"wyborczy","kand_jednostka":"zywiecki","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":28536,"recs":121}},{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"Gliwice","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":26909,"recs":113}},{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"Bielsko-Biala","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":26837,"recs":124}},{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"czestochowski","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":24955,"recs":136}},{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"zawiercianski","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":24262,"recs":117}},{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"cieszynski","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":23002,"recs":90}},{"_id":{"kand_plec":"K","kand_typ":"partia","kand_jednostka":"Katowice","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":22943,"recs":64}},{"_id":{"kand_plec":"M","kand_typ":"partia","kand_jednostka":"zywiecki","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":22549,"recs":124}},{"_id":{"kand_plec":"K","kand_typ":"wyborczy","kand_jednostka":"slaskie","kand_szczebel":"sejmik"},"value":{"kand_glosow_sum":22350,"recs":44}},{"_id":{"kand_plec":"M","kand_typ":"wyborczy","kand_jednostka":"Bielsko-Biala","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":19881,"recs":59}},{"_id":{"kand_plec":"M","kand_typ":"wyborczy","kand_jednostka":"Katowice","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":19832,"recs":51}}]
"""

def get_data_ii():
#postgres select + group by
    conn_postgres = psycopg2.connect("user='postgres' host='localhost' password='marcinbarski' dbname='cclpoll'")
    cur = conn_postgres.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute("""
        SELECT k.jednostka AS "_id_kand_jednostka", k.szczebel AS "_id_kand_szczebel",
                COUNT(*) as "value_rec_count", SUM(k.l_glosow) AS "value_kand_glosow_total"
        FROM kandydaci_rady k
        GROUP BY k.jednostka, k.szczebel
        ORDER BY value_rec_count DESC, k.jednostka, k.szczebel
    """)
    rows = cur.fetchall()
    out= []
    for row in rows:
        dict_id= {'kand_jednostka':row['_id_kand_jednostka'], 'kand_szczebel':row['_id_kand_szczebel']}
        dictval= {'kand_glosow_total':row['value_kand_glosow_total'], 'rec_count':row['value_rec_count']}
        dictrow= {'_id':dict_id, 'value':dictval}
        out.append(dictrow)
    conn_postgres.close()
    return out

#plain table
"""
    return [{"_id":{"kand_jednostka":"slaskie","kand_szczebel":"sejmik"},"value":{"kand_glosow_sum":856271,"recs":505}},{"_id":{"kand_jednostka":"slaskie","kand_szczebel":"sejmik"},"value":{"kand_glosow_sum":386308,"recs":241}},{"_id":{"kand_jednostka":"slaskie","kand_szczebel":"sejmik"},"value":{"kand_glosow_sum":108105,"recs":82}},{"_id":{"kand_jednostka":"slaskie","kand_szczebel":"sejmik"},"value":{"kand_glosow_sum":46457,"recs":132}},{"_id":{"kand_jednostka":"Czestochowa","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":44538,"recs":129}},{"_id":{"kand_jednostka":"Katowice","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":38399,"recs":158}},{"_id":{"kand_jednostka":"Sosnowiec","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":34586,"recs":114}},{"_id":{"kand_jednostka":"bielski","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":30805,"recs":124}},{"_id":{"kand_jednostka":"bedzinski","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":28641,"recs":112}},{"_id":{"kand_jednostka":"zywiecki","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":28536,"recs":121}},{"_id":{"kand_jednostka":"Gliwice","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":26909,"recs":113}},{"_id":{"kand_jednostka":"Bielsko-Biala","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":26837,"recs":124}},{"_id":{"kand_jednostka":"czestochowski","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":24955,"recs":136}},{"_id":{"kand_jednostka":"zawiercianski","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":24262,"recs":117}},{"_id":{"kand_jednostka":"cieszynski","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":23002,"recs":90}},{"_id":{"kand_jednostka":"Katowice","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":22943,"recs":64}},{"_id":{"kand_jednostka":"zywiecki","kand_szczebel":"powiat"},"value":{"kand_glosow_sum":22549,"recs":124}},{"_id":{"kand_jednostka":"slaskie","kand_szczebel":"sejmik"},"value":{"kand_glosow_sum":22350,"recs":44}},{"_id":{"kand_jednostka":"Bielsko-Biala","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":19881,"recs":59}},{"_id":{"kand_jednostka":"Katowice","kand_szczebel":"miasto na prawach powiatu"},"value":{"kand_glosow_sum":19832,"recs":51}}]
"""
