from flask import Flask, send_file, render_template, request
import os
import glob
import pandas as pd
import datetime
#from werkzeug.import secure file_name
from werkzeug.utils import secure_filename, send_file

app = Flask('__name__')
app.config['UPLOAD_FOLDER'] = 'uploader/'

@app.route('/')
def upload_file():
    return render_template('index.html')

#main
@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file1():
    if request.method == 'POST':
        files = request.files.getlist("file")
        
        #save the files in the selected folder
        for file in files:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))

        #calling merge function
        merge = merger()            
        #res =  merge.to_html(classes='data', header='true', index='false')
        df = pd.read_csv("master.csv")
        res =  df.to_html(classes='data', header='true', index='false')
        return render_template("master.html", data=[res], titles=merge.columns.values, index=False)

#DOWNLOAD CSV BUTTON FOR MASTER 
@app.route('/download')
def download_file():
        path = "./master.csv"
        return send_file(path,as_attachment=True, environ=request.environ)

#DOWNLOAD CSV BUTTON FOR UE FORMAT
@app.route('/download_UE')
def download_file1():
        path = "./processed_UE.csv"
        return send_file(path,as_attachment=True, environ=request.environ)

#DOWNLOAD CSV BUTTON FOR TNB FORMAT
@app.route('/download_TNB')
def download_file2():
        path = "./processed_TNB.csv"
        return send_file(path,as_attachment=True, environ=request.environ)

def merger():
 #access
        listfiles = glob.glob("uploader/*.csv")

        list_dir=[]
        for i in listfiles:
           
            df_for_concat = pd.read_csv(i, index_col=None)
            list_dir.append(df_for_concat)
        
        result = pd.concat(list_dir, ignore_index=True, join='inner')
       
        #Export to csv
        result.to_csv( "master.csv", index=False, encoding='utf-8-sig')
        
        return result

#UE Format Page
@app.route('/UE_format', methods = ['GET', 'POST'])
def UE_format():
    if request.method == 'POST':
        files = glob.glob('uploader/*')

        df = UE_clean()
        res = df.to_html(classes='data', header='true')

        #Export to csv
        df.to_csv( "processed_UE.csv", index=False, encoding='utf-8-sig')
        
        for f in files:
            os.remove(f)

        return render_template("EU.html", data=[res], titles=df.columns.values, index=False)

#Data Cleaning for UE Format
def UE_clean():
    
    df = pd.read_csv("master.csv")

    #remove unwanted columns
    df.drop(df.columns[[1,8,9,10,11,15,16,17,18,19,
                        21,22,23,24,25,26,27,28,29,
                        30,31,32,33,34,35,36,37,38,
                        39,40,41,42,43,44,45,46,47,
                        48,49,50,51]], axis=1, inplace=True)
    
    #pitch and roll have zero value
    df[df.columns[4]] = 0
    df[df.columns[5]] = 0
    df[df.columns[4]]=df[df.columns[4]].map('{:,.0f}'.format)
    df[df.columns[5]]=df[df.columns[5]].map('{:,.0f}'.format)

    #longitude and latitude has 6 d.p
    df[df.columns[1]]=df[df.columns[1]].map('{:,.6f}'.format)
    df[df.columns[2]]=df[df.columns[2]].map('{:,.6f}'.format)


    #rename columns
    df.columns =['filename', 'latitude','longitude','height',
                    'roll','pitch','heading','date','time',
                    'unix_time_sec','distancetoprevious']

    #drop rows when latitud and longitud = 0 
    df.drop(df.loc[df['latitude']==0].index, inplace=True)
    df.drop(df.loc[df['longitude']==0].index, inplace=True)

    #create new column named datetime
    df['date'] = df['date'].str.split('-').str[0] + df['date'].str.split('-').str[1] + df['date'].str.split('-').str[2]
    df['datetime'] = df['date']+ ' ' +  df['time']
    
    #Change datetime format
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d %H:%M:%S')

    #Create datetime index and convert it to Asia/Singapore timezone
    df.index = pd.to_datetime(df['datetime'], utc=True)
    df.index = df.index.floor('S').tz_convert('Asia/Singapore')

    #Replace 'date' and 'time' values
    df['time'] = df.index.time
    df['date'] = df.index.date

    #Reset datetime index
    df.reset_index(drop=True, inplace=True)

    #Remove column datetime column
    df.drop(df.columns[[11]], axis=1, inplace=True)

    return df

#TNB Format Page
@app.route('/TNB_format', methods = ['GET', 'POST'])
def TNB_format():
    if request.method == 'POST':
        files = glob.glob('uploader/*')

        df = TNB_clean()
        res =  df.to_html(classes='data', header='true')
    
        #Export to csv
        df.to_csv( "processed_TNB.csv", index=False, encoding='utf-8-sig')
        
        for f in files:
            os.remove(f)
            
        return render_template("TNB.html", data=[res], titles=df.columns.values, index=False)

def TNB_clean():

    df = pd.read_csv("master.csv")

    #remove unwanted columns for TNB format
    df.drop(df.columns[[1,4,8,9,10,11,14,15,16,17,18,19,
                        20,21,22,23,24,25,26,27,28,29,
                        30,31,32,33,34,35,36,37,38,
                        39,40,41,42,43,44,45,46,47,
                        48,49,50,51]], axis=1, inplace=True)

    #rename columns
    df.columns =['filename', 'latitude','longitude',
                    'roll','pitch','heading','date','time',]

    #drop rows when latitud and longitud = 0 
    df.drop(df.loc[df['latitude']==0].index, inplace=True)
    df.drop(df.loc[df['longitude']==0].index, inplace=True)

    #longitud and latitud has
    df[df.columns[1]]=df[df.columns[1]].map('{:,.6f}'.format)
    df[df.columns[2]]=df[df.columns[2]].map('{:,.6f}'.format)

    #create new column named 'datetime'
    df['date'] = df['date'].str.split('-').str[0] + df['date'].str.split('-').str[1] + df['date'].str.split('-').str[2]
    df['datetime'] = df['date']+ ' ' +  df['time']    

    #format datetime
    df['datetime'] = pd.to_datetime(df['datetime'], format='%Y%m%d %H:%M:%S')

    #create datetime index and convert it to 'Asia/Singapore' timezone
    df.index = pd.to_datetime(df['datetime'], utc=True)
    df.index = df.index.floor('S').tz_convert('Asia/Singapore')

    #Replace the value in column "date" and "time" based on datetime index value
    df['time'] = df.index.time
    df['date'] = df.index.date
    
    #Remove datetime column
    df.drop(df.columns[[8]], axis=1, inplace=True)
    
    #Reset datetime index
    df.reset_index(drop=True, inplace=True)

    return df
    


    