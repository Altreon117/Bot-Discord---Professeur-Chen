from datetime import datetime  # Gestion des dates et heures (usage: CommandNode timestamp)
import DatabaseFunction as db  # Fonctions de base de données personnalisées (usage: toutes les opérations d'historique)


# ================== COMMAND HISTORY (Linked List) ==================

class CommandNode:
    """Node de la liste chaînée représentant une commande"""
    def __init__(self, command_name: str, user_id: int, timestamp: datetime):
        self.command_name = command_name
        self.user_id = user_id
        self.timestamp = timestamp
        self.next = None  # Pointeur vers le prochain nœud


class CommandHistory:
    """Liste chaînée pour stocker l'historique des commandes d'un utilisateur"""
    def __init__(self):
        self.head = None  # Premier nœud (commande la plus récente)
        self.tail = None  # Dernier nœud (commande la plus ancienne)
        self.size = 0
    
    def add_command(self, command_name: str, user_id: int):
        """Ajoute une commande au début de la liste (plus récente)"""
        new_node = CommandNode(command_name, user_id, datetime.now())
        
        if self.head is None:
            # Liste vide
            self.head = new_node
            self.tail = new_node
        else:
            # Ajouter au début
            new_node.next = self.head
            self.head = new_node
        
        self.size += 1
    
    def get_last_command(self) -> CommandNode:
        """Retourne la dernière commande (la plus récente)"""
        return self.head
    
    def get_all_commands(self) -> list:
        """Retourne toutes les commandes sous forme de liste"""
        commands = []
        current = self.head
        while current:
            commands.append({
                "command": current.command_name,
                "timestamp": current.timestamp,
                "user_id": current.user_id
            })
            current = current.next
        return commands
    
    def clear_history(self):
        """Vide complètement l'historique"""
        self.head = None
        self.tail = None
        self.size = 0
    
    def get_size(self) -> int:
        """Retourne le nombre de commandes dans l'historique"""
        return self.size


class HistoryManager:
    """Gestionnaire d'historique basé sur la base de données"""
    def add_command(self, user_id: int, command_name: str, pseudo: str = None):
        db.add_command_history(user_id, command_name, pseudo)
    
    def clear_user_history(self, user_id: int):
        db.clear_command_history(user_id)
    
    def get_last_command(self, user_id: int) -> dict:
        return db.get_last_command_history(user_id)
    
    def get_all_user_commands(self, user_id: int) -> list:
        return db.get_all_command_history(user_id)
