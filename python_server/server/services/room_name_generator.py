"""
Room name generator.
Port of server/service/RoomNameGenerator.js
"""
import random


class RoomNameGenerator:
    """
    Generates random room names.
    """
    
    adjectives = [
        'awesome', 'amazing', 'great', 'fantastic', 'super',
        'admirable', 'famous', 'fine', 'gigantic', 'grand',
        'marvelous', 'mighty', 'outstanding', 'splendid', 'wonderful',
        'big', 'super', 'smashing', 'sensational'
    ]
    
    nouns = [
        'game', 'adventure', 'fun zone', 'arena', 'party',
        'tournament', 'league', 'gala', 'gathering', 'bunch',
        'fight', 'battle', 'conflict', 'encounter', 'clash',
        'combat', 'confrontation', 'challenge'
    ]
    
    def get_name(self) -> str:
        """Get a random room name."""
        return f'The {self.get_adjective()} {self.get_noun()}'
    
    def get_adjective(self) -> str:
        """Get a random adjective."""
        return random.choice(self.adjectives)
    
    def get_noun(self) -> str:
        """Get a random noun."""
        return random.choice(self.nouns)

