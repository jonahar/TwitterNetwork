import os
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

documents_dir = '/cs/labs/avivz/jonahar/Twitter/bitcoin_btc_documents'
documents = os.listdir(documents_dir)
documents = [os.path.join(documents_dir, d) for d in documents]

num_topics = 10
words_in_topic = 10


def print_topics(model, vectorizer, top_n=10):
    for idx, topic in enumerate(model.components_):
        print("Topic %d:" % (idx))
        print([vectorizer.get_feature_names()[i] for i in topic.argsort()[:-top_n - 1:-1]])


NUM_TOPICS = 10

vectorizer = CountVectorizer(input='filename', min_df=5, max_df=0.9,
                             stop_words='english', lowercase=True,
                             token_pattern='[a-zA-Z\-][a-zA-Z\-]{2,}')
data_vectorized = vectorizer.fit_transform(documents)

# Build a Latent Dirichlet Allocation Model
lda_model = LatentDirichletAllocation(n_topics=num_topics, max_iter=20, learning_method='online')
lda_Z = lda_model.fit_transform(data_vectorized)
print_topics(lda_model, vectorizer)
