import msalimport msal
from settings import CLIENT_ID, REDIRECT_URI, AUTHORITY, SCOPE

# Создание экземпляра приложения с использованием ID клиента и авторитета
app = msal.PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

# Получение URL-адреса авторизации
auth_url = app.get_authorization_request_url(SCOPE, redirect_uri=REDIRECT_URI, login_hint=None)

# Вывод URL-адреса для пользователя
print(f"Please go to this URL and authorize the app: {auth_url}")
