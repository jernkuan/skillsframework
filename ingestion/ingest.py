import openai
import qdrant_client
import streamlit as st
import pandas as pd
from dataclasses import dataclass, asdict
from qdrant_client.models import VectorParams, Distance, PointStruct

openai_client = openai.Client(api_key=st.secrets.openai.api_key)

client = qdrant_client.QdrantClient(
    url=f"{st.secrets.qdrant.host}:{st.secrets.qdrant.port}",
    api_key=st.secrets.qdrant.api_key,
)

df = pd.read_excel(
    "ingestion/SkillsFramework_Dataset_2024_06.xlsx",
    sheet_name="Job Role_Description",
    header=0,
)

@dataclass
class JobRole:
    sector: str
    track: str
    role: str
    description: str


job_roles = [
    JobRole(row["Sector"], row["Track"], row["Job Role"], row["Job Role Description"])
    for _, row in df.iterrows()
]

texts = [job_role.description for job_role in job_roles]

embedding_model = "text-embedding-3-small"

result = openai_client.embeddings.create(input=texts, model=embedding_model)

points = [
    PointStruct(
        id=idx,
        vector=data.embedding,
        payload=asdict(job_role),
    )
    for idx, (data, job_role) in enumerate(zip(result.data, job_roles))
]

collection_name = "skillsframework"

client.create_collection(
    collection_name,
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE,
    ),
)

for i in range(0, len(points), 50):
    client.upsert(collection_name, points[i : i + 50])
