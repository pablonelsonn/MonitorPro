from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.user import User

db = SessionLocal()

try:
    user = db.query(User).filter(User.username == "admin").first()

    if not user:
        print("Usuário admin não encontrado.")
    else:
        nova_senha = input("Digite a nova senha do admin: ")

        if not nova_senha:
            print("A senha não pode ser vazia.")
        else:
            user.hashed_password = hash_password(nova_senha)
            user.is_active = True

            db.commit()

            print("Senha do admin alterada com sucesso.")

finally:
    db.close()