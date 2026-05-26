from pymongo import MongoClient

uri = "mongodb+srv://seguro:Seguro2026Teste@cluster0.saq8sca.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
print(client.admin.command("ping"))