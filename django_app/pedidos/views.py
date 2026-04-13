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
from .forms import CustomAuthenticationForm, CustomUserCreationForm, ClienteForm, ProductoForm, PedidoForm, PedidoCreateForm, DetallePedidoFormSet


def devolver_stock(pedido):
    """Devuelve al inventario el stock de todos los detalles de un pedido."""
    for detalle in pedido.detalles.select_related('producto').all():
        detalle.producto.stock += detalle.cantidad
        detalle.producto.save()


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

    def form_valid(self, form):
        self.object = self.get_object()
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Cliente eliminado.')
            return response
        except (ProtectedError, IntegrityError):
            return render(self.request, 'protected_error.html',
                          {'object_type': 'cliente'}, status=400)


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

    def form_valid(self, form):
        self.object = self.get_object()
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Producto eliminado.')
            return response
        except (ProtectedError, IntegrityError):
            return render(self.request, 'protected_error.html',
                          {'object_type': 'producto'}, status=400)



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

    def get_context_data(self, **kwargs):
        self.object = None
        context = super().get_context_data(**kwargs)
        products = list(Producto.objects.filter(stock__gt=0).values('id', 'nombre', 'precio', 'stock'))
        # Convertir Decimal a float para serializacion JSON
        for p in products:
            p['precio'] = float(p['precio'])
        context['product_prices_json'] = json.dumps({str(p['id']): p['precio'] for p in products})
        context['product_list'] = json.dumps(products)

        if self.request.POST:
            context['detalles_formset'] = DetallePedidoFormSet(self.request.POST, prefix='detalles')
            context['existing_details_json'] = '[]'
        else:
            context['detalles_formset'] = DetallePedidoFormSet(prefix='detalles')
            context['existing_details_json'] = '[]'

        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not self.request.user.is_staff:
            # Usuario normal: asignar cliente automáticamente y ocultar campos
            cliente = self.get_cliente_for_user(self.request.user)
            if 'cliente' in form.fields:
                form.fields['cliente'].initial = cliente.pk
                form.fields['cliente'].widget = forms.HiddenInput()
            if 'estado' in form.fields:
                form.fields['estado'].initial = 'Pendiente'
                form.fields['estado'].widget = forms.HiddenInput()
        else:
            # Staff: mostrar selector de clientes completo
            if 'cliente' in form.fields:
                form.fields['cliente'].queryset = Cliente.objects.all()
                form.fields['cliente'].widget = forms.Select(attrs={'class': 'form-select'})
        return form

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    @transaction.atomic
    def form_valid(self, form):
        context = self.get_context_data()
        detalles_formset = context['detalles_formset']

        # Llamar is_valid() para poblar cleaned_data de cada formulario
        # Ignoramos el resultado porque manejamos la validacion manualmente
        detalles_formset.is_valid()
        print(f'  detalles_formset.is_valid(): {detalles_formset.is_valid()}')
        print(f'  detalles_formset.errors: {detalles_formset.errors}')
        print(f'  detalles_formset.non_form_errors: {detalles_formset.non_form_errors}')

        detalles_validos = []
        for det_form in detalles_formset:
            # Formularios sin cleaned_data = vacios o con errores de campos requeridos
            if not det_form.cleaned_data:
                continue

            if det_form.cleaned_data.get('DELETE', False):
                continue

            producto = det_form.cleaned_data.get('producto')
            cantidad = det_form.cleaned_data.get('cantidad')

            if not producto or not cantidad:
                continue

            # Validar stock
            if producto.stock < cantidad:
                messages.error(self.request,
                    f'Stock insuficiente para "{producto.nombre}". Disponible: {producto.stock}')
                return self.form_invalid(form)

            detalles_validos.append(det_form)

        if not detalles_validos:
            messages.error(self.request, 'Debes seleccionar al menos un producto.')
            return self.form_invalid(form)

        # Guardar pedido
        if not self.request.user.is_staff:
            # Usuario normal: asignar cliente automáticamente
            form.instance.usuario = self.request.user
            form.instance.cliente = self.get_cliente_for_user(self.request.user)
        # Staff: el cliente ya viene del formulario (form.instance.cliente)
        self.object = form.save()
        print(f'  Pedido creado: #{self.object.id}')

        # Guardar detalles y descontar stock
        for det_form in detalles_validos:
            producto = det_form.cleaned_data['producto']
            cantidad = det_form.cleaned_data['cantidad']
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

