from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from .models import SolicitudArriendo, Inmueble, Region, Comuna
from .forms import RegistroUsuarioForm, SolicitudArriendoForm, InmuebleForm, UsuarioUpdateForm

# Create your views here.

def index(request):
    inmuebles = Inmueble.objects.all()
    return render(request, 'index.html', {'inmuebles': inmuebles})

@login_required
def detalle_inmueble(request, id):
    inmueble = Inmueble.objects.get(pk=id)
    return render(request, 'detalle_inmueble.html', {'inmueble': inmueble})

def registro_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            password = form.cleaned_data['password']
            usuario.set_password(password)
            usuario.save()
            usuario_autenticado = authenticate(username=usuario.username, password=password)
            if usuario_autenticado is not None:
                login(request, usuario_autenticado)
                messages.success(request, "Te has registrado exitosamente.")
                return redirect('index')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registro_usuario.html', {'form': form})

@login_required
def generar_solicitud_arriendo(request, id):
    inmueble = get_object_or_404(Inmueble, pk=id)
    if request.user.usuario.tipo_usuario == 'arrendatario':
        if request.method == 'POST':
            form = SolicitudArriendoForm(request.POST)
            if form.is_valid():
                solicitud = form.save(commit=False)
                solicitud.arrendatario = request.user.usuario
                solicitud.inmueble = inmueble
                solicitud.save()
                messages.success(request, "Solicitud de arriendo enviada exitosamente.")
                return redirect('detalle', id=inmueble.id)
        else:
            form = SolicitudArriendoForm(initial={'inmueble': inmueble})
        return render(request, 'generar_solicitud_arriendo.html', {'form': form})
    else:
        return redirect('index')

@login_required
def solicitudes_arrendador(request):
    if request.user.usuario.tipo_usuario == 'arrendador':
        solicitudes = SolicitudArriendo.objects.filter(inmueble__propietario=request.user)
        return render(request, 'solicitudes_arrendador.html', {'solicitudes': solicitudes})
    else:
        return redirect('index')

@login_required
def alta_inmueble(request):
    if request.method == 'POST':
        form = InmuebleForm(request.POST, request.FILES)
        if form.is_valid():
            inmueble = form.save(commit=False)
            inmueble.propietario = request.user.usuario
            inmueble.save()
            messages.success(request, "Inmueble agregado exitosamente.")
            return redirect('dashboard')
    else:
        form = InmuebleForm()
    return render(request, 'alta_inmueble.html', {'form': form})

@login_required
def perfil_usuario(request):
    if request.method == 'POST':
        u_form = UsuarioUpdateForm(request.POST, instance=request.user.usuario)
        if u_form.is_valid():
            if u_form.has_changed():
                usuario = u_form.save()
                if 'password' in u_form.changed_data:
                    update_session_auth_hash(request, usuario)
                messages.success(request, "Perfil actualizado correctamente.")
            else:
                messages.info(request, "No se detectaron cambios en tu perfil.")
            return redirect('perfil_usuario')
    else:
        u_form = UsuarioUpdateForm(instance=request.user.usuario)
    return render(request, 'perfil_usuario.html', {'u_form': u_form})

@login_required
def dashboard(request):
    # Inicialización de formularios
    if request.method == 'POST':
        u_form = UsuarioUpdateForm(request.POST, instance=request.user.usuario)
        if u_form.is_valid():
            u_form.save()
            messages.success(request, 'Tu perfil ha sido actualizado con éxito.')
            return redirect('dashboard')  # Redirecciona a dashboard para evitar resubmission de formulario
    else:
        u_form = UsuarioUpdateForm(instance=request.user.usuario)

    # Filtrado de inmuebles según selección de región y comuna
    regiones = Region.objects.all()
    comunas = Comuna.objects.all()
    region_id = request.GET.get('region')
    comuna_id = request.GET.get('comuna')
    inmuebles = Inmueble.objects.all()
    if region_id:
        inmuebles = inmuebles.filter(comuna__region_id=region_id)
    if comuna_id:
        inmuebles = inmuebles.filter(comuna_id=comuna_id)

    # Determinar si el usuario es arrendador o arrendatario y cargar datos adecuados
    context = {
        'u_form': u_form,
        'regiones': regiones,
        'comunas': comunas,
        'inmuebles': inmuebles,
    }

    if request.user.usuario.tipo_usuario == 'arrendatario':
        solicitudes = SolicitudArriendo.objects.filter(arrendatario=request.user.usuario)
        context['solicitudes'] = solicitudes
        return render(request, 'dashboard_arrendatario.html', context)
    
    elif request.user.usuario.tipo_usuario == 'arrendador':
        inmuebles_propios = Inmueble.objects.filter(propietario=request.user.usuario)
        solicitudes_recibidas = SolicitudArriendo.objects.filter(inmueble__propietario=request.user.usuario)
        context.update({
            'inmuebles_propios': inmuebles_propios,
            'solicitudes_recibidas': solicitudes_recibidas
        })
        return render(request, 'dashboard_arrendador.html', context)
    else:
        messages.error(request, "Tipo de usuario no reconocido.")
        return redirect('index')


def filter_inmuebles(request):
    inmuebles = Inmueble.objects.all()
    region_id = request.GET.get('region')
    comuna_id = request.GET.get('comuna')
    if region_id:
        inmuebles = inmuebles.filter(comuna__region_id=region_id)
    if comuna_id:
        inmuebles = inmuebles.filter(comuna_id=comuna_id)
    return inmuebles


def my_view(request):
    messages.add_message(request, messages.INFO, 'Mensaje de Prueba.')
@login_required
def actualizar_inmueble(request, id):
    inmueble = get_object_or_404(Inmueble, pk=id, propietario=request.user.usuario)
    if request.method == 'POST':
        form = InmuebleForm(request.POST, request.FILES, instance=inmueble)
        if form.is_valid():
            form.save()
            messages.success(request, "Inmueble actualizado con éxito.")
            return redirect('dashboard')
    else:
        form = InmuebleForm(instance=inmueble)
    return render(request, 'actualizar_inmueble.html', {'form': form})

@login_required
def eliminar_inmueble(request, id):
    inmueble = get_object_or_404(Inmueble, pk=id, propietario=request.user.usuario)
    if request.method == 'POST':
        inmueble.delete()
        messages.success(request, "Inmueble eliminado con éxito.")
        return redirect('dashboard')
    return render(request, 'eliminar_inmueble.html', {'inmueble': inmueble})