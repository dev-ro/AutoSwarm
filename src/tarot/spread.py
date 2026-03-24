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

    def display(self, target_signs=None):
        cprint(f"Spread: {self.name.capitalize().replace('_', ' ')}", attrs=['underline', 'bold'])
        print(self.description)
        print()
        print(f"Ideal questions to answer: {self.questions}\n")
        
        relevant_cards_count = 0
        found_signs = set()

        for position, card in self.cards.items():
            color = self.get_color(card.element)
            attrs = ['bold'] if card.is_upright else []
            
            highlight = False
            if target_signs:
                for sign in target_signs:
                    if card.matches_sign(sign):
                        highlight = True
                        found_signs.add(sign)
                        break
            
            pos_display = f"{position}:"
            if highlight:
                pos_display += " [CUSP RELEVANT]"
                relevant_cards_count += 1
            
            print(pos_display)
            cprint(f"{card}", color, attrs=attrs)
            print()
        
        print(f"Elemental Dignities: {self.elemental_dignity()}")
        
        if target_signs and relevant_cards_count > 0:
            signs_str = " & ".join(target_signs)
            print(f"\nCUSP ANALYSIS ({signs_str}):")
            print(f"Total Cusp-Relevant Cards: {relevant_cards_count}")
            if len(found_signs) > 1:
                print("STRENGTHENED CUSP: Cards from BOTH signs of your cusp appeared, indicating a powerful alignment of your dual nature.")
            else:
                print(f"Focus on {list(found_signs)[0]} qualities within your cusp placement.")
        
        print()

    def get_analysis_data(self, target_signs=None, persona="main_character"):
        relevant_cards_count = 0
        found_signs = set()
        
        cards_data = []
        for position, card in self.cards.items():
            highlight = False
            if target_signs:
                for sign in target_signs:
                    if card.matches_sign(sign):
                        highlight = True
                        found_signs.add(sign)
                        break
            
            c_dict = card.to_dict(persona=persona)
            c_dict["position"] = position
            c_dict["cusp_relevant"] = highlight
            cards_data.append(c_dict)
            if highlight:
                relevant_cards_count += 1

        synthesis = {
            "elemental_dignities": self.elemental_dignity()
        }
        
        if target_signs:
            summary = ""
            if relevant_cards_count > 0:
                if len(found_signs) > 1:
                    summary = "STRENGTHENED CUSP: Cards from BOTH signs of your cusp appeared, indicating a powerful alignment of dual nature."
                else:
                    summary = f"Focus on {list(found_signs)[0]} qualities within your cusp placement."
            else:
                summary = "No cusp-relevant cards found."

            synthesis["cusp_analysis"] = {
                "target_signs": target_signs,
                "relevant_cards_count": relevant_cards_count,
                "found_signs": list(found_signs),
                "summary": summary
            }
        
        return {
            "cards": cards_data,
            "synthesis": synthesis
        }

    def get_color(self, element):
        if element == 'Fire':
            return 'red'
        elif element == 'Water':
            return 'blue'
        elif element == 'Earth':
            return 'green'
        elif element == 'Air':
            return 'cyan'
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