from rest_framework.test import APIRequestFactory





factory = APIRequestFactory()



request = factory.get('playground/user/')

print(request)
