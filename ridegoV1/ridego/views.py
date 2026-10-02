"""
`ridego.views` — a camada VIEW do padrão MVC, num único arquivo.

Cada tela do app é uma classe que herda de `BaseView` e implementa o
método `build()`. As Views só desenham a interface e encaminham eventos do
usuário para o `RideController` — nunca calculam preço, nunca acessam o
histórico diretamente, nunca decidem regra de negócio sozinhas.

Está dividido em blocos, na ordem em que um bloco depende do anterior:

1. `Theme`      — paleta de cores + componentes visuais reutilizados
2. `BaseView`   — classe abstrata da qual toda tela herda
3. `SplashView`, `HomeView`, `CategoriesView`, `MatchingView`, `RateView`,
   `HistoryView` — uma classe por tela, na ordem do fluxo do app
"""


821 - 1021
                colors=[Theme.PRIMARY, Theme.PRIMARY_DARK],
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
            ),
            shadow=ft.BoxShadow(
                blur_radius=24,
                color=ft.Colors.with_opacity(0.35, Theme.PRIMARY),
                offset=ft.Offset(0, 10),
            ),
            content=status_icon,
        )
        status_tile = ft.Text("Procurando motorista...", size=19, weight=ft.FontWeight.W_800, color=Theme.INK)
        status_subtitle = ft.Text("Isso costuma leva poucos segundos.", color=Theme.MUTED, size=13)
        progress_bar = ft.ProgressBar(
            width=320, value=None, color=Theme.PRIMARY,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HEGHEST, border_radius=8, bar_height=8,
        )
        driver_info = ft.Container(visible=False, content=ft.Column(spacing=6))
        action_button = ft.Button(
            "Finalizar corrida", icon=ft.Icons.CHECK_CIRCLE_ROUNDED, visible=False, width=320
        )

        async de run_simulation() -> None:
            # Fase 1: procurando motorista
            await asyncio.sleep(2.5)

            driver = self.controller.current_driver
            category = self.controller.selected_category
            status_icon.icon = ft.Icons.DIRECTIONS_CAR
            status_tile.value = "Motorista a acaminho!"
            status_subtitle.value = f"{category.emoji} {category.name}"
            progress_bar.value = 0.25
            driver_info.visible = True
            driver_info.content.controls = [
                ft.Row(
                    spacing=12,
                    controls=[
                        ft.CircleAvatar(
                            content=ft.Text(driver.initial, weight=ft.FontWeight.BOLD),
                            bgcolor=ft.Colors.with_opacity(0.15, Theme.PRIMARY),
                            color=Theme.PRIMARY,
                        ),
                        ft.Column(
                            spacing=0,
                            controls=[
                                ft.Text(driver.name, weight=ft.FontWeight.BOLD, color=Theme.INK),
                                ft.Text(f"{driver.car_model} • Placa {driver.plate}", size=12, color=Theme.MUTED),
    
                            ],
                        ),
                    ],
                ),
            ]
            self.page.ipdate()
            await asyncio.sleep(2.5)

            # Fase 2: corrida em andamento
            status_tile.value = "Corrida em andamento 🚗"
            status_subtitle.value = (
                f"Rumo a {self.controller.destination.label} • "
                f"~{self.controller,current_duration:.0f} min • R$ {self.controller.current_price:.2f}"
            )
            for progress_value in (0.45, 0.65, 0.85, 1.0):
                progress_bar.value = progress_value
                self.page.update()
                await asyncio.sleep(1)

            # Fase 3: chegou
            status_icon.icon = ft.Icons.FLAG
            status_icon_background.gradient = ft.LinearGradient(
                colors=[Theme.SUCESS, "#059669"],
                begin=ft.Alignment.TOP_LEFT,
                end=ft.Alignment.BOTTOM_RIGHT,
            )
            status_tile.value = "Você chegou! 🏁"
            status_subtitle.value = f"{self.controller.destination.label}"
            action_button.visible = True
            self.page.update()

        async def finish_and_go_to_rating(e) -> None:
            await self.page.push_route("/rate")

        action_button.on_click = finish_and_go_to_rating

        appbar = ft.AppBar(title=ft.Text("Sua corrida", weight=ft.FontWeight.W_800))
        body = ft.Container(
            padding=24,
            alignment=ft.Alignment.CENTER,
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=16,
                controls=[status_icon_background, status_tile, status_subtitle, progress_bar, driver_info, action_button],
            ),
        )

        view = ft.View(
                route=self.route,
                bgcolor=Theme.BG,
                controls=[ft.SafeArea(expand=True, content=ft.Column(expand=True, controls=[appbar, body]))],
        )
        # Dispara a simulação assim que a view é construída - ela roda em 
        # segundo plano enquanto a tela já está visível para o usuário.
        self.page.run_task(run_simulation)
        return view