class PedidoUpdateView(LoginRequiredMixin, UpdateView):
    model = Pedido
    form_class = PedidoCreateForm
    template_name = 'pedidos/pedidos/formulario.html'
    success_url = reverse_lazy('pedido-list')

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(usuario=self.request.user, estado='Pendiente')
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        products = list(Producto.objects.filter(stock__gt=0).values('id', 'nombre', 'precio', 'stock'))
        for p in products:
            p['precio'] = float(p['precio'])
        context['product_prices_json'] = json.dumps({str(p['id']): p['precio'] for p in products})
        context['product_list'] = json.dumps(products)

        # Determinar si debemos mostrar el formset editable.
        # Usar el estado enviado en POST si existe, sino el de la BD.
        # Esto evita errores de ManagementForm cuando se cambia el estado.
        post_estado = self.request.POST.get('estado', '') if self.request.POST else ''
        usar_formset_editable = (self.object.estado == 'Pendiente' or post_estado == 'Pendiente')

        if usar_formset_editable:
            if self.request.POST:
                context['detalles_formset'] = DetallePedidoFormSet(self.request.POST, prefix='detalles')
                context['existing_details_json'] = '[]'
            else:
                existing_details = [
                    {'producto_id': str(det.producto_id), 'cantidad': det.cantidad}
                    for det in self.object.detalles.all()
                ]
                context['existing_details_json'] = json.dumps(existing_details)
                context['detalles_formset'] = DetallePedidoFormSet(prefix='detalles', initial=[
                    {'producto': det.producto, 'cantidad': det.cantidad}
                    for det in self.object.detalles.all()
                ])
                total = sum(det.producto.precio * det.cantidad for det in self.object.detalles.all())
                context['pedido_total'] = total
        else:
            # Pedido no pendiente: no se necesita el formset (solo lectura)
            context['detalles_formset'] = DetallePedidoFormSet(prefix='detalles')
            context['existing_details_json'] = '[]'
            total = sum(det.producto.precio * det.cantidad for det in self.object.detalles.all())
            context['pedido_total'] = total

        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Eliminar el campo 'cliente' del formulario — siempre se muestra como texto plano
        if 'cliente' in form.fields:
            del form.fields['cliente']

        if not self.request.user.is_staff:
            if 'estado' in form.fields:
                form.fields['estado'].initial = 'Pendiente'
                form.fields['estado'].widget = forms.HiddenInput()
        else:
            # Limitar opciones del estado según el estado actual del pedido
            if self.object and 'estado' in form.fields:
                estado_actual = self.object.estado
                if estado_actual == 'Pendiente':
                    opciones_estado = [('Pendiente', 'Pendiente'), ('Enviado', 'Enviado'), ('Anulado', 'Anulado')]
                elif estado_actual == 'Enviado':
                    opciones_estado = [('Enviado', 'Enviado'), ('Entregado', 'Entregado'), ('Anulado', 'Anulado')]
                else:
                    opciones_estado = Pedido.ESTADOS
                form.fields['estado'].choices = opciones_estado
        return form

    def dispatch(self, request, *args, **kwargs):
        pedido = self.get_object()
        # Bloquear edición para pedidos cerrados (tanto staff como usuarios)
        if pedido.estado in ('Entregado', 'Anulado'):
            messages.error(request, 'Este pedido ya está cerrado y no puede modificarse.')
            return redirect('pedido-list')
        if not request.user.is_staff:
            if pedido.estado != 'Pendiente':
                messages.error(request, 'Solo se pueden editar pedidos en estado Pendiente.')
                return redirect('pedido-list')
            if pedido.usuario != request.user:
                messages.error(request, 'No tienes permiso para editar este pedido.')
                return redirect('pedido-list')
        return super().dispatch(request, *args, **kwargs)

    @transaction.atomic
    def form_valid(self, form):
        db_estado = Pedido.objects.get(pk=self.object.pk).estado
        submitted_estado = self.request.POST.get('estado') or db_estado

        # Validar transición de estados permitida
        transiciones_validas = {
            'Pendiente': ['Pendiente', 'Enviado', 'Anulado'],
            'Enviado': ['Enviado', 'Entregado', 'Anulado'],
            'Entregado': ['Entregado', 'Anulado'],
            'Anulado': ['Anulado'],
        }

        print(f"DEBUG: Transiciones válidas para '{db_estado}': {transiciones_validas.get(db_estado, [db_estado])}")

        if submitted_estado not in transiciones_validas.get(db_estado, [db_estado]):
            print(f"DEBUG: Transición INVÁLIDA - entrando en form_invalid")
            opciones = [t for t in transiciones_validas.get(db_estado, []) if t != db_estado]
            if opciones:
                msg = f'No se puede cambiar el estado de "{db_estado}" a "{submitted_estado}". Las opciones válidas son: {", ".join(opciones)}.'
            else:
                msg = f'El estado "{db_estado}" es final y no permite cambios.'
            messages.error(self.request, msg)
            return self.form_invalid(form)

        print(f"DEBUG: Transición de estado VÁLIDA")

        # 1. Si el nuevo estado es 'Anulado', devolver stock y guardar ANTES de validar formset
        print(f"\nDEBUG: Verificando si es anulación...")
        print(f"DEBUG: submitted_estado == 'Anulado': {submitted_estado == 'Anulado'}")
        print(f"DEBUG: db_estado != 'Anulado': {db_estado != 'Anulado'}")

        if submitted_estado == 'Anulado' and db_estado != 'Anulado':
            print(f"DEBUG: ENTRANDO en bloque de ANULACIÓN")
            print(f"DEBUG: Llamando a devolver_stock()...")
            devolver_stock(self.object)
            print(f"DEBUG: Stock devuelto correctamente")
            form.instance.estado = 'Anulado'
            form.instance.cliente = self.object.cliente
            form.instance.usuario = self.object.usuario
            print(f"DEBUG: form.instance.estado = 'Anulado'")
            print(f"DEBUG: Retornando super().form_valid(form) con éxito")
            messages.success(self.request, 'Pedido anulado correctamente. Stock devuelto al inventario.')
            print("=" * 60)
            print("DEBUG: form_valid - FIN (rama ANULACIÓN)")
            print("=" * 60)
            return super().form_valid(form)

        print(f"DEBUG: NO es anulación, continuando...")

        # 2. La validación del formset solo si el pedido ES y SIGUE siendo Pendiente
        print(f"\nDEBUG: Verificando si db_estado == 'Pendiente': {db_estado == 'Pendiente'}")
        if db_estado == 'Pendiente':
            print(f"DEBUG: ENTRANDO en bloque de validación de formset (Pendiente)")
            context = self.get_context_data()
            detalles_formset = context['detalles_formset']
            detalles_formset.is_valid()

            detalles_validos = []
            print(f"DEBUG: Iterando sobre formset, total forms: {len(detalles_formset)}")
            for i, det_form in enumerate(detalles_formset):
                print(f"DEBUG: Procesando form {i}")
                if not hasattr(det_form, 'cleaned_data'):
                    print(f"DEBUG:   - Sin cleaned_data, skip")
                    continue
                if not det_form.cleaned_data:
                    print(f"DEBUG:   - cleaned_data vacío, skip")
                    continue
                if det_form.cleaned_data.get('DELETE', False):
                    print(f"DEBUG:   - Marcado para eliminar, skip")
                    continue
                producto = det_form.cleaned_data.get('producto')
                cantidad = det_form.cleaned_data.get('cantidad')
                if not producto or not cantidad:
                    print(f"DEBUG:   - Producto o cantidad faltante, skip")
                    continue
                print(f"DEBUG:   - Producto: {producto.nombre}, Cantidad: {cantidad}, Stock: {producto.stock}")
                if producto.stock < cantidad:
                    print(f"DEBUG:   - Stock INSUFICIENTE - retornando form_invalid")
                    messages.error(self.request,
                        f'Stock insuficiente para "{producto.nombre}". Disponible: {producto.stock}')
                    return self.form_invalid(form)
                print(f"DEBUG:   - Válido, agregando a detalles_validos")
                detalles_validos.append(det_form)

            print(f"DEBUG: Total detalles_validos: {len(detalles_validos)}")
            if not detalles_validos:
                print(f"DEBUG: Sin detalles válidos - retornando form_invalid")
                messages.error(self.request, 'Debes seleccionar al menos un producto.')
                return self.form_invalid(form)

            # Restaurar stock anterior
            print(f"DEBUG: Llamando devolver_stock() para restaurar stock anterior...")
            devolver_stock(self.object)

            # Eliminar detalles anteriores
            print(f"DEBUG: Eliminando detalles anteriores del pedido...")
            self.object.detalles.all().delete()

            # Guardar nuevos detalles y descontar stock
            print(f"DEBUG: Guardando nuevos detalles y descontando stock...")
            for det_form in detalles_validos:
                producto = det_form.cleaned_data['producto']
                cantidad = det_form.cleaned_data['cantidad']
                DetallePedido.objects.create(
                    pedido=self.object,
                    producto=producto,
                    cantidad=cantidad
                )
                producto.stock -= cantidad
                producto.save()
                print(f"DEBUG:   - Creado detalle: {producto.nombre} x{cantidad}, stock restante: {producto.stock}")

        print(f"\nDEBUG: Fuera del bloque Pendiente")
        print(f"DEBUG: Asignando cliente y usuario al form.instance...")

        # Staff no puede cambiar cliente
        form.instance.cliente = self.object.cliente
        form.instance.usuario = self.object.usuario

        print(f"DEBUG: Mensaje de éxito asignado")
        messages.success(self.request, 'Pedido actualizado.')
        print("=" * 60)
        print("DEBUG: form_valid - FIN (ruta normal)")
        print("=" * 60)
        return super().form_valid(form)

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

