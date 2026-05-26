import streamlit as st
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConfigurationError

@st.cache_resource
def get_db():
    try:
        uri = st.secrets.get("MONGO_URI", "")
    except FileNotFoundError:
        st.error(
            "⚠️ **Arquivo de configuração não encontrado.**\n\n"
            "Crie o arquivo `.streamlit/secrets.toml` com sua URI do MongoDB Atlas."
        )
        st.stop()
    
    if not uri or "<" in uri:
        st.error(
            "⚠️ **MongoDB não configurado.**\n\n"
            "**Passo 1:** Acesse [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)\n"
            "**Passo 2:** Crie um cluster (gratuito) e um usuário de banco\n"
            "**Passo 3:** Copie a connection string\n"
            "**Passo 4:** Edite `.streamlit/secrets.toml`:\n\n"
            "```\n"
            "MONGO_URI = \"mongodb+srv://seguro:Seguro2026Teste@cluster0.saq8sca.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0\"\n"
            "```\n\n"
            "Substitua `usuario`, `senha` e `seu-cluster` pelos seus dados reais."
        )
        st.stop()
    
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        return client["psi_si"]
    except (ServerSelectionTimeoutError, ConfigurationError) as e:
        st.error(f"❌ **Erro ao conectar ao MongoDB:** {str(e)}")
        st.stop()