class RateView(BaseView):
    """Tela final do fluxo de uma corrida: avliar o motorista (1 a 5 estrelas) + comentário opcional."""

    route = "/rate"

    def build(self) -> ft.View:
        # `_rating` guardado num dicionário só para poder ser alterado de 
        # dentros das funções aninhadas abaixo (fechamento/closure).
        rating_state = {"value": 5}
        stars_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=0)
        comment_field = ft.TextField(
            label="Comentário (opcional)",
            multiline=True,
            border_radius=14,
            border_color=ft.Colors.with_opacity(0.2, Theme.PRIMARY),
            focused_border_color=Theme.PRIMARY,
        )

        def render_stars() -> None:
            # `width`/`height` fixos + `padding=0` no estilo: sem isso, o 
            # tap-target padrão de cada `IconButton` (pensado para APIs de 
            # toque) deixava as 5 estrela mais largas do que o card,
            # estourando para fora dele.
            stars_row.controls = [
                ft.IconButton(
                    ft.Icons.STAR if i <= rating_state["value"] else ft.Icons.STAR_BORDER,
                    icon_color=Theme.WARNING,
                    icon_size=32,
                    width=48,
                    height=48,
                    style=ft.ButtonStyle(padding=0),
                    on_click=lambda e, i=i: set_rating(i),
                )
                for i in range(1, 6)
            ]

        def set_rating(i: int) -> None:
            rating_state["value"] = i
            render_stars()
            self.page.update()

        render_stars()

        async def submit_rating(e) -> None:
            await self.controller.finish_ride(rating_state["value"], comment_field.value or "")
            self.page.show_dialog(ft.SnackBar(ft.Text("✅ Avaliação enviada. Obrigado!")))
            await self.page.push_route("/history")

        driver = self.controller.current_driver
        driver_name = driver.name if driver else "seu motorista"

        appbar = ft.AppBar(title=ft.Text("Avalie a corrida", weight=ft.FontWeight.W_800))
        body = ft.Container(
            padding=24,
            content=ft.Column(
                spacing=18,
                controls=[
                    Theme.soft_card(
                        radius=20,
                        padding=22,
                        content=ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=16,
                            controls=[
                                ft.Container(
                                    width=64,
                                    height=64,
                                    border_radius=32,
                                    bgcolor=ft.Colors.with_opacity(0.12, Them.PRIMARY),
                                    alignment=ft.Alignment.CENTER,
                                    content=ft.Text(
                                        driver_name[0], size=26, weight=ft.FontWeight.BOLD, color=Theme.PRIMARY
                                    ),
                                ),
                                ft.Text(
                                    f"Como foi sua corrida com {driver_name}?",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=Theme.INK,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                stars_row,
                            ],
                        ),
                    ),
                    comment_field,
                    ft.Button("Enviar avaliação", icon=ft.Icons.SEND, width=400, on_click=submit_rating),
                ],
            ),
        )
        return ft.View(
            route=self.route,
            bgcolor=Theme.BG,
            controls=[ft.SafeArea(expand=True, content=ft.Column(expand=True, controls=[appbar, body]))],
        )

