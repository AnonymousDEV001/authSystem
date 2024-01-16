from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import *
import requests
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *


@api_view(["POST"])
def create_user(request):
    if request.method == 'POST':
        data = request.data
        user_serializer = CustomUserSerializer(data=data)
        if user_serializer.is_valid():
            existing_user = CustomUser.objects.filter(
                email=data["email"]).first()
            if existing_user:
                return Response({"error": "User already exists"})

            user = user_serializer.save()

            return Response({"message": "User created sucessfully"})
        return Response(user_serializer.errors)
    




@api_view(['POST'])
def token_verification_view(request):
    provider = request.data.get('provider')
    token = request.data.get('token')

    if not provider or not token:
        return Response({'error': 'Provider and token are required'}, status=400)

    if provider == 'google':
        user_info_url = f"https://www.googleapis.com/oauth2/v3/userinfo"
        headers = {
            'Authorization': f'Bearer {token}'
        }
        user_info_response = requests.get(user_info_url, headers=headers)

        if user_info_response.status_code == 200:
            user_info_data = user_info_response.json()
            email = user_info_data.get("email")
            first_name = user_info_data.get("given_name")
            last_name = user_info_data.get("family_name")

            # Check if the user already exists in the database
            existing_user = CustomUser.objects.filter(email=email).first()
            existing_user_oauth = social_auth.objects.filter(
                email=email).first()
            # checking if user already exists and is signed up using other methord or not
            if existing_user:
                if existing_user.provider != "google":
                    return Response({'error': 'User Has been registered using some other methord'}, status=400)
                # Update the existing user's information
                existing_user.first_name = first_name
                existing_user.last_name = last_name
                existing_user.save()
                if existing_user_oauth:
                    existing_user_oauth.access_token = token
                    existing_user_oauth.save()
                else:
                    # Create a new social_auth entry if it doesn't exist
                    social_auth.objects.create(
                        foreignKey=existing_user,
                        email=email,
                        access_token=token,
                        provider=provider
                    )
            else:
                # Create a new user
                new_user = CustomUser.objects.create(
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    provider=provider,
                )
                new_user_oauth = social_auth.objects.create(
                    foreignKey=new_user,
                    email=email,
                    access_token=token,
                    provider=provider
                )

            refresh = RefreshToken.for_user(
                existing_user if existing_user else new_user)

            # Access token can be obtained from the refresh token
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({"refresh": refresh_token, 'access': access_token}, status=401)
        else:
            return Response({'error': 'Invalid Google access token'}, status=401)
    else:
        return Response({'error': 'Invalid provider'}, status=401)
