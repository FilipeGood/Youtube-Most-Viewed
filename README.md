# Youtube-Most-Viewed
Try to replicate the "spotify year in review".

I mainly use Youtube to listen to music so I really wanted something like the "spotify year in review" piece. 

This repo, reads your historical youtube data (you need to provide the csv) and them produces multiple graphs and insights about your activity on youtube.
If you want, you can use this repo to find out what are your youtube patterns. Just follow the steps.

### Step 1 
**Download youtube historical data**
- Go to this website - http://google.com/takeout
- Select only "Youtube and Youtube Music"
![alt text](https://github.com/FilipeGood/Youtube-Most-Viewed/blob/main/Readme%20Images/Screenshot%20from%202021-01-23%2020-18-58.png)

- Change the download format to JSON
- Download :)



### Step 2
- After you have downloaded the file, uncompress it
- run the following command - `python3 main.py -f convert -d *<file_name.json>*`
- This method will convert the json file into a csv file. It will also create other columns that will be useful later
![alt text](![alt text](https://github.com/FilipeGood/Youtube-Most-Viewed/blob/main/Readme%20Images/top_10_titles.jpg))
![alt text](![alt text](https://github.com/FilipeGood/Youtube-Most-Viewed/blob/main/Readme%20Images/views_by_day_of_week.jpg))



### Step 3
- Run the following command - `python3 main.py -f create`
- This will create multiple xlsx file and multiple graphs
- You can use the xlsx files and the graphs to explore your youtube usage



### Join previous historic data with new one
- If you have a new historica data file, you can join the old one with the new one 
- Run the following command -  `python3 main.py -f join -d *<new_file_name.csv>*`






**If you run in to any problem or have extra ideas, feel free to contact me via linkedin https://www.linkedin.com/in/filipe-good/**
