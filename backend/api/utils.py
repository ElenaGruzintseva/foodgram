from django.http import HttpResponse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.pdfgen import canvas


def generate_shopping_list_pdf(recipes_in_shopping_list):
    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = 'attachment; filename="shopping_list.pdf"'

    p = canvas.Canvas(response)

    pdfmetrics.registerFont(TTFont("Arial", "./recipes/fonts/arial.ttf"))
    p.setFont("Arial", 15)

    p.drawString(100, 800, "Список покупок:")

    y_position = 780

    for recipe in recipes_in_shopping_list:
        name = recipe["ingredient__name"]
        total_amount = recipe["total_amount"]
        measurement_unit = recipe["ingredient__measurement_unit"]

        item_text = f"{name} ({measurement_unit}) - {total_amount}"
        p.drawString(100, y_position, item_text)

        y_position -= 20

    p.showPage()
    p.save()

    return response
