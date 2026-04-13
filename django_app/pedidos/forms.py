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

        if not nombre:
            raise ValidationError('El nombre es obligatorio.')

        nombre = nombre.strip()

        if len(nombre) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres.')

        if len(nombre) > 150:
            raise ValidationError('El nombre no puede tener más de 150 caracteres.')

        # Validar que no contenga números
        if re.search(r'\d', nombre):
            raise ValidationError('El nombre no puede contener números.')

        # Validar que no contenga caracteres especiales inválidos
        # Solo se permiten letras, espacios, acentos, ñ, y apóstrofes/guiones en nombres compuestos
        if not re.match(r"^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s'\-]+$", nombre):
            raise ValidationError('El nombre solo puede contener letras, espacios y caracteres válidos (acentos, ñ, guiones).')

        # Validar que tenga al menos una letra (no solo espacios)
        if not re.search(r'[A-Za-záéíóúÁÉÍÓÚñÑüÜ]', nombre):
            raise ValidationError('El nombre debe contener al menos una letra.')

        # Validar que no sea solo espacios repetidos
        if not nombre or len(nombre.replace(' ', '')) < 3:
            raise ValidationError('El nombre debe tener al menos 3 caracteres (sin contar espacios).')

        # Validar que cada palabra tenga al menos 2 caracteres (evitar "a b c")
        palabras = nombre.split()
        for palabra in palabras:
            if len(palabra) < 2:
                raise ValidationError(f'Cada palabra del nombre debe tener al menos 2 caracteres. "{palabra}" es demasiado corta.')

        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()

        if not telefono:
            return telefono

        # Validar que solo contenga dígitos, espacios, guiones, paréntesis y signo +
        if not re.match(r'^[\d\s\-\(\)\+]+$', telefono):
            raise forms.ValidationError('El teléfono solo puede contener números, espacios, guiones y paréntesis.')

        # Extraer solo los dígitos para contar
        solo_digitos = re.sub(r'[^\d]', '', telefono)

        if len(solo_digitos) < 7:
            raise forms.ValidationError('El teléfono debe tener al menos 7 dígitos.')

        if len(solo_digitos) > 10:
            raise forms.ValidationError('El teléfono no puede tener más de 10 dígitos.')

        return telefono

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion', '').strip()

        if not direccion:
            return direccion

        if len(direccion) > 200:
            raise forms.ValidationError('La dirección no puede tener más de 200 caracteres.')

        # Validar que no contenga caracteres potencialmente peligrosos (prevención XSS)
        if re.search(r'[<>"\';/]', direccion):
            raise forms.ValidationError('La dirección contiene caracteres no permitidos.')

        return direccion

    def save(self, commit=True):
        user = super().save(commit=False)
        # Generar username único a partir del email
        email_prefix = self.cleaned_data['email'].split('@')[0]
        base_username = re.sub(r'[^A-Za-z0-9_.]', '', email_prefix).lower()
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

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if not nombre:
            raise forms.ValidationError('El nombre es obligatorio.')

        nombre = nombre.strip()

        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')

        if len(nombre) > 100:
            raise forms.ValidationError('El nombre no puede tener más de 100 caracteres.')

        # Validar que no contenga números
        if re.search(r'\d', nombre):
            raise forms.ValidationError('El nombre no puede contener números.')

        # Validar que no contenga caracteres especiales inválidos
        if not re.match(r"^[A-Za-záéíóúÁÉÍÓÚñÑüÜ\s'\-]+$", nombre):
            raise forms.ValidationError('El nombre solo puede contener letras, espacios y caracteres válidos (acentos, ñ, guiones).')

        # Validar que tenga al menos una letra
        if not re.search(r'[A-Za-záéíóúÁÉÍÓÚñÑüÜ]', nombre):
            raise forms.ValidationError('El nombre debe contener al menos una letra.')

        # Validar que no sea solo espacios repetidos
        if not nombre or len(nombre.replace(' ', '')) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres (sin contar espacios).')

        # Validar que cada palabra tenga al menos 2 caracteres
        palabras = nombre.split()
        for palabra in palabras:
            if len(palabra) < 2:
                raise forms.ValidationError(f'Cada palabra del nombre debe tener al menos 2 caracteres. "{palabra}" es demasiado corta.')

        return nombre

    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()

        if not telefono:
            return telefono

        # Validar que solo contenga dígitos, espacios, guiones, paréntesis y signo +
        if not re.match(r'^[\d\s\-\(\)\+]+$', telefono):
            raise forms.ValidationError('El teléfono solo puede contener números, espacios, guiones y paréntesis.')

        # Extraer solo los dígitos para contar
        solo_digitos = re.sub(r'[^\d]', '', telefono)

        if len(solo_digitos) < 7:
            raise forms.ValidationError('El teléfono debe tener al menos 7 dígitos.')

        if len(solo_digitos) > 15:
            raise forms.ValidationError('El teléfono no puede tener más de 15 dígitos.')

        return telefono

    def clean_direccion(self):
        direccion = self.cleaned_data.get('direccion', '').strip()

        if not direccion:
            return direccion

        if len(direccion) > 200:
            raise forms.ValidationError('La dirección no puede tener más de 200 caracteres.')

        # Validar que no contenga caracteres potencialmente peligrosos (prevención XSS)
        if re.search(r'[<>"\';/]', direccion):
            raise forms.ValidationError('La dirección contiene caracteres no permitidos.')

        return direccion

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

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')

        if not nombre:
            raise forms.ValidationError('El nombre es obligatorio.')

        nombre = nombre.strip()

        if len(nombre) < 3:
            raise forms.ValidationError('El nombre debe tener al menos 3 caracteres.')

        if len(nombre) > 100:
            raise forms.ValidationError('El nombre no puede tener más de 100 caracteres.')

        # Validar que no contenga números (opcional para productos, pero útil)
        # Se permiten números en nombres de productos (ej: "iPhone 15"), así que solo validamos caracteres peligrosos
        if re.search(r'[<>"\';/]', nombre):
            raise forms.ValidationError('El nombre contiene caracteres no permitidos.')

        return nombre


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
        'invalid_login': 'Correo o contraseña incorrectos.',
        'inactive': 'Esta cuenta no está activa.',
    }
    username = forms.CharField(
        label='Correo electrónico',
        strip=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'correo@ejemplo.com'})
    )
    password = forms.CharField(
        label='Contraseña',
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )

    def clean_username(self):
        email = self.cleaned_data.get('username')
        if email:
            # Validate email format
            try:
                from django.core.validators import validate_email
                validate_email(email)
            except Exception:
                raise ValidationError('Introduce un correo electrónico válido.')
        return email

    def confirm_login_allowed(self, user):
        # Authenticate by email: override username field with the user's actual username
        # This is handled in the view, so we just check is_active
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages.get('inactive', 'Esta cuenta no está activa.'),
                code='inactive',
            )
