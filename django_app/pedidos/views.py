from django import forms
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import (ListView, DetailView,
    CreateView, UpdateView, DeleteView)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import models, IntegrityError
from django.db import transaction
from django.db.models.deletion import ProtectedError
from django.views import View
from django.db.models import Count, Sum
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
import json
from django.http import JsonResponse
from .models import Cliente, Producto, Pedido, DetallePedido
from .forms import CustomAuthenticationForm, CustomUserCreationForm, ClienteForm, ProductoForm, PedidoForm, PedidoCreateForm

class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    raise_exception = True

    def test_func(self):
        return self.request.user.is_staff

class RenovarSesionView(View):
    """Renueva la sesión vía AJAX cuando el usuario ingresa su contraseña en el modal.
    No requiere LoginRequiredMixin porque se llama precisamente cuando la sesión expiró."""
    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        if not username:
            return JsonResponse({'ok': False, 'error': 'No se pudo identificar la sesión.'}, status=400)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'ok': True})
        return JsonResponse({'ok': False, 'error': 'Contraseña incorrecta.'}, status=400)

class ClienteListView(StaffRequiredMixin, ListView):
    model = Cliente
    template_name = 'pedidos/clientes/lista.html'
    context_object_name = 'clientes'
    paginate_by = 10   # Paginación automática: 10 por página

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                models.Q(nombre__icontains=q) | models.Q(correo__icontains=q)
            )
        return queryset

