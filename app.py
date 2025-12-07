import streamlit as st
from pymongo import MongoClient
import gridfs
import numpy as np
from PIL import Image
import io

# ----------------- CONEXÃO -------------------

uri = "mongodb+srv://amandafgomes_db_user:juq5dX$rhqN9G!S@cluster0.fxvo9rw.mongodb.net/?appName=Cluster0"
client = MongoClient(uri)
db = client["fei_database"]
fs = gridfs.GridFS(db)

# ----------------- CARREGAR BASE FEI -------------------

def carregar_base():
    imagens = []
    nomes = []

    for arq in fs.find():
        dados = arq.read()
        imagem = Image.open(io.BytesIO(dados)).convert("L")
        imagem = np.array(imagem)

        imagens.append(imagem)
        nomes.append(arq.filename)

    return np.array(imagens), nomes

dataset, nomes_dataset = carregar_base()

# ----------------- COMPARAÇÃO -------------------

def comparar_imagem(imagem_usuario, dataset):
    diffs = []

    for img in dataset:
        dif = np.sum(abs(img - imagem_usuario))
        diffs.append(dif)

    diffs = np.array(diffs)
    idx_min = np.argmin(diffs)

    return idx_min, diffs[idx_min]

# ----------------- INTERFACE -------------------

st.title("Comparador Facial FEI")

uploaded = st.file_uploader("Envie uma imagem JPG", type=["jpg","jpeg"])

if uploaded is not None:
    imagem_user = Image.open(uploaded).convert("L")
    imagem_user_np = np.array(imagem_user)

    st.image(imagem_user, caption="Imagem enviada", use_container_width=True)

    st.subheader("Comparando...")

    idx, distancia = comparar_imagem(imagem_user_np, dataset)

    st.success(f"Rosto mais parecido encontrado: {nomes_dataset[idx]}")

    # Mostrar imagem mais parecida
    dado = fs.find_one({"filename": nomes_dataset[idx]}).read()
    imagem_parecida = Image.open(io.BytesIO(dado))

    st.image(imagem_parecida, caption="Rosto mais semelhante encontrado")
