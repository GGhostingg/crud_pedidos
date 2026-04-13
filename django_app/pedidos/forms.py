import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Cliente, Producto, Pedido

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label='Usuario',
        max_length=150,
        strip=True,
        validators=[],
        help_text='Puede incluir espacios y los símbolos @ . + - _',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su usuario'
        }),
        error_messages={
            'required': 'El usuario es obligatorio.',
            'invalid': 'El usuario solo puede contener letras, números, espacios y @ . + - _'
        }
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if not re.match(r'^[A-Za-z0-9 @.+_-]+$', username):
                raise ValidationError('El usuario solo puede contener letras, números, espacios y @ . + - _')
        return username

    def _post_clean(self):
        super()._post_clean()
        # Django's UnicodeUsernameValidator (del modelo User) rechaza espacios,
        # pero nuestra clean_username ya los validó. Si clean_username pasó
        # eliminamos el error que el modelo haya añadido para username.
        if 'username' in self._errors and self.cleaned_data.get('username'):
            self._errors.pop('username', None)

    email = forms.EmailField(
        required=True,
        label='Correo electrónico',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'correo@ejemplo.com'
        }),
        error_messages={
            'required': 'El correo es obligatorio.',
            'invalid': 'Introduce un correo válido.'
        }
    )

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

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'username': 'Usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar contraseña',
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese su usuario'
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

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Este correo ya está registrado.')
        return email

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

class PedidoCreateForm(forms.ModelForm):
    producto = forms.ModelChoiceField(
        queryset=Producto.objects.filter(stock__gt=0),
        label='Producto',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        initial=1,
        label='Cantidad',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )

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

    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')
        if producto and cantidad and cantidad > producto.stock:
            self.add_error('cantidad', 'No hay suficiente stock para este producto.')
        return cleaned_data

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
