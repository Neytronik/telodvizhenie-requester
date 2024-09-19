class Material:
    def __init__(self, min_layers=120, max_layers=250, max_sections=8, min_sections=4):
        super().__init__()
        self.min_layers = min_layers
        self.max_layers = max_layers
        self.max_sections = max_sections
        self.min_sections = min_sections


kulirka = Material(min_layers=120, max_layers=250, min_sections=4, max_sections=8, )
futer = Material(min_layers=20, max_layers=30, min_sections=4, max_sections=5)
karde = Material()
dvunitka = Material()
petlya = Material()
chlopok = Material()
default_material = Material(min_layers=0, max_layers=0, min_sections=0, max_sections=0)

material_params = {
    "Футер": futer,
    "Карде": karde,
    "Кулирка": kulirka,
    "Двухнитка": dvunitka,
    "Петля": petlya,
    "Хлопок": chlopok,
}