class PedidoDeleteView(StaffRequiredMixin, DeleteView):
    model = Pedido
    template_name = 'pedidos/pedidos/confirmar_eliminar.html'
    success_url = reverse_lazy('pedido-list')

    def form_valid(self, form):
        self.object = self.get_object()
        try:
            response = super().form_valid(form)
            messages.success(self.request, 'Pedido eliminado.')
            return response
        except (ProtectedError, IntegrityError):
            return render(self.request, 'protected_error.html',
                          {'object_type': 'pedido'}, status=400)

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
        devolver_stock(pedido)
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


def nombre_visible(request):
    """Agrega display_name, username y user_username al contexto de todos los templates."""
    if request.user.is_authenticated:
        nombre = request.user.get_full_name()
        if not nombre:
            nombre = request.user.first_name or request.user.username
        return {
            'display_name': nombre.strip(),
            'user_display_name': nombre.strip(),
            'user_username': request.user.username,
        }
    return {'display_name': '', 'user_display_name': '', 'user_username': ''}


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

            # Extrae teléfono, dirección y nombre completo del formulario
            telefono = form.cleaned_data.get('telefono', '')
            direccion = form.cleaned_data.get('direccion', '')
            nombre_completo = form.cleaned_data.get('nombre_completo', '')

            # Crea el cliente vinculado al usuario con el nombre completo real
            Cliente.objects.get_or_create(
                correo=user.email,
                defaults={
                    'nombre': nombre_completo or user.get_full_name() or user.username,
                    'telefono': telefono,
                    'direccion': direccion,
                    'usuario': user,
                }
            )

            login(request, user)
            messages.success(request, 'Cuenta creada correctamente. Bienvenido.')
            return redirect('dashboard')
        return render(request, self.template_name, {'form': form})


