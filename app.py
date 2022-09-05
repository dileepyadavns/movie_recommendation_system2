
from unittest import result
import numpy as np
import pandas as pd
from flask import Flask, render_template, request
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import bs4 as bs
import urllib.request
import pickle
import json
import requests
from datetime import datetime

# load the nlp model and tfidf vectorizer from disk
# filename = 'nlp_model.pkl'
# clf = pickle.load(open(filename, 'rb'))
# vectorizer = pickle.load(open('tranform.pkl','rb'))

# def create_similarity():
#     data = pd.read_csv('main_data.csv')
#     data=data.iloc[:100,:]
#     # creating a count matrix
#     cv = CountVectorizer()
#     count_matrix = cv.fit_transform(data['comb'])
#     # creating a similarity score matrix
#     similarity = cosine_similarity(count_matrix)
#     return data,similarity

# def rcmd(m):
#     m = m.lower()
#     try:
#         data.head()
#         similarity.shape
#     except:
#         data, similarity = create_similarity()
#     # if m not in data['movie_title'].unique():
#     #     return('Sorry! The movie you requested is not in our database. Please check the spelling or try with some other movies')
    
#     if m in data['genres'].unique():
#         i=data.loc[data['geres']==m].index[0]
#         lst = list(enumerate(similarity[i]))
#         lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
#         lst = lst[1:11] # excluding first item since it is the requested movie itself
#         l = []
#         for i in range(len(lst)):
#             a = lst[i][0]
#             l.append(data['movie_title'][a])
#         return l

        


#     else:
#         i = data.loc[data['movie_title']==m].index[0]
#         lst = list(enumerate(similarity[i]))
#         lst = sorted(lst, key = lambda x:x[1] ,reverse=True)
#         lst = lst[1:11] # excluding first item since it is the requested movie itself
#         l = []
#         for i in range(len(lst)):
#             a = lst[i][0]
#             l.append(data['movie_title'][a])
#         return l
    
# # converting list of string to list (eg. "["abc","def"]" to ["abc","def"])
# def convert_to_list(my_list):
#     my_list = my_list.split('","')
#     my_list[0] = my_list[0].replace('["','')
#     my_list[-1] = my_list[-1].replace('"]','')
#     return my_list

# def get_suggestions():
#     data = pd.read_csv('main_data.csv')
#     return list(data['movie_title'].str.capitalize())



import psycopg2 #pip install psycopg2 
import psycopg2.extras
import pandas as pd

conn = psycopg2.connect( #psycopg2 database adaptor for implementing python
         host="localhost",
        database="students",
       user='postgres',
      password='p@ssw0rd')

app = Flask(__name__)


@app.route("/similarity",methods=["GET","POST"])
def similarity():
    data = pd.read_csv('main_data.csv')
    data=data.iloc[:10][:]
    m_str=list(data['movie_title'].str.capitalize())
    return m_str



# def recommend():
#     data = pd.read_csv('main_data.csv')
#     data=data.iloc[:500,:]

#     m_str=list(data['movie_title'].str.capitalize())
    
#     return render_template('recommend.html',movies=m_str)

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/home", methods=['POST','GET'])
def home():


   
    username = request.form.get('username')
    password = request.form.get('password')
    cur = conn.cursor()
    with conn:
        cur.execute(f"SELECT * FROM user_details WHERE username=%(username)s AND password=%(password)s",
                    {'username': username, 'password': password})

        if cur.fetchall():
                data = pd.read_csv('main_data.csv')
                data=data.iloc[:10,:]
                dt = datetime.now()
                login_date_time = dt
                cur.execute('INSERT INTO  user_activity(time,username) VALUES(%s,%s) ', ( dt,username))
                conn.commit()


                token= '5492165c61b1a21c06eb3a3b578a6339'
                arr= list(data['movie_title'].str.capitalize())
                ppath=[]
                for i in arr:
                    response = requests.get("https://api.themoviedb.org/3/search/movie?api_key="+token+"&query="+i).json()
                    try:
                        path= 'https://image.tmdb.org/t/p/original'+str(response['results'][0]['poster_path'])
                        new={
                           "name": i,
                           "src": path,
                            "count": 0
                            }
                        ppath.append(new)
                    except IndexError:
                         pass  
             



                return render_template('recommend.html',ppath=ppath)     
    
     
@app.route("/path",methods=['GET', 'POST'])
def view():
        # updated = request.form.get('updated')
        information = request.data
        my_json = information.decode('utf8')
        data = json.loads(my_json)

        information = json.dumps(data, indent=4, sort_keys=True).replace("'", '"')  
        
        # data = json.load(information)
        print(information)
        cur = conn.cursor()
        for i in data:
            print(i['count'])
          
            if i['count']>0 :
                print(i['name'])
                cur.execute('INSERT INTO  user_activity(movie,clicks) VALUES(%s,%s) ', (i['name'], i['count'],))
                conn.commit()
        
        return information

if __name__ == '__main__':
    app.run(debug=True)

