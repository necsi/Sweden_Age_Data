import json, requests
import pandas as pd
from datetime import datetime

def main():
    #get lastest sha of commit on master
    r = requests.get('https://api.github.com/repos/adamaltmejd/covid/branches/master')
    latest_commit_sha = r.json()['commit']['commit']['tree']['sha']
    #get the files/folders
    r = requests.get('https://api.github.com/repos/adamaltmejd/covid/git/trees/'+latest_commit_sha)
    tree = r.json()['tree']
    #get sha of data/ and get the files/folders of data/
    sha_of_dir = [i for i in tree if i['path']=='data'][0]['sha']
    r = requests.get('https://api.github.com/repos/adamaltmejd/covid/git/trees/'+sha_of_dir)
    tree = r.json()['tree']
    #get sha of data/FHM/ 
    sha_of_dir = [i for i in tree if i['path']=='FHM'][0]['sha']
    r = requests.get('https://api.github.com/repos/adamaltmejd/covid/git/trees/'+sha_of_dir)

    j = json.loads(r.content.decode())
    file_names = [i['path'] for i in j['tree']][1:]
    print(file_names)

    # Get the files and throw em together into one dataframe
    df =pd.read_excel('https://raw.githubusercontent.com/adamaltmejd/covid/master/data/FHM/'+file_names[0], sheet_name='Totalt antal per åldersgrupp').rename(columns={'Totalt_antal_fall':file_names[0][-15:-5]})
    df.index = df['Åldersgrupp']
    df = df[[file_names[0][-15:-5]]]
    the_big_dict= df.to_dict()
    for fname in file_names[1:]:
        # Using dicts here should make this slightly faster
        date=fname[-15:-5]
        print(date)
        df_temp = pd.read_excel('https://raw.githubusercontent.com/adamaltmejd/covid/master/data/FHM/'+fname, sheet_name='Totalt antal per åldersgrupp').rename(columns={'Totalt_antal_fall':date})
        df_temp.index = df_temp['Åldersgrupp']
        the_big_dict[date] = df_temp.to_dict()[date]

    df=pd.DataFrame(data=the_big_dict).fillna(0)
    df.loc['80+'] = df.loc[['Ålder_80_90', 'Ålder_90_plus', 'Ålder_80_89']].sum() #Because they changed how they stratify
    df=df.T
    df= df.reset_index().rename(columns={'index': 'Date'})
    df.to_csv('Age_Stratified.csv', index=False)

if __name__ == "__main__":
    main()