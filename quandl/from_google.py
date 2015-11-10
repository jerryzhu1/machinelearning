import kragle as kg
import pandas as pd


df = pd.from_google("1vSX8gpL6nXvWyMuw18DDBmVK2YpjXvYP9dvdtelsLDA","GlobalOriginals")

titles = df[['title', 'group', 'globalfdd','launchreporting']]

print titles.sort('globalfdd')

launch_report_titles = titles[titles['launchreporting']==1]

print launch_report_titles
# for i, row in df[('title', 'group', 'globalfdd')].iterrows():
# 	print row.title

print launch_report_titles.to_json()