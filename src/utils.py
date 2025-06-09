import numpy as np

# 余弦相似度Cosine Similarity）的标准范围是[-1, 1]
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))