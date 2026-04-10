from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from .models import Pedido, Cliente


@login_required
def exportar_pdf(request):
    if not request.user.is_staff:
        raise PermissionDenied
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=pedidos.pdf'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph('Reporte de Pedidos', styles['Title']))

    pedidos = Pedido.objects.select_related('cliente').all()
    datos = [['ID', 'Cliente', 'Fecha', 'Estado']]
    for p in pedidos:
        datos.append([
            str(p.id),
            p.cliente.nombre,
            p.fecha.strftime('%Y-%m-%d'),
            p.estado
        ])

    tabla = Table(datos, colWidths=[40, 200, 100, 100])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A5F')),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#EBF5FB')]),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elementos.append(tabla)
    doc.build(elementos)
    return response


@login_required
def exportar_excel(request):
    if not request.user.is_staff:
        raise PermissionDenied
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=pedidos.xlsx'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Pedidos'

    azul_fill = PatternFill('solid', fgColor='1E3A5F')
    blanco_font = Font(bold=True, color='FFFFFF')

    encabezados = ['ID', 'Cliente', 'Fecha', 'Estado']
    for col, enc in enumerate(encabezados, 1):
        c = ws.cell(row=1, column=col, value=enc)
        c.fill = azul_fill
        c.font = blanco_font
        c.alignment = Alignment(horizontal='center')

    for fila, p in enumerate(Pedido.objects.select_related('cliente').all(), 2):
        ws.cell(row=fila, column=1, value=p.id)
        ws.cell(row=fila, column=2, value=p.cliente.nombre)
        ws.cell(row=fila, column=3, value=p.fecha.strftime('%Y-%m-%d'))
        ws.cell(row=fila, column=4, value=p.estado)

    wb.save(response)
    return response


@login_required
def exportar_clientes_pdf(request):
    if not request.user.is_staff:
        raise PermissionDenied
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=clientes.pdf'

    doc = SimpleDocTemplate(response, pagesize=A4)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph('Reporte de Clientes', styles['Title']))

    datos = [['ID', 'Nombre', 'Correo', 'Teléfono']]
    for c in Cliente.objects.all():
        datos.append([str(c.id), c.nombre, c.correo, c.telefono or ''])

    tabla = Table(datos, colWidths=[40, 160, 180, 100])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E3A5F')),
        ('TEXTCOLOR',  (0,0), (-1,0), colors.white),
        ('FONTNAME',   (0,0), (-1,0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#EBF5FB')]),
        ('GRID',       (0,0), (-1,-1), 0.5, colors.grey),
    ]))
    elementos.append(tabla)
    doc.build(elementos)
    return response


@login_required
def exportar_clientes_excel(request):
    if not request.user.is_staff:
        raise PermissionDenied
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=clientes.xlsx'

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Clientes'

    azul_fill = PatternFill('solid', fgColor='1E3A5F')
    blanco_font = Font(bold=True, color='FFFFFF')

    encabezados = ['ID', 'Nombre', 'Correo', 'Teléfono']
    for col, enc in enumerate(encabezados, 1):
        c = ws.cell(row=1, column=col, value=enc)
        c.fill = azul_fill
        c.font = blanco_font
        c.alignment = Alignment(horizontal='center')

    for fila, cliente in enumerate(Cliente.objects.all(), 2):
        ws.cell(row=fila, column=1, value=cliente.id)
        ws.cell(row=fila, column=2, value=cliente.nombre)
        ws.cell(row=fila, column=3, value=cliente.correo)
        ws.cell(row=fila, column=4, value=cliente.telefono or '')

    wb.save(response)
    return response
