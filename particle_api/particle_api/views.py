from django.http import FileResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from particle_api.helpers import log_message
from particle_api.settings import BASE_DIR

import random, os

DLLS_DIR = BASE_DIR / "static_distributables" / "dlls"
INJECTOR_PATH = BASE_DIR / "static_distributables" / "injector.exe"

@api_view(['GET'])
def dll(request):
    dlls = os.listdir(DLLS_DIR)
    dll = random.choice(dlls)
    
    log_message('user_injection', dll = dll)
    return FileResponse(
        open(DLLS_DIR / dll, "rb"),
        as_attachment = True,
        filename = "dll.dll"
    )

@api_view(['GET'])
def injector(request):
    return FileResponse(
        open(INJECTOR_PATH, "rb"),
        as_attachment = True,
        filename = "injector.exe"
    )