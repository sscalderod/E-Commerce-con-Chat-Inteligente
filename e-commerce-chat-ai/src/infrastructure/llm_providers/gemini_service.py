import asyncio
import os

import google.generativeai as genai
from dotenv import load_dotenv

from src.domain.entities import ChatContext, Product
from src.domain.exceptions import ChatServiceError


class GeminiService:
    """Servicio de infraestructura para generar respuestas con Google Gemini.

    Encapsula la configuracion del cliente y la construccion de prompts
    orientados al catalogo de productos y contexto conversacional.
    """

    def __init__(self) -> None:
        """Configura cliente Gemini usando variables de entorno.

        Raises:
            ChatServiceError: Si no existe GEMINI_API_KEY.
        """
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ChatServiceError("No se encontro GEMINI_API_KEY en variables de entorno")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def generate_response(
        self,
        user_message: str,
        products: list[Product],
        context: ChatContext,
    ) -> str:
        """Genera una respuesta contextual usando productos y memoria conversacional.

        Args:
            user_message (str): Mensaje actual del usuario.
            products (list[Product]): Catalogo disponible para recomendaciones.
            context (ChatContext): Historial reciente de la sesion.

        Returns:
            str: Texto de respuesta generado por el modelo.

        Raises:
            ChatServiceError: Si hay un fallo al invocar Gemini.
        """
        try:
            products_text = self.format_products_info(products)
            history_text = context.format_for_prompt()

            prompt = (
                "Eres un asistente virtual experto en ventas de zapatos para un e-commerce.\n"
                "Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.\n\n"
                "PRODUCTOS DISPONIBLES:\n"
                f"{products_text}\n\n"
                "INSTRUCCIONES:\n"
                "- Se amigable y profesional.\n"
                "- Usa el contexto de la conversacion anterior.\n"
                "- Recomienda productos especificos cuando sea apropiado.\n"
                "- Menciona precios, tallas y disponibilidad.\n"
                "- Si no tienes informacion, se honesto.\n\n"
                "HISTORIAL DE LA CONVERSACION:\n"
                f"{history_text if history_text else 'Sin historial previo.'}\n\n"
                f"Usuario: {user_message}\n\n"
                "Asistente:"
            )

            response = await asyncio.to_thread(self.model.generate_content, prompt)
            answer = (response.text or "").strip() if response else ""
            if not answer:
                return "No pude generar una respuesta en este momento. Intenta nuevamente."
            return answer
        except Exception as error:
            raise ChatServiceError(f"Error al generar respuesta con Gemini: {error}") from error

    def format_products_info(self, products: list[Product]) -> str:
        """Formatea el inventario para incorporarlo en el prompt del modelo.

        Args:
            products (list[Product]): Productos del catalogo.

        Returns:
            str: Texto multilinea con informacion relevante del inventario.
        """
        if not products:
            return "No hay productos disponibles actualmente."

        lines: list[str] = []
        for product in products:
            lines.append(
                "- "
                f"{product.name} | Marca: {product.brand} | Categoria: {product.category} "
                f"| Talla: {product.size} | Color: {product.color} "
                f"| Precio: ${product.price:.2f} | Stock: {product.stock}"
            )
        return "\n".join(lines)
