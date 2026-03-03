from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from django.db.models import Q
from finance.models import Transaccion, SubCategoria, TipoTransaccion, Moneda, MetodoPago
from usuario.models import Persona
import os 
# 1. IMPORTAMOS LA NUEVA LIBRERÍA
from google import genai
from django.utils import timezone

# 2. INICIALIZAMOS EL CLIENTE NUEVO (Pon tu clave aquí)
client = genai.Client(api_key=os.getenv('GEMINI_API_KEY'))  # Asegúrate de tener esta variable en tu .env

@api_view(['POST'])
def procesar_compras_por_voz(request):
    texto_usuario = request.data.get('texto', '')

    if not texto_usuario:
        return Response({'error': 'No se envió ningún texto'}, status=status.HTTP_400_BAD_REQUEST)

    # 1. Obtener Subcategorías permitidas
    nombres_subcategorias = list(SubCategoria.objects.filter(
        Q(usuario=request.user) | Q(usuario__isnull=True)
    ).values_list('nombre', flat=True))
    lista_categorias_str = ", ".join(nombres_subcategorias)

    # 2. NUEVO: Obtener Personas registradas por este usuario
    nombres_personas = list(Persona.objects.filter(usuario=request.user).values_list('nombre', flat=True))
    lista_personas_str = ", ".join(nombres_personas) if nombres_personas else "Ninguna persona registrada"

    # 3. PROMPT MEJORADO: Reglas semánticas y de personas
    
    # Esto fuerza la hora a tu zona horaria (ej: 2026-03-02T22:24:18-04:00)
    fecha_hora_actual = timezone.localtime(timezone.now()).isoformat()

    prompt = f"""
    Eres un asistente financiero experto. Analiza el texto del usuario y extrae las transacciones.
    Fecha y hora actual del sistema: {fecha_hora_actual}
    
    Texto del usuario: "{texto_usuario}"

    Reglas ESTRICTAS:
    1. Devuelve ÚNICAMENTE un array en formato JSON puro.
    2. Cada objeto debe tener estas llaves:
       - "monto": (número decimal)
       - "concepto": (texto corto)
       - "tipo_transaccion": (estrictamente "Ingreso" o "Egreso")
       - "subcategoria": (Elige de esta lista: [{lista_categorias_str}]). 
         REGLA DE CONTEXTO: Si dice "le presté", usa 'Préstamo'. Si dice "le di" o "regalé", usa 'Regalo', A MENOS QUE se especifique el propósito (ej. "le di para pasaje" -> 'Transporte'). La prioridad es el propósito del gasto.
       - "persona": (Busca en: [{lista_personas_str}]. Si no está, devuelve null).
       - "fecha_registro": (Calcula la fecha y hora si el usuario indica un tiempo en el pasado, como "ayer" o "hace una hora". Usa esta fecha y hora actual como punto de partida: "{fecha_hora_actual}". Devuelve el resultado ESTRICTAMENTE en formato ISO 8601 INCLUYENDO EL DESFASE HORARIO. Tiene que mantener exactamente la misma estructura y el mismo desfase que la fecha de partida. Si el usuario no menciona fecha ni hora, devuelve exactamente esta cadena: "{fecha_hora_actual}").
    """

    try:
        # response = client.models.generate_content(
        #     model="gemini-3-flash-preview",
        #     contents=prompt,
        # )
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=prompt,
        )
        
        texto_limpio = response.text.strip()

        if texto_limpio.startswith("```json"):
            texto_limpio = texto_limpio[7:-3]
        elif texto_limpio.startswith("```"):
            texto_limpio = texto_limpio[3:-3]

        datos_json = json.loads(texto_limpio)

    except Exception as e:
        return Response({'error': f'Error al procesar con IA: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 4. Guardar en la Base de Datos incluyendo la Persona
    transacciones_creadas = 0
    try:
        moneda_default = Moneda.objects.first()
        metodo_pago_default = MetodoPago.objects.first()

        for item in datos_json:
            tipo_obj = TipoTransaccion.objects.filter(nombre__icontains=item['tipo_transaccion']).first()
            subcat_obj = SubCategoria.objects.filter(nombre__icontains=item['subcategoria']).first()
            
            # NUEVO: Buscar el objeto Persona si la IA detectó a alguien
            persona_obj = None
            if item.get('persona'):
                persona_obj = Persona.objects.filter(
                    usuario=request.user, 
                    nombre__icontains=item['persona']
                ).first()

            Transaccion.objects.create(
                usuario=request.user,
                monto=item['monto'],
                concepto=item['concepto'],
                tipo_transaccion=tipo_obj,
                subcategoria=subcat_obj,
                persona=persona_obj, # <-- Guardamos la persona aquí
                fecha_registro=item.get('fecha_registro', timezone.now()), # <-- AGREGAMOS LA FECHA AQUÍ
                moneda=moneda_default,
                metodo_pago=metodo_pago_default
            )
            transacciones_creadas += 1

        return Response({
            'mensaje': f'Éxito: Se registraron {transacciones_creadas} transacciones.',
            'datos': datos_json
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': f'Error al guardar en BD: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)