from django.urls import path
from . import views

from .exports import exportar_pdf, exportar_excel, exportar_clientes_pdf, exportar_clientes_excel

urlpatterns = [
    path('', views.DashboardView.as_view(), name='dashboard'),
    # Clientes
    path('clientes/',            views.ClienteListView.as_view(),   name='cliente-list'),
    path('clientes/nuevo/',      views.ClienteCreateView.as_view(), name='cliente-create'),
    path('clientes/<int:pk>/editar/', views.ClienteUpdateView.as_view(), name='cliente-update'),
    path('clientes/<int:pk>/eliminar/', views.ClienteDeleteView.as_view(), name='cliente-delete'),

    # Productos
    path('productos/',            views.ProductoListView.as_view(),   name='producto-list'),
    path('productos/nuevo/',      views.ProductoCreateView.as_view(), name='producto-create'),
    path('productos/<int:pk>/editar/', views.ProductoUpdateView.as_view(), name='producto-update'),
    path('productos/<int:pk>/eliminar/', views.ProductoDeleteView.as_view(), name='producto-delete'),

    # Pedidos
    path('pedidos/',             views.PedidoListView.as_view(),   name='pedido-list'),
    path('mis-pedidos/',         views.MisPedidosView.as_view(),   name='mis-pedidos'),
    path('pedidos/nuevo/',       views.PedidoCreateView.as_view(), name='pedido-create'),
    path('pedidos/<int:pk>/editar/', views.PedidoUpdateView.as_view(), name='pedido-update'),
    path('pedidos/<int:pk>/eliminar/', views.PedidoDeleteView.as_view(), name='pedido-delete'),
    path('pedidos/<int:pk>/anular/',   views.AnularPedidoView.as_view(), name='pedido-anular'),

    # Sesión
    path('renovar-sesion/', views.RenovarSesionView.as_view(), name='renovar-sesion'),

    # Exportación
    path('pedidos/exportar/pdf/',    exportar_pdf,            name='exportar-pdf'),
    path('pedidos/exportar/excel/',  exportar_excel,          name='exportar-excel'),
    path('clientes/exportar/pdf/',   exportar_clientes_pdf,   name='exportar-clientes-pdf'),
    path('clientes/exportar/excel/', exportar_clientes_excel, name='exportar-clientes-excel'),
]


