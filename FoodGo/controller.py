"""
controller.py — camada CONTROLLER do padrão MVC.

Uma única classe, `AppController`, cuidando de TODA a regra de negócio
do app: consultar/filtrar restaurantes, gerenciar o carrinho, gerenciar
o histórico de pedidos e persistir tudo isso em disco. As Views
(`views.py`) só chamam métodos daqui — nunca calculam totais, nunca
leem/gravam SharedPreferences diretamente.

ENCAPSULAMENTO: o estado (`_cart`, `_orders`, etc.) fica em atributos
"privados" (prefixo `_`); o resto do app só acessa através de
propriedades (`cart`, `cart_count`, ...) e métodos (`add_item`,
`change_qty`, ...), que sabem manter tudo consistente (ex.: salvar em
disco depois de cada mudança).

--------------------------------------------------------------------------
SOBRE O "SALVAMENTO EM SEGUNDO PLANO" (fire-and-forget)
--------------------------------------------------------------------------
Cada ação do carrinho (adicionar item, +1, -1) precisa:
    1) mudar os dados em memória (o que a tela mostra), e
    2) gravar essa mudança em disco, para não se perder ao fechar o app.

Se o passo 2 fosse sempre feito com `await` (esperando terminar antes de
liberar a tela), o app pareceria "lento" a cada toque, porque gravar em
disco (ou no navegador, na versão web) pode levar um tempinho perceptível.
A solução: o passo 1 é imediato, e o passo 2 roda "por trás", disparado
com `asyncio.create_task(...)` em vez de `await` — a tela já pode ser
redesenhada enquanto o salvamento termina sozinho (ver `_fire_and_forget`).
"""

# Digitar a partir deste ponto (2ª digitação)
