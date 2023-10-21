from msal import ConfidentialClientApplication
import settings

# Создание экземпляра приложения с использованием ID клиента, авторитета и секрета клиента
app = ConfidentialClientApplication(settings.CLIENT_ID, authority=settings.AUTHORITY, client_credential=settings.CLIENT_SECRET)

# Запрос кода авторизации от пользователя
code = input("Enter the authorization code: ")

# Получение токена доступа с использованием кода авторизации
result = app.acquire_token_by_authorization_code(code, settings.SCOPE, redirect_uri=settings.REDIRECT_URI)

# Вывод результата для пользователя
print(result)
