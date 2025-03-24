# %%
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.config import Settings
from uuid import uuid4

# %%
# init embedding
embeddings = HuggingFaceEmbeddings(model_name='distiluse-base-multilingual-cased-v2', model_kwargs={"device" : "cuda"})

# Init Chroma
vector_store = Chroma(
    collection_name="drugs",
    embedding_function=embeddings,
    persist_directory="./chroma_db",
    client_settings=Settings(
        chroma_api_impl="chromadb.api.fastapi.FastAPI",
        chroma_server_host="localhost",
        chroma_server_http_port=8000
    )
)

# %%
import json

with open('drug_checkpoint.json') as data:
    drugs_data = json.load(data)
    data.close()

drugs_data

# %%
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=300,
    chunk_overlap=50
)

# %%
for drug in drugs_data:
    chunks = text_splitter.split_text(drug['content'])     
    chunk_ids = [f"{drug['drugName']}_{i}" for i in range(len(chunks))]  # Unique ID for each chunk

    # 🔍 Step 1: Check if documents already exist (Batch Query)
    existing_docs = vector_store.get(ids=chunk_ids)  # Fetch in bulk

    # 🔄 Step 2: Filter out existing documents
    new_docs = []
    new_ids = []
    
    for i, chunk in enumerate(chunks):
        if chunk_ids[i] not in existing_docs['ids']:  # If not found, add to insertion list
            new_docs.append(Document(page_content=chunk, metadata={"drug_name": drug['drugName'], "source": "drugs.com"}))
            new_ids.append(chunk_ids[i])

    # 🚀 Step 3: Insert only new documents
    if new_docs:
        vector_store.add_documents(new_docs, ids=new_ids)
        print(f'Inserted drug: {drug["drugName"]} ({len(new_docs)} new chunks)')
    else:
        print(f'Skipped drug: {drug["drugName"]} (already exists)')


# %%
results = vector_store.similarity_search(
    "I need drug because my ear is feel weird and it kinda pain",
    k=10,
)
for res in results:
    print(f"* {res.page_content} [{res.metadata}]")

# %%



