from collections import defaultdict, Counter
from pandas import DataFrame, pivot_table
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

import numpy as np
from sklearn.preprocessing import StandardScaler

from bot.models import ImageModel, Reaction, MessageModel


def prepare_matrix():
    from users.models import User

    users = list(User.objects.all())
    images = list(
        ImageModel.objects.filter(category=ImageModel.ImageCategory.MAIN).all()
    )

    min_reactions = 2
    images = [
        img
        for img in images
        if Reaction.objects.filter(image=img).count() >= min_reactions
    ]

    messages = (
        MessageModel.objects.filter(images__in=images).prefetch_related("images").all()
    )
    participants = [user.id.hex for user in users] + [
        f"sender:{sender.hex}" for sender in messages.values_list("sender", flat=True)
    ]

    participant_idx = {pid: idx for idx, pid in enumerate(participants)}
    image_idx = {img.id.hex: idx for idx, img in enumerate(images)}

    matrix = np.zeros((len(participants), len(images)))

    for reaction in Reaction.objects.filter(image__in=images):
        u = participant_idx[reaction.user.id.hex]
        i = image_idx[reaction.image.id.hex]
        matrix[u][i] = 1 if reaction.react else -1

    for msg in messages:
        pid = f"sender_{msg.sender.id.hex}"
        u = participant_idx.get(pid)
        if u:
            for img in msg.images.all():
                i = image_idx.get(img.id)
                if i:
                    matrix[u][i] = 1

    if matrix.shape[1] == 0:
        return None, None, None

    scaler = StandardScaler()
    normalized_matrix = scaler.fit_transform(matrix)
    return normalized_matrix, participant_idx, image_idx


def precompute_pca_and_save():
    from django.core.cache import cache
    from sklearn.decomposition import PCA

    normalized_matrix, participant_idx, image_idx = prepare_matrix()

    if normalized_matrix is None:
        return

    pca = PCA()
    pca.fit(normalized_matrix)

    cumulative_variance = np.cumsum(pca.explained_variance_ratio_)
    n_components = np.argmax(cumulative_variance >= 0.9) + 1

    pca = PCA(n_components=n_components)
    train_reduced = pca.fit_transform(normalized_matrix)

    reversed_image_idx = {v: k for k, v in image_idx.items()}
    cache.set("normalized_matrix", normalized_matrix, timeout=None)
    cache.set("train_reduced", train_reduced, timeout=None)
    cache.set("participant_idx", participant_idx, timeout=None)
    cache.set("reversed_image_idx", reversed_image_idx, timeout=None)


def recommend_images_for_user(user, similarity_threshold=0.3):
    from django.core.cache import cache
    from sklearn.metrics.pairwise import cosine_similarity

    normalized_matrix = cache.get("normalized_matrix")
    train_reduced = cache.get("train_reduced")
    participant_idx = cache.get("participant_idx")
    idx_image = cache.get("reversed_image_idx")

    if not all(
        x is not None
        for x in [normalized_matrix, train_reduced, participant_idx, idx_image]
    ):
        return []

    participant_key = user.id.hex
    user_idx = participant_idx.get(participant_key)
    if user_idx is None:
        return []

    user_vector = train_reduced[user_idx].reshape(1, -1)
    similarities = cosine_similarity(user_vector, train_reduced).flatten()

    top_indices = np.where(similarities >= similarity_threshold)[0]
    top_indices = top_indices[top_indices != user_idx]  # Exclude self

    meme_scores = {}

    for sim_idx in top_indices:
        participant_images = normalized_matrix[sim_idx]
        for img_idx, score in enumerate(participant_images):
            if score > 0:
                img_id = idx_image[img_idx]
                meme_scores[img_id] = meme_scores.get(img_id, 0) + similarities[sim_idx]

    recommended_memes_with_scores = sorted(
        meme_scores.items(), key=lambda x: x[1], reverse=True
    )

    return [img_id for img_id, _ in recommended_memes_with_scores]
