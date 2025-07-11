import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def generate_wordcloud_from_csv(csv_file_path):
    # Read the CSV file
    df = pd.read_csv(csv_file_path)

    # Ensure the DataFrame contains the necessary columns
    if 'tokenized_word' not in df.columns or 'count' not in df.columns:
        raise ValueError("CSV file must contain 'tokenized_word' and 'count' columns")

    # Convert the data into a dictionary suitable for word cloud
    word_freq = dict(zip(df['tokenized_word'], df['count']))

    # Generate the word cloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(word_freq)

    # Display the word cloud
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.show()


