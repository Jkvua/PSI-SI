from storage.usuarios import criar_usuario

try:
    criar_usuario(
        nome="Admin do Trio", 
        usuario="admin_trio", 
        senha="trioadmin", 
        perfil="admin"
    )
    print("Superusuário 'admin_trio' criado com sucesso no MongoDB!")
except Exception as e:
    print(f"Erro ao criar: {e}")