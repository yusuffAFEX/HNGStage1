import os

import requests
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class VisitorNameAPIView(APIView):

    def get(self, request, *args, **kwargs):
        visitor_name = self.request.GET.get('visitor_name', None)

        if not visitor_name:
            return Response(data={'message': "provide visitor name as a query param"}, status=status.HTTP_400_BAD_REQUEST)

        ip = get_client_ip(self.request)
        lat, long = get_geolocation(ip)
        print(lat, long)
        API_KEY = os.getenv('API_KEY')

        try:
            response = requests.get(
                f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={long}&units=metric&appid={API_KEY}").json()
        except Exception as e:
            return Response(data={'message': 'there is a network glitch, try again later'},
                            status=status.HTTP_400_BAD_REQUEST)

        location = response.get('name') if response.get('name') else '-'
        temp = response.get('main').get('temp') if response.get('main') else '-'
        print(location)
        return Response(data={'client_id': ip, 'location': f'{location}', 'greeting': f'Hello, {visitor_name}!, the temperature is {temp} degrees Celcius in {location}'}, status=status.HTTP_200_OK)


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_geolocation(ip):
    try:
        token = os.getenv('token')
        url = f'https://ipinfo.io/{ip}?token={token}'
        response = requests.get(url)
        lat, long = response.json().get('loc').split(',')
        return lat, long
    except Exception as e:
        print(e)
        return None, None