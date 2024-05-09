import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onlydepas.settings')
django.setup()

from app.models import Inmueble, Comuna, Region

def fetch_inmuebles_por_region():
    regiones = Region.objects.prefetch_related('comunas__inmuebles').distinct()
    inmuebles_por_region = {}

    for region in regiones:
        region_dict = {}
        for comuna in region.comunas.all():
            inmuebles = comuna.inmuebles.filter(disponible=True).values('nombre', 'descripcion')
            if inmuebles:
                region_dict[comuna.nombre] = list(inmuebles)
        if region_dict:
            inmuebles_por_region[region.nombre] = region_dict

    return inmuebles_por_region

def save_to_file(inmuebles_data, filename='inmuebles_por_region.txt'):
    with open(filename, 'w', encoding='utf-8') as file:
        for region, comunas in inmuebles_data.items():
            file.write(f"Región: {region}\n")
            for comuna, inmuebles in comunas.items():
                file.write(f"  Comuna: {comuna}\n")
                for inmueble in inmuebles:
                    file.write(f"    Nombre: {inmueble['nombre']}\n")
                    file.write(f"    Descripción: {inmueble['descripcion']}\n")
                file.write("\n")
            file.write("\n")

if __name__ == '__main__':
    inmuebles_data = fetch_inmuebles_por_region()
    save_to_file(inmuebles_data)
