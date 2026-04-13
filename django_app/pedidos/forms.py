import re

from django import forms
from django.forms import formset_factory, BaseFormSet
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Cliente, Producto, Pedido

class CustomUserCreationForm(UserCreationForm):
    nombre_completo = forms.CharField(
        label='Nombre completo',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: Julieta Meza'
        }),
        error_messages={
            'required': 'El nombre es obligatorio.',
        }
    )

    class Meta:
        model = User
        fields = ['nombre_completo', 'email', 'password1', 'password2']
        labels = {
            'email': 'Correo electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'correo@ejemplo.com'
            }),
            'password1': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su contraseña'
            }),
            'password2': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Confirma la contraseña'
            }),
        }

    telefono = forms.CharField(
        required=False,
        label='Teléfono',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Número de teléfono (opcional)'
        })
    )

    direccion = forms.CharField(
        required=False,
        label='Dirección',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tu dirección (opcional)'
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

    def clean_nombre_completo(self):
        nombre = self.cleaned_data.get('nombre_completo')
        if nombre and len(nombre.strip()) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')
        return nombre.strip()

    def save(self, commit=True):
        user = super().save(commit=False)
        # Generar username unico a partir del email (sin espacios, sin @)
        email_prefix = self.cleaned_data['email'].split('@')[0]
        base_username = re.sub(r'[^A-Za-z0-9_.]', '', email_prefix)
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f'{base_username}{counter}'
            counter += 1
        user.username = username
        user.set_password(self.cleaned_data["password1"])
        user.first_name = self.cleaned_data.get('nombre_completo', '').split()[0] if self.cleaned_data.get('nombre_completo') else ''
        user.last_name = ' '.join(self.cleaned_data.get('nombre_completo', '').split()[1:]) if self.cleaned_data.get('nombre_completo') else ''
        if commit:
            user.save()
        return user

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'correo', 'direccion', 'telefono']
        labels = {
            'nombre': 'Nombre',
            'correo': 'Correo electrónico',
            'direccion': 'Dirección',
            'telefono': 'Teléfono',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cliente'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Dirección'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Teléfono'}),
        }
        error_messages = {
            'nombre': {'required': 'El nombre es obligatorio.'},
            'correo': {'required': 'El correo es obligatorio.', 'invalid': 'Introduce un correo válido.'},
        }

    def clean_correo(self):
        correo = self.cleaned_data.get('correo')
        if self.instance.pk:
            existe = Cliente.objects.exclude(pk=self.instance.pk).filter(correo=correo).exists()
        else:
            existe = Cliente.objects.filter(correo=correo).exists()
        if existe:
            raise forms.ValidationError('Este correo ya está registrado para otro cliente.')
        return correo

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'precio', 'stock']
        labels = {
            'nombre': 'Nombre',
            'precio': 'Precio',
            'stock': 'Stock',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del producto'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }
        error_messages = {
            'nombre': {'required': 'El nombre es obligatorio.'},
            'precio': {'required': 'El precio es obligatorio.'},
            'stock': {'required': 'El stock es obligatorio.'},
        }

    def clean_precio(self):
        precio = self.cleaned_data.get('precio')
        if precio is not None and precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor que cero.')
        return precio

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None and stock < 0:
            raise forms.ValidationError('El stock no puede ser negativo.')
        return stock


class DetallePedidoForm(forms.Form):
    """Un detalle individual dentro del formulario de pedido."""
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(stock__gt=0),
        label='Producto',
        widget=forms.Select(attrs={'class': 'form-select detalle-producto'})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Cantidad',
        widget=forms.NumberInput(attrs={'class': 'form-control detalle-cantidad', 'min': '1'})
    )


# Formset para múltiples detalles de pedido
DetallePedidoFormSet = formset_factory(
    DetallePedidoForm,
    extra=1,
    can_delete=True,
)


class PedidoCreateForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'estado']
        labels = {
            'cliente': 'Cliente',
            'estado': 'Estado',
        }
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['cliente', 'estado']
        labels = {
            'cliente': 'Cliente',
            'estado': 'Estado',
        }
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
        }

class CustomAuthenticationForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Usuario o contraseña incorrectos.',
        'inactive': 'Esta cuenta no está activa.',
    }
    username = forms.CharField(
        label='Usuario',
        strip=False,
        help_text='Puede incluir espacios y los símbolos @ . + - _',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and not re.match(r'^[A-Za-z0-9 @.+_-]+$', username):
            raise ValidationError('El usuario solo puede contener letras, números, espacios y @ . + - _')
        return username
