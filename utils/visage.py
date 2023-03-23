import os
# import cv2
import torch
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1, fixed_image_standardization
import time
import tqdm

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    import cv2

import logging

logger = logging.getLogger("cv2")
logger.setLevel(logging.ERROR)

class Visage:
    def __init__(self, reference_image_directory, embeddings_file="embeddings.npy"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.mtcnn = MTCNN(keep_all=True, device=self.device)
        self.resnet = InceptionResnetV1(pretrained="vggface2").eval().to(self.device)
        
        if os.path.isfile(embeddings_file):
            self.reference_image_embeddings = np.load(embeddings_file)
        else:
            self.reference_images = self.load_reference_images(reference_image_directory)
            self.reference_image_embeddings = self.get_embeddings(self.reference_images)
            np.save(embeddings_file, self.reference_image_embeddings)

    def load_reference_images(self, reference_image_directory):
        print("Processing the images...")
        reference_images = []
        file_names = [file_name for file_name in os.listdir(reference_image_directory) if file_name.endswith((".jpg", ".jpeg", ".png"))]
        for file_name in tqdm.tqdm(file_names, desc='Loading reference images'):
            image = cv2.imread(os.path.join(reference_image_directory, file_name))
            reference_images.append(image)
        return reference_images

    def get_embeddings(self, images):
        embeddings = []
        for image in images:
            detected_faces = self.mtcnn(image)
            if detected_faces is not None:
                detected_faces = detected_faces.to(self.device)
                embeddings.append(self.resnet(detected_faces).detach().cpu().numpy())
        return np.vstack(embeddings) if embeddings else None

    def capture_image(self):
        cap = cv2.VideoCapture(0)
        time.sleep(2)
        ret, frame = cap.read()
        cap.release()
        return frame

    def is_same_person(self, threshold=0.8):
        current_user_image = self.capture_image()
        current_user_embedding = self.get_embeddings([current_user_image])

        if current_user_embedding is None or self.reference_image_embeddings is None:
            return False
        try:
            distances = np.linalg.norm(self.reference_image_embeddings - current_user_embedding, axis=1)
            return np.any(distances < threshold) 
        except:
            print("Distance calculation failed.")
            return False
        