class ClienteCreateView(StaffRequiredMixin, CreateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'pedidos/clientes/formulario.html'
    success_url = reverse_lazy('cliente-list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente creado exitosamente.')
        return super().form_valid(form)

class ClienteUpdateView(StaffRequiredMixin, UpdateView):
    model = Cliente
    form_class = ClienteForm
    template_name = 'pedidos/clientes/formulario.html'
    success_url = reverse_lazy('cliente-list')

    def form_valid(self, form):
        messages.success(self.request, 'Cliente actualizado.')
        return super().form_valid(form)

class ClienteDeleteView(StaffRequiredMixin, DeleteView):
    model = Cliente
    template_name = 'pedidos/clientes/confirmar_eliminar.html'
    success_url = reverse_lazy('cliente-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, 'Cliente eliminado.')
            return redirect(self.success_url)
        except (ProtectedError, IntegrityError):
            return render(request, 'protected_error.html', {'object_type': 'cliente'}, status=400)


# ── PRODUCTOS ─────────────────────────────────────────────────────────
# (Igual que Clientes, cambia 'Cliente' por 'Producto' y el template)
class ProductoListView(StaffRequiredMixin, ListView):
    model = Producto
    template_name = 'pedidos/productos/lista.html'
    context_object_name = 'productos'
    paginate_by = 10
    
class ProductoCreateView(StaffRequiredMixin, CreateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'pedidos/productos/formulario.html'
    success_url = reverse_lazy('producto-list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto creado exitosamente.')
        return super().form_valid(form)

class ProductoUpdateView(StaffRequiredMixin, UpdateView):
    model = Producto
    form_class = ProductoForm
    template_name = 'pedidos/productos/formulario.html'
    success_url = reverse_lazy('producto-list')

    def form_valid(self, form):
        messages.success(self.request, 'Producto actualizado.')
        return super().form_valid(form)

class ProductoDeleteView(StaffRequiredMixin, DeleteView):
    model = Producto
    template_name = 'pedidos/productos/confirmar_eliminar.html'
    success_url = reverse_lazy('producto-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, 'Producto eliminado.')
            return redirect(self.success_url)
        except (ProtectedError, IntegrityError):
            return render(request, 'protected_error.html', {'object_type': 'producto'}, status=400)



# ── PEDIDOS ───────────────────────────────────────────────────────────
class PedidoListView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'pedidos/pedidos/lista.html'
    context_object_name = 'pedidos'
    paginate_by = 10

    def get_queryset(self):
        estado = self.request.GET.get('estado')
        qs = Pedido.objects.select_related('cliente', 'usuario').prefetch_related('detalles__producto').all()
        if not self.request.user.is_staff:
            qs = qs.filter(usuario=self.request.user)
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Pedidos' if self.request.user.is_staff else 'Mis pedidos'
        if self.request.user.is_staff:
            context['page_note'] = 'Aquí se muestra el listado completo de pedidos.'
        else:
            context['page_note'] = 'Aquí están tus pedidos personales.'
        return context

class MisPedidosView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'pedidos/pedidos/lista.html'
    context_object_name = 'pedidos'
    paginate_by = 10

    def get_queryset(self):
        estado = self.request.GET.get('estado')
        qs = Pedido.objects.select_related('cliente', 'usuario').prefetch_related('detalles__producto').filter(usuario=self.request.user)
        if estado:
            qs = qs.filter(estado=estado)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Mis pedidos'
        context['page_note'] = 'Solo ves los pedidos que hiciste con esta cuenta.'
        return context

class PedidoCreateView(LoginRequiredMixin, CreateView):
    model = Pedido
    form_class = PedidoCreateForm
    template_name = 'pedidos/pedidos/formulario.html'
    success_url = reverse_lazy('pedido-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_staff:
            form.fields.pop('cliente', None)
            form.fields['estado'].initial = 'Pendiente'
            form.fields['estado'].widget = forms.HiddenInput()
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = Producto.objects.filter(stock__gt=0).values('id', 'precio')
        context['product_prices_json'] = json.dumps({str(p['id']): float(p['precio']) for p in products})
        return context

    @transaction.atomic
    def form_valid(self, form):
        producto = form.cleaned_data['producto']
        cantidad = form.cleaned_data['cantidad']
        if producto.stock < cantidad:
            messages.error(self.request, f'Stock insuficiente. Disponible: {producto.stock}')
            return self.form_invalid(form)
        if not self.request.user.is_staff:
            form.instance.cliente = self.get_cliente_for_user(self.request.user)
            form.instance.estado = 'Pendiente'
        form.instance.usuario = self.request.user
        self.object = form.save()
        DetallePedido.objects.create(
            pedido=self.object,
            producto=producto,
            cantidad=cantidad
        )
        producto.stock -= cantidad
        producto.save()
        messages.success(self.request, 'Pedido creado exitosamente.')
        return redirect(self.get_success_url())

    def get_cliente_for_user(self, user):
        """Obtiene o crea el cliente vinculado al usuario autenticado."""
        nombre_cliente = user.get_full_name() or user.username
        correo = user.email or f'{user.username}@example.com'
        
        cliente, _ = Cliente.objects.get_or_create(
            usuario=user,
            defaults={
                'nombre': nombre_cliente,
                'correo': correo,
                'direccion': '',
                'telefono': '',
            }
        )
        
        # Actualiza datos si cambiaron en el usuario
        if cliente.nombre != nombre_cliente or cliente.correo != correo:
            cliente.nombre = nombre_cliente
            cliente.correo = correo
            cliente.save()
        
        return cliente

class PedidoUpdateView(StaffRequiredMixin, UpdateView):
    model = Pedido
    form_class = PedidoForm
    template_name = 'pedidos/pedidos/formulario.html'
    success_url = reverse_lazy('pedido-list')

    def form_valid(self, form):
        messages.success(self.request, 'Pedido actualizado.')
        return super().form_valid(form)

class PedidoDeleteView(StaffRequiredMixin, DeleteView):
    model = Pedido
    template_name = 'pedidos/pedidos/confirmar_eliminar.html'
    success_url = reverse_lazy('pedido-list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, 'Pedido eliminado.')
            return redirect(self.success_url)
        except (ProtectedError, IntegrityError):
            return render(request, 'protected_error.html', {'object_type': 'pedido'}, status=400)

    def form_valid(self, form):
        messages.success(self.request, 'Pedido eliminado.')
        return super().form_valid(form)

class AnularPedidoView(LoginRequiredMixin, View):
    template_name = 'pedidos/pedidos/confirmar_anular.html'

    def get_pedido(self, pk, user):
        pedido = Pedido.objects.filter(pk=pk, usuario=user).first()
        return pedido

    def get(self, request, pk):
        pedido = self.get_pedido(pk, request.user)
        if not pedido:
            messages.error(request, 'Pedido no encontrado.')
            return redirect('pedido-list')
        if pedido.estado != 'Pendiente':
            messages.error(request, 'Solo se pueden anular pedidos en estado Pendiente.')
            return redirect('pedido-list')
        return render(request, self.template_name, {'pedido': pedido})

    def post(self, request, pk):
        pedido = self.get_pedido(pk, request.user)
        if not pedido:
            messages.error(request, 'Pedido no encontrado.')
            return redirect('pedido-list')
        if pedido.estado != 'Pendiente':
            messages.error(request, 'Solo se pueden anular pedidos en estado Pendiente.')
            return redirect('pedido-list')
        # Restaurar stock
        for detalle in pedido.detalles.select_related('producto').all():
            detalle.producto.stock += detalle.cantidad
            detalle.producto.save()
        pedido.estado = 'Anulado'
        pedido.save()
        messages.success(request, f'Pedido #{pedido.id} anulado correctamente.')
        return redirect('pedido-list')


# ── DASHBOARD ──────────────────────────────────────────────────────────
class DashboardView(LoginRequiredMixin, View):
    template_name = 'pedidos/dashboard.html'

    def get(self, request):
        if request.user.is_staff:
            total_clientes = Cliente.objects.count()
            total_productos = Producto.objects.count()
            total_pedidos = Pedido.objects.count()
            pedidos_por_estado = Pedido.objects.values('estado').annotate(count=Count('estado'))
            productos_stock_bajo = Producto.objects.filter(stock__lt=5)
            ingresos = DetallePedido.objects.filter(
                pedido__estado='Entregado'
            ).aggregate(total=Sum(models.F('cantidad') * models.F('producto__precio')))['total'] or 0
        else:
            total_clientes = Cliente.objects.filter(correo=request.user.email).count() if request.user.email else 0
            total_productos = 0
            total_pedidos = Pedido.objects.filter(usuario=request.user).count()
            pedidos_por_estado = Pedido.objects.filter(usuario=request.user).values('estado').annotate(count=Count('estado'))
            productos_stock_bajo = []
            ingresos = DetallePedido.objects.filter(
                pedido__estado='Entregado',
                pedido__usuario=request.user
            ).aggregate(total=Sum(models.F('cantidad') * models.F('producto__precio')))['total'] or 0
        
        context = {
            'total_clientes': total_clientes,
            'total_productos': total_productos,
            'total_pedidos': total_pedidos,
            'pedidos_por_estado': pedidos_por_estado,
            'productos_stock_bajo': productos_stock_bajo,
            'ingresos': ingresos,
        }
        return render(request, self.template_name, context)


def handler_403(request, exception=None):
    """Maneja errores 403 Forbidden con una página estilizada."""
    return render(request, '403.html', status=403)


# ── REGISTRO ──────────────────────────────────────────────────────────
class RegistroView(View):
    template_name = 'pedidos/registro.html'

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Extrae teléfono y dirección del formulario
            telefono = form.cleaned_data.get('telefono', '')
            direccion = form.cleaned_data.get('direccion', '')
            
            # Crea el cliente vinculado al usuario (por email)
            nombre_cliente = user.get_full_name() or user.username
            Cliente.objects.get_or_create(
                correo=user.email,
                defaults={
                    'nombre': nombre_cliente,
                    'telefono': telefono,
                    'direccion': direccion,
                }
            )
            
            login(request, user)
            messages.success(request, 'Cuenta creada correctamente. Bienvenido.')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


