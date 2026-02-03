from termcolor import cprint

class Spread:
    def __init__(self, name, description, questions, positions):
        self.name = name
        self.description = description
        self.questions = questions
        self.positions = positions
        self.cards = {}

    def draw_cards(self, deck, upright_only=False):
        self.cards = {position: deck.draw_card(upright_only=upright_only) for position in self.positions}

    def display(self):
        cprint(f"Spread: {self.name.capitalize().replace('_', ' ')}", attrs=['underline', 'bold'])
        print(self.description)
        print()
        print(f"Ideal questions to answer: {self.questions}\n")
        for position, card in self.cards.items():
            color = self.get_color(card.element)
            attrs = ['bold'] if card.is_upright else []
            print(f"{position}:")
            cprint(f"{card}", color, attrs=attrs)
            print()
        print(f"Elemental Dignities: {self.elemental_dignity()}")
        print()

    def get_color(self, element):
        if element == 'Fire':
            return 'red'
        elif element == 'Water':
            return 'blue'
        elif element == 'Earth':
            return 'green'
        elif element == 'Air':
            return 'cyan'
        elif element == 'Major':
            return 'magenta'
        else:
            return None  # Default color

    def elemental_dignity(self):
        elements = [card.element for card in self.cards.values()]
        dignity = {'strengthen': 0, 'weaken': 0, 'neutral': 0}

        element_pairs = {
            ('Fire', 'Air'), ('Air', 'Fire'),
            ('Water', 'Earth'), ('Earth', 'Water'),
            ('Fire', 'Water'), ('Water', 'Fire'),
            ('Air', 'Earth'), ('Earth', 'Air')
        }

        for i in range(len(elements)):
            for j in range(i + 1, len(elements)):
                if elements[i] == 'Major' or elements[j] == 'Major':
                    continue
                if elements[i] == elements[j]:
                    dignity['strengthen'] += 1
                elif (elements[i], elements[j]) in element_pairs:
                    if (elements[i], elements[j]) in {('Fire', 'Air'), ('Air', 'Fire'), ('Water', 'Earth'), ('Earth', 'Water')}:
                        dignity['strengthen'] += 1
                    else:
                        dignity['weaken'] += 1
                else:
                    dignity['neutral'] += 1

        return dignity
