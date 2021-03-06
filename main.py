import pandas as pd
import json
import argparse
import json
import urllib
import time
from matplotlib import pyplot as plt
import pafy
import numpy as np
from datetime import datetime
from os import path

# CONVERT - python3 main.py -f convert -d histórico_de_visualizações_3Jan.json
# JOIN -  python3 main.py -f join -d histórico_de_visualizações_3Jan.csv
# CREATE FILES - python3 main.py -f create



ap = argparse.ArgumentParser()
ap.add_argument("-f", "--function", required=True, help="Function to execute: \n\tjoin - Join historic data \n\tcreate - Create files")
ap.add_argument("-d", "--data", required=False,
	help="path to historic data")
args = vars(ap.parse_args())


# pip3 install matplotlib
# pip3 install pafy
# pip3 install youtube-dl

# Convert file from json to csv

def convert_json_to_dataframe(data):
    """
        Converts the original json file to a csv file with the correct columns

        data: json historical data
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

    df['duration_sec'] = np.nan
    df['duration_min'] = np.nan

    print('Going to create the duration columns. This might take a while....')
    df = create_duration_col(df)
    return df

def create_duration_col(df):
    """
        Uses pafy lib to get the duration of each video

        df: pandas dataframe with the historical data
    """
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
            print('Invalid URL: ', row['title_url'])

    df['duration_sec']  = seconds
    df['duration_min'] = minutes

    return df


# Join with previous historical data
def join_historic_data(df):
    """
        Joins new historic data with the previous data.
        Then, saves the new data.
        ! Assumes that the previous processed historical data is saved on the file Historic_data.csv

        df: pandas dataframe with the new data
    """

    prev_hist = pd.read_csv('Historic_data.csv') # get previous data
    prev_date = prev_hist.time.values[0]
    df = df[(df.time > prev_date)]  # only select the records that have a date higher than the previous date

    df = pd.concat([df, prev_hist])
    df.to_csv('Historic_data.csv', index=False)
    return df

# Create files and graphs
def create_files_with_aggregates(df):
    """
        This method groups and aggregates the data by multiple columns and saves the
        resulting dataframes

        df: pandas dataframe
    """
    # Save data grouped by title and channel
    df.groupby(['title', 'channel'])\
            .size()\
            .reset_index(name='counter')\
            .sort_values(by=['counter'], ascending=False)\
            .to_csv('views_by_title&channel.xlsx', index=False)\


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

    create_plots(df)
    return df

def create_plots(df):
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

    if 'duration_sec' in df.columns:

        # Top 10 most min passed videos
        aux = df.groupby(['title'])['duration_sec'].sum()/60 # get minutes
        aux = aux.round()
        plt.figure(figsize=(15, 20))
        ax = aux.nlargest(20).plot.bar(colormap='Paired')
        plt.xticks(
            rotation=60,
            horizontalalignment='right',
            fontweight='heavy',
            fontsize='small',
        )

        for spine in plt.gca().spines.values():
            spine.set_visible(False)
        for p in ax.patches:
            ax.annotate(str(p.get_height()), (p.get_x()+p.get_width()/2, p.get_height()*1.005), ha='center', fontweight='heavy',color='b', fontsize=11)
        plt.savefig('top_20_most_min_videos.jpg')


        # Top 20 most min passed CHANNELS
        aux = df.groupby(['channel'])['duration_sec'].sum()/60 # get minutes
        aux = aux.round()
        plt.figure(figsize=(15, 20))
        ax = aux.nlargest(20).plot.bar(colormap='Paired')
        plt.xticks(
            rotation=60,
            horizontalalignment='right',
            fontweight='heavy',
            fontsize='small',
        )

        for spine in plt.gca().spines.values():
            spine.set_visible(False)
        for p in ax.patches:
            ax.annotate(str(p.get_height()), (p.get_x()+p.get_width()/2, p.get_height()*1.005), ha='center', fontweight='heavy',color='b', fontsize=11)
        plt.savefig('top_20_most_min_channels.jpg')


        # Top 20 days with most minutes passed on youtube
        df['time'] = pd.to_datetime(df['time'])
        df['date_day'] = df['time'].dt.date
        aux = df.groupby(['date_day'])['duration_sec'].sum()/60 # get minutes
        aux = aux.round()

        plt.figure(figsize=(15, 20))
        ax = aux.nlargest(20).plot.bar(colormap='Paired')
        plt.xticks(
            rotation=60,
            horizontalalignment='right',
            fontweight='heavy',
            fontsize='small',
        )

        for spine in plt.gca().spines.values():
            spine.set_visible(False)
        for p in ax.patches:
            ax.annotate(str(p.get_height()), (p.get_x()+p.get_width()/2, p.get_height()*1.005), ha='center', fontweight='heavy',color='b', fontsize=11)
        plt.savefig('top_20_days_most_min.jpg')


def main():
    f = args['function']
    path = args['data']
    if f == 'convert':
        if path is None:
            print('Error: you have to provide the path for the new file!')
            return
        with open(path) as json_file:
            data = json.load(json_file)
        df = convert_json_to_dataframe(data)
        df.to_csv(path.replace('json', 'csv'), index=False)
        if not path.exists("Historic_data.csv"):
            df.to_csv("test.csv", index=False)
    elif f == 'create':
        if path is None:
            print('Error: you have to provide the path for the csv file!')
            return
        df = pd.read_csv('test.csv')
        create_files_with_aggregates(df)
    elif f == 'join':
        if path is None:
            print('Error: you have to provide the path for the new csv file!')
            return
        df = pd.read_csv(path) # new data
        join_historic_data(df)
    else:
        print('Invalid function input!')
        return



if __name__ == "__main__":
    main()