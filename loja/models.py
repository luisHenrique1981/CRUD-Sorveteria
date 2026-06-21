from django.db import models
from django.contrib.auth.models import User


class ItemCarrinho(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    session_key = models.CharField(
        max_length=100,
        null=True,
        blank=True
    )

    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    quantidade = models.PositiveIntegerField(default=1)
    imagem = models.CharField(max_length=255, blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)

    def subtotal(self):
        return self.preco * self.quantidade

    def __str__(self):
        return f"{self.nome} - {self.quantidade} unidade(s)"

class Produto(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    preco = models.DecimalField(max_digits=8, decimal_places=2)
    descricao = models.TextField(blank=True, null=True)
    # A imagem segue a mesma lógica de texto (ex: img/menu/sorvete.jpg) para casar com o seu HTML
    imagem = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} - {self.categoria}"