from django.core.management.utils import get_random_secret_key

DATABASE_NAME = "django_database"
DATABASE_ROOT_PASSWORD = "12345"
DATABASE_USER = "user"
DATABASE_USER_PASSWORD = "12345"
SECRET_KEY = get_random_secret_key().replace("#", "$")
DATABASE_HOST = "127.0.0.1"
DATABASE_PORT = "3306"

with open("./.env", "a") as f:
    try:
        f.write(f"DATABASE_NAME={DATABASE_NAME}\nDATABASE_ROOT_PASSWORD={DATABASE_ROOT_PASSWORD}\nDATABASE_USER={DATABASE_USER}\nDATABASE_USER_PASSWORD={DATABASE_USER_PASSWORD}\nDATABASE_HOST={DATABASE_HOST}\nDATABASE_PORT={DATABASE_PORT}\nSECRET_KEY={SECRET_KEY}")
        print("Arquivo .env criado! Acesse o arquivo para alterar as informações!")
    except:
        print("Houve algum erro! Tente novamente.")