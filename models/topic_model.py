from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation

def get_topics(docs, n_topics=3):
    """
    Performs Latent Dirichlet Allocation (LDA) to find topics in documents.
    """
    if not docs or all(d.strip() == "" for d in docs):
        return ["Not enough text data to generate topics."]
        
    vectorizer = CountVectorizer(stop_words='english', max_df=0.9, min_df=2)
    try:
        X = vectorizer.fit_transform(docs)
    except ValueError:
        return ["Text is too sparse to find topics. Need more unique words."]

    if X.shape[1] == 0:
        return ["No relevant vocabulary found after filtering stop words."]

    lda = LatentDirichletAllocation(n_components=n_topics, random_state=42)
    lda.fit(X)
    
    words = vectorizer.get_feature_names_out()
    topics = []
    for idx, topic in enumerate(lda.components_):
        top_words_idx = topic.argsort()[:-6:-1] # Get top 5 words
        top_words = [words[i] for i in top_words_idx]
        topics.append(f"Topic {idx + 1}: {', '.join(top_words)}")
        
    return topics