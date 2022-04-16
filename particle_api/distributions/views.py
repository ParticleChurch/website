from django.http import FileResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from particle_api.settings import BASE_DIR

import random, os, time

STATIC_DISTRIBUTABLES = BASE_DIR / "static_distributables" 

def read_injector_version():
    with open(STATIC_DISTRIBUTABLES / "injector" / "version.txt", "r") as f:
        return f.read()

@api_view(['GET'])
def dll_download(request):
    dlls = os.listdir(STATIC_DISTRIBUTABLES / 'dlls')
    
    return FileResponse(
        open(STATIC_DISTRIBUTABLES / 'dlls' / random.choice(dlls), "rb"),
        as_attachment = True,
        filename = "dll.dll"
    )

@api_view(['GET'])
def injector_download(request):
    return FileResponse(
        open(STATIC_DISTRIBUTABLES / 'injector' / 'injector.exe', "rb"),
        as_attachment = True,
        filename = f"injector_v{read_injector_version()}.exe"
    )

@api_view(['GET'])
def injector_version(request):
    current_version = read_injector_version().lower().strip()
    local_version = request.GET.get('local_version', current_version + 'this ensures the comparison will fail').lower().strip()
    
    return Response({
        'update_required': current_version != local_version,
        'current_version': current_version,
    })