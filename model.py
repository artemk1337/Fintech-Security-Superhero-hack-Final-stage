import insightface
import numpy as np
from PIL import Image


image = Image.open('face.jpg')
model = insightface.app.FaceAnalysis()
ctx_id = -1
model.prepare(ctx_id=ctx_id)

faces = model.get(image)
for idx, face in enumerate(faces):
    print("Face [%d]:"%idx)
    print("\tage:%d"%(face.age))
    gender = 'Female' if face.gender == 0 else 'Male'
    print("\tgender:%s"%(gender))
    print("\tembedding shape:%s"%face.embedding.shape)
    print("\tbbox:%s"%(face.bbox.astype(np.int).flatten()))
    print("\tlandmark:%s"%(face.landmark.astype(np.int).flatten()))
    print("")
