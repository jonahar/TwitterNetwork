import os
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

documents_dir = '/cs/labs/avivz/jonahar/Twitter/bitcoin_btc_documents'
documents_names = os.listdir(documents_dir)
documents_paths = [os.path.join(documents_dir, d) for d in documents_names]

num_topics = 10
words_in_topic = 10


def print_topics(model, vectorizer, top_n=10):
    for idx, topic in enumerate(model.components_):
        print("Topic %d:" % (idx))
        print([vectorizer.get_feature_names()[i] for i in topic.argsort()[:-top_n - 1:-1]])


def top_users_in_topic(topic_idx, lda_Z, threshold=0.9, max_users=0):
    """
    print all users with probability to be related to topic 'topix_idx' at least 'threshold'.

    :param topic_idx:
    :param lda_Z:
    :param threshold:
    :param max_users:
    :return:
    """
    topic = lda_Z[:, topic_idx]
    threshold_indices = np.where(topic >= threshold)[0]  # users above threshold
    top_indices = topic.argsort()[-max_users:]  # top max_users users
    indices = np.intersect1d(threshold_indices, top_indices, assume_unique=True)
    return [documents_names[i] for i in indices]


vectorizer = CountVectorizer(input='filename', min_df=5, max_df=0.9,
                             stop_words='english', lowercase=True,
                             token_pattern='[a-zA-Z\-][a-zA-Z\-]{2,}')
data_vectorized = vectorizer.fit_transform(documents_paths)

# Build a Latent Dirichlet Allocation Model
lda_model = LatentDirichletAllocation(n_topics=num_topics, max_iter=20, learning_method='online')
lda_Z = lda_model.fit_transform(data_vectorized)
print_topics(lda_model, vectorizer)
topix_idx = ...  # manually find the wanted topic
users = top_users_in_topic(topix_idx, lda_Z, threshold=0.6)
