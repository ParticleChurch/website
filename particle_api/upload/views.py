from rest_framework.response import Response
from rest_framework.decorators import api_view
import particle_api.helpers as helpers
import os

@api_view(['POST'])
def upload_dll(request):
    if request.data['key'] != helpers.SECRETS['upload_dll_key']:
        return Response(status = 401)
    
    file = request.FILES["encrypted.dll"]
    
    if file.size > 10 * 1024 * 1024: # 10 MB
        return Response({"detail": "File is too large. Max size is 10MiB."}, status = 400)
    
    with open("/var/www/particle_api/static_distributables/temp.dll", "wb") as f:
        for chunk in file.chunks(chunk_size = 1024):
            f.write(chunk)
    
    os.replace("/var/www/particle_api/static_distributables/temp.dll", "/var/www/particle_api/static_distributables/dlls/encrypted.dll")
    
    return Response({"success": True})
