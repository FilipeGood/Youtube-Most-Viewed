import pandas as pd
import json
import argparse
import json
import urllib
import time
from matplotlib import pyplot as plt
import pafy
from datetime import datetime
# CONVERT - python3 main.py -f convert -d histórico_de_visualizações_3Jan.json
# JOIN -  python3 main.py -f join -d histórico_de_visualizações_3Jan.jsonArguments:  join ,  histórico_de_visualizações_3Jan.json
# CREATE FILES - python3 main.py -f create




"""
#! Download youtube data:
    - http://google.com/takeout

# ? TODO
    - More functions in create files

    - Graphs

    - Get minutes of each video
    - Total number of minutes by day
    - "Interface" like this: https://www.youtube.com/watch?v=hkhyKJj28Ac&list=WL&index=18&ab_channel=KalleHallden
"""


ap = argparse.ArgumentParser()
ap.add_argument("-f", "--function", required=True, help="Function to execute: \n\tjoin - Join historic data \n\tcreate - Create files")
ap.add_argument("-d", "--data", required=False,
	help="path to historic data")
args = vars(ap.parse_args())




def create_files(df):

    # df = df.drop('url') # ! -------------------------------------------

    # Save data grouped by title and channel
    df.groupby(['title', 'channel']).size().reset_index(name='counter').sort_values(by=['counter'], ascending=False).to_csv('views_by_title&channel.xlsx', index=False)


    # Views by channel
    df['channel'].value_counts().to_csv('views_by_channel.xlsx')

    # Views by day
    days = list()
    for t in df['time'].str.split('T'):
        # t[0] => day !!!  t[1] => time
        days.append(t[0])
    df['day'] = days

    df.groupby(['day']).size().reset_index(name='counter').to_csv('views_by_day.xlsx', index=False)


    # Views by day of week
    df['day'] = pd.to_datetime(df['day'])
    df['day_of_week'] = df['day'].dt.day_name()
    df.groupby(['day_of_week']).size().reset_index(name='counter').to_csv('views_by_day_week.xlsx', index=False)

    create_graphs(df)

def create_graphs(df):
    # fig_size(width, height)

    # Top 10 most viewed channels
    plt.figure(figsize=(15,15))
    ax = df['channel'].value_counts().nlargest(10).plot.bar( colormap='Paired')
    plt.xticks(
        rotation=45,
        horizontalalignment='right',
        fontweight='heavy',
        fontsize='medium',
    )
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x()+p.get_width()/2, p.get_height()*1.005), ha='center', fontweight='heavy',color='b', fontsize=11)
    plt.savefig('top_10_channels.jpg')

    # Top 10 most viewed videos
    df['title'] = df['title'].str.replace('Watched', ' ')
    df['title'] = df['title'].str.replace('\\[Official Music Video\\]', ' ')
    plt.figure(figsize=(15,15))
    ax = df['title'].replace('Watched', '').value_counts().nlargest(10).plot.bar(colormap='Paired')
    plt.xticks(
        rotation=45,
        horizontalalignment='right',
        fontweight='heavy',
        fontsize='medium',
    )
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x()+p.get_width()/2, p.get_height()*1.005), ha='center', fontweight='heavy',color='b', fontsize=11)
    plt.savefig('top_10_titles.jpg')

    # Views by day of week
    plt.figure(figsize=(15,15))
    plt.xticks(
        rotation=45,
        horizontalalignment='right',
        fontweight='heavy',
        fontsize='medium',
    )
    ax = df['day_of_week'].value_counts().plot.bar(colormap='Paired')
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x()+p.get_width()/2, p.get_height()*1.005), ha='center', fontweight='heavy',color='b', fontsize=11)
    plt.savefig('views_by_day_of_week.jpg')


    # Top 10 days views
    plt.figure(figsize=(15,15))
    plt.xticks(
        rotation=45,
        horizontalalignment='right',
        fontweight='heavy',
        fontsize='medium',
    )
    ax = df['day'].dt.strftime('%Y-%m-%d').value_counts().nlargest(10).plot.bar(colormap='Paired')
    for spine in plt.gca().spines.values():
        spine.set_visible(False)
    for p in ax.patches:
        ax.annotate(str(p.get_height()), (p.get_x()+p.get_width()/2, p.get_height()*1.005), ha='center', fontweight='heavy',color='b', fontsize=11)
    plt.savefig('top_10_days_views.jpg')

    # Line with the number of views per day
    plt.figure(figsize=(15,15))
    plt.xticks(
        rotation=45,
        horizontalalignment='right',
        fontweight='heavy',
        fontsize='medium',
    )
    df.groupby(['day']).size().plot(kind='line', colormap='Paired')
    plt.savefig('days_views.jpg')
    #plt.show()

def convert_json_to_dataframe(data):
    """
        Converts the original json file to a csv file with the correct columns
    """
    new_list = list()
    for obj in data:
        if 'titleUrl' not in  obj:
            continue

        header = obj['header']
        title = obj['title']
        title_url = obj['titleUrl']
        channel = ''
        if 'subtitles' in obj:
            channel = obj['subtitles'][0]['name']
        time = obj['time']
        new_list.append([header, title, title_url, channel, time])

    df = pd.DataFrame(new_list, columns=['header', 'title', 'title_url', 'channel', 'time'])
    return df

def create_duration_col(df):
    seconds = list()
    minutes = list()
    for index, row in df.iterrows():
        try:
            url = row['title_url']
            video = pafy.new(url)
            duration =  datetime.strptime(video.duration, '%H:%M:%S')

            seconds.append(duration.minute*60 + duration.second )
            minutes.append(duration)
        except:
            seconds.append(None)
            minutes.append(None)
            print('Upssss: ', row['title_url'])


    df['duration_sec']  = seconds
    df['duration_min'] = minutes

    return df



def join_historic_data(df):
    """
        Joins new historic data with the previous data.
        Then, saves the new data
    """
    prev_hist = pd.read_csv('Historic_data.csv')
    prev_date = prev_hist.time.values[0]
    df = df[(df.time > prev_date)]

    # create duration columns of the new dataframe
    # it is better to do here than in the function convert_json_to_dataframe because the dataframe is smaller
    df = create_duration_col(df)

    df = pd.concat([df, prev_hist])
    print(df.shape)
    df.to_csv('Historic_data.csv', index=False)
    return df

def save_historic_data_as_csv(df):
    """
        ? Not being used!
        Just a json to csv converter
    """
    path = args['data']
    path = path.replace('.json', '')
    return df.to_csv(f'{path}.csv', index=False)

def main():
    f = args['function']
    path = args['data']
    print('Arguments: ', f, ', ', path)
    if f == 'convert':
        if path is None:
            print('Error: you have to provide the path for the new file!')
            return
        with open(path) as json_file:
            data = json.load(json_file)

        df = convert_json_to_dataframe(data)
        df.to_csv(path.replace('json', 'csv'), index=False)
    elif f == 'join':
        if path is None:
            print('Error: you have to provide the path for the new file!')
            return
        print('-'+path+'-')
        df = pd.read_json(path)
        df = join_historic_data(df)

    elif f == 'create':
        df = pd.read_csv('Historic_data.csv')
        create_files(df)
    return
if __name__ == "__main__":
    main()
    """
    df = pd.read_csv('Historic_data.csv')
    df = create_duration_col(df)
    df.to_csv('Historic_data1.csv', index=False)
    """

    #df = json_to_dataframe(data)

    # 15,267
    # 18 101

    #df = pd.read_json(path)
    #df.to_csv('test.csv')
    #print(df)
    #save_historic_data_as_csv(df)
    #create_files(df)