import csv
import pandas as pd

# Create output directory if it does not exist
import os
if not os.path.exists('output'):
    os.makedirs('output')

header = None
# Read first row from csv file and use it as a header
with open('metrics_meta.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=';', quotechar='|')
    header = next(reader)

# read data from csv file using header
data = None
data = pd.read_csv('metrics_meta.csv', delimiter=';', encoding='utf-8', decimal=',')


# Create histogram from values_bitrate
import matplotlib.pyplot as plt
import numpy as np

# Convert values_bitrate to float
values_bitrate = [float(i) for i in data['input_bitrate']]
values_length = [float(i) for i in data['duration_original']]
values_resolution = [float(i / 1000000) for i in data['resolution']] # Divide resolution by 1 million to get megapixels
#values_resolution = [float(i) for i in data['resolution']] # Divide resolution by 1 million to get megapixels
values_si_avg = [float(i) for i in data['si_avg']]
values_si_min = [float(i) for i in data['si_min']]
values_si_max = [float(i) for i in data['si_max']]
values_si_std = [float(i) for i in data['si_std']]
values_ti_avg = [float(i) for i in data['ti_avg']]
values_ti_min = [float(i) for i in data['ti_min']]
values_ti_max = [float(i) for i in data['ti_max']]
values_ti_std = [float(i) for i in data['ti_std']]

#year;digg_count;share_count;play_count;comment_count;author_fans;author_following;author_heart;author_video;author_digg
values_year = [int(i) for i in data['year']]
values_digg_count = [int(i) for i in data['digg_count']]
values_share_count = [int(i) for i in data['share_count']]
values_play_count = [int(i) for i in data['play_count']]
values_comment_count = [int(i) for i in data['comment_count']]
values_author_fans = [int(i) if not np.isnan(i) else 0 for i in data['author_fans']]
values_author_following = [int(i) if not np.isnan(i) else 0 for i in data['author_following']]
values_author_heart = [int(i) if not np.isnan(i) else 0 for i in data['author_heart']]
values_author_video = [int(i) if not np.isnan(i) else 0 for i in data['author_video']]
values_author_digg = [int(i) if not np.isnan(i) else 0 for i in data['author_digg']]


# Create bitrate histogram
plt.hist(values_bitrate, bins=100)
plt.title("Bitrate")
plt.xlabel("Bitrate [kbps]")
plt.ylabel("Frequency")

# Save histogram to file in output directory
plt.savefig('output/bitrate_histogram.svg', format="svg")
plt.savefig('output/bitrate_histogram.png', format="png")

# Create length histogram
plt.clf()
plt.hist(values_length, bins=100)
plt.title("Length")
plt.xlabel("Length [s]")
plt.ylabel("Frequency")

# Save histogram to file in output directory
plt.savefig('output/length_histogram.png')
plt.savefig('output/length_histogram.svg', format='svg')

# Create resolution histogram
plt.hist(values_resolution, bins=100)
plt.title("Resolution")
plt.xlabel("Resolution [Mpx]")
plt.ylabel("Frequency")
plt.xlim(0, 100)

# Save histogram to file in output directory
plt.savefig('output/resolution_histogram.png')
plt.savefig('output/resolution_histogram.svg', format='svg')

# Create si_avg histogram
plt.clf()
plt.hist(values_si_avg, bins=100)
plt.title("SI Average")
plt.xlabel("SI value")
plt.ylabel("Frequency")

# Save histogram to file in output directory
plt.savefig('output/si_avg_histogram.png')
plt.savefig('output/si_avg_histogram.svg', format='svg')

# Create si_min histogram
plt.clf()
plt.hist(values_si_min, bins=100)
plt.title("SI Minimum")
plt.xlabel("SI value")
plt.ylabel("Frequency")

# Save histogram to file in output directory
plt.savefig('output/si_min_histogram.png')
plt.savefig('output/si_min_histogram.svg', format='svg')

# Create si_max histogram
plt.clf()
plt.hist(values_si_max, bins=100)
plt.title("SI Maximum")
plt.xlabel("SI value")
plt.ylabel("Frequency")

# Save histogram to file in output directory
plt.savefig('output/si_max_histogram.png')
plt.savefig('output/si_max_histogram.svg', format='svg')

# Create si_std histogram
plt.clf()
plt.hist(values_si_std, bins=100)
plt.title("SI Standard Deviation")
plt.xlabel("SI Standard Deviation")
plt.ylabel("Frequency")

# Save histogram to file in output directory
plt.savefig('output/si_std_histogram.png')
plt.savefig('output/si_std_histogram.svg', format='svg')

# Create ti_avg histogram
plt.clf()
plt.hist(values_ti_avg, bins=100)
plt.title("TI Average")
plt.xlabel("TI value")
plt.ylabel("Frequency")

# Save histogram to file in output directory
plt.savefig('output/ti_avg_histogram.png')
plt.savefig('output/ti_avg_histogram.svg', format='svg')

# Create ti_min histogram
plt.clf()
plt.hist(values_ti_min, bins=100)
plt.title("TI Minimum")
plt.xlabel("TI value")
plt.ylabel("Frequency")

# Save histogram to file in output directory
plt.savefig('output/ti_min_histogram.png')
plt.savefig('output/ti_min_histogram.svg', format='svg')

# Create ti_max histogram
plt.clf()
plt.hist(values_ti_max, bins=100)
plt.title("TI Maximum")
plt.xlabel("TI Maximum")
plt.ylabel("Frequency")

# Save histogram to file in output directory
plt.savefig('output/ti_max_histogram.png')
plt.savefig('output/ti_max_histogram.svg', format='svg')


print(np.unique(values_year))
unique_years, counts = np.unique(values_year, return_counts=True)
# Create year column bar chart
plt.clf()
plt.bar(unique_years, counts)
plt.title("Year")
plt.ylabel("Frequency")

# Set the number of tick labels to display
num_labels = 2

# Determine the step size for tick labels
step = int(len(unique_years) / (num_labels - 1))
print(step)

# Set the tick locations and labels
plt.xticks(unique_years, rotation=45)

# Save histogram to file in output directory
plt.savefig('output/year_histogram.png', format="png")
plt.savefig('output/year_histogram.svg', format="svg")

# Create a figure with two rows and one column
fig, axes = plt.subplots(1, 2, figsize=(20, 8))

# Row 1: SI Values
# SI Average histogram
axes[0].hist(values_si_avg, bins=100)
axes[0].set_title("SI Average")
axes[0].set_xlabel("SI Average")
axes[0].set_ylabel("Frequency")

"""
# SI Standard Deviation histogram
axes[0].hist(values_si_std, bins=100, alpha=0.8)
axes[0].set_title("SI Average, SI Standard Deviation")
axes[0].set_xlabel("SI Value")
axes[0].set_ylabel("Frequency")
axes[0].legend(["SI Average", "SI Standard Deviation"])
"""


# SI Minimum histogram
axes[0].hist(values_si_min, bins=100, alpha=0.8)
axes[0].set_title("SI Average, SI Minimum")
axes[0].set_xlabel("SI Value")
axes[0].set_ylabel("Frequency")
axes[0].legend(["SI Average", "SI Standard Deviation", "SI Minimum"])

# SI Maximum histogram
axes[0].hist(values_si_max, bins=100, alpha=0.8)
axes[0].set_title("SI Average, SI Minimum, SI Maximum")
axes[0].set_xlabel("SI Value")
axes[0].set_ylabel("Frequency")
axes[0].legend(["SI Average", "SI Minimum", "SI Maximum"])

# Row 2: TI Values
# TI Average histogram
axes[1].hist(values_ti_avg, bins=100)
axes[1].set_title("TI Average")
axes[1].set_xlabel("TI Average")
axes[1].set_ylabel("Frequency")

"""
# TI Standard Deviation histogram
axes[1].hist(values_ti_std, bins=100, alpha=0.8)
axes[1].set_title("TI Average, TI Standard Deviation")
axes[1].set_xlabel("TI Value")
axes[1].set_ylabel("Frequency")
axes[1].legend(["TI Average", "TI Standard Deviation"])
"""

# TI Minimum histogram
axes[1].hist(values_ti_min, bins=100, alpha=0.8)
axes[1].set_title("TI Average, TI Standard Deviation, TI Minimum")
axes[1].set_xlabel("TI Value")
axes[1].set_ylabel("Frequency")
axes[1].legend(["TI Average", "TI Standard Deviation", "TI Minimum"])

# TI Maximum histogram
axes[1].hist(values_ti_max, bins=100, alpha=0.8)
axes[1].set_title("TI Average, TI Minimum, TI Maximum")
axes[1].set_xlabel("TI Value")
axes[1].set_ylabel("Frequency")
axes[1].legend(["TI Average", "TI Minimum", "TI Maximum"])

# Adjust the spacing between subplots
plt.tight_layout()

# Save the combined histogram to a file in the output directory
plt.savefig('output/combined_histogram.png')
plt.savefig('output/combined_histogram.svg', format='svg')

# Show the combined histogram
#plt.show()


# Create digg count histogram
plt.clf()
plt.hist(values_digg_count, bins=100)
plt.title("Digg Count")
plt.xlabel("Digg Count")
plt.ylabel("Frequency")
plt.savefig('output/digg_count_histogram.png')
plt.savefig('output/digg_count_histogram.svg', format='svg')

# Create share count histogram
plt.clf()
plt.hist(values_share_count, bins=100)
plt.title("Share Count")
plt.xlabel("Share Count")
plt.ylabel("Frequency")
plt.savefig('output/share_count_histogram.png')
plt.savefig('output/share_count_histogram.svg', format='svg')

# Create play count histogram
plt.clf()
plt.hist(values_play_count, bins=100)
plt.title("Play Count")
plt.xlabel("Play Count")
plt.ylabel("Frequency")
plt.savefig('output/play_count_histogram.png')
plt.savefig('output/play_count_histogram.svg', format='svg')

# Create comment count histogram
plt.clf()
plt.hist(values_comment_count, bins=100)
plt.title("Comment Count")
plt.xlabel("Comment Count")
plt.ylabel("Frequency")
plt.savefig('output/comment_count_histogram.png')
plt.savefig('output/comment_count_histogram.svg', format='svg')

# Create author fans histogram
plt.clf()
plt.hist(values_author_fans, bins=100)
plt.title("Author Fans")
plt.xlabel("Author Fans")
plt.ylabel("Frequency")
plt.savefig('output/author_fans_histogram.png')
plt.savefig('output/author_fans_histogram.svg', format='svg')

# Create author following histogram
plt.clf()
plt.hist(values_author_following, bins=100)
plt.title("Author Following")
plt.xlabel("Author Following")
plt.ylabel("Frequency")
plt.savefig('output/author_following_histogram.png')
plt.savefig('output/author_following_histogram.svg', format='svg')

# Create author heart histogram
plt.clf()
plt.hist(values_author_heart, bins=100)
plt.title("Author Heart")
plt.xlabel("Author Heart")
plt.ylabel("Frequency")
plt.savefig('output/author_heart_histogram.png')
plt.savefig('output/author_heart_histogram.svg', format='svg')

# Create author video histogram
plt.clf()
plt.hist(values_author_video, bins=100)
plt.title("Author Video")
plt.xlabel("Author Video")
plt.ylabel("Frequency")
plt.savefig('output/author_video_histogram.png')
plt.savefig('output/author_video_histogram.svg', format='svg')

# Create author digg histogram
plt.clf()
plt.hist(values_author_digg, bins=100)
plt.title("Author Digg")
plt.xlabel("Author Digg")
plt.ylabel("Frequency")
plt.savefig('output/author_digg_histogram.png')
plt.savefig('output/author_digg_histogram.svg', format='svg')



fig, axs = plt.subplots(2, 2, figsize=(15, 10))

# Plot digg_count histogram
axs[0, 0].hist(values_digg_count, bins=100)
axs[0, 0].set_title('Digg Count')
axs[0, 0].set_xlabel('Digg Count')
axs[0, 0].set_ylabel('Frequency')

# Plot share_count histogram
axs[0, 1].hist(values_share_count, bins=100)
axs[0, 1].set_title('Share Count')
axs[0, 1].set_xlabel('Share Count')
axs[0, 1].set_ylabel('Frequency')

# Plot play_count histogram
axs[1, 0].hist(values_play_count, bins=100)
axs[1, 0].set_title('Play Count')
axs[1, 0].set_xlabel('Play Count')
axs[1, 0].set_ylabel('Frequency')

# Plot comment_count histogram
axs[1, 1].hist(values_comment_count, bins=100)
axs[1, 1].set_title('Comment Count')
axs[1, 1].set_xlabel('Comment Count')
axs[1, 1].set_ylabel('Frequency')

# Global title
plt.suptitle('Video Engagement Analysis Histograms', fontsize=16)

# Enhance layout
plt.tight_layout()
#plt.show()

# Save the whole subplot to file
fig.savefig('output/count_histograms.png')
fig.savefig('output/count_histograms.svg', format='svg')


fig, axs = plt.subplots(2, 3, figsize=(20, 10))

# Plot author_fans histogram
axs[0, 0].hist(values_author_fans, bins=100)
axs[0, 0].set_title('Author Fans')
axs[0, 0].set_xlabel('Author Fans')
axs[0, 0].set_ylabel('Frequency')

# Plot author_following histogram
axs[0, 1].hist(values_author_following, bins=100)
axs[0, 1].set_title('Author Following')
axs[0, 1].set_xlabel('Author Following')
axs[0, 1].set_ylabel('Frequency')

# Plot author_heart histogram
axs[0, 2].hist(values_author_heart, bins=100)
axs[0, 2].set_title('Author Heart')
axs[0, 2].set_xlabel('Author Heart')
axs[0, 2].set_ylabel('Frequency')

# Plot author_video histogram
axs[1, 0].hist(values_author_video, bins=100)
axs[1, 0].set_title('Author Video')
axs[1, 0].set_xlabel('Author Video')
axs[1, 0].set_ylabel('Frequency')

# Plot author_digg histogram
axs[1, 1].hist(values_author_digg, bins=100)
axs[1, 1].set_title('Author Digg')
axs[1, 1].set_xlabel('Author Digg')
axs[1, 1].set_ylabel('Frequency')

# Leave the last subplot empty
axs[1, 2].axis('off')

# Global title
plt.suptitle('Author Analysis Histograms', fontsize=16)

# Enhance layout
plt.tight_layout()
#plt.show()

# Save the whole subplot to file
fig.savefig('output/author_histograms.png')
fig.savefig('output/author_histograms.svg', format='svg')


