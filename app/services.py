from app.models import  Inmueble, Comuna, Usuario
#CRUD DEL MODELO INMUEBLE

def get_all_inmuebles(): #para ENLISTAR
 Inm = Inmueble.objects.all()
 return Inm



def insertar_inmueble(data): 
    inm = Inmueble(
        nombre=data['nombre'],
        direccion=data['direccion'],
        descripcion=data['descripcion'],
        precio=data['precio'],
        comuna=Comuna.objects.get(id=data['comuna_id']),
        disponible=data['disponible'],
        m2_construidos=data['m2_construidos'],
        m2_terreno=data['m2_terreno'],
        cantidad_estacionamientos=data['cantidad_estacionamientos'],
        cantidad_habitaciones=data['cantidad_habitaciones'],
        cantidad_banos=data['cantidad_banos'],
        tipo_de_inmueble=data['tipo_de_inmueble'],
        propietario=Usuario.objects.get(id=data['propietario_id'])
    )
    if 'imagen' in data:
        inm.imagen = data['imagen']
    inm.save()
    
 
 
def actualizar_descrp_inmueble(id_inmueble,new_descrip): #para actualizar
    Inmueble.objects.filter(pk=id_inmueble).update(descripcion=new_descrip)
 
 
def eliminar_inmueble(id_inmueble): #para eliminar
    Inmueble.objects.get(id=id_inmueble).delete()