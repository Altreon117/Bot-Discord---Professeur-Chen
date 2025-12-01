# Attention !
Le notation se fera en fonction de votre projet.
### Date du dernier commit : 1 décembre à 23h59 !

# Projet Bot discord B2 (sujet de rattrapage)

Pour ce sujet de rattrapage, vous allez devoir créer un bot discord. Vous allez créer plusieurs fonctionnalités obligatoires et vous devrez rajouter 3 fonctionnalités en plus obligatoires mais de votre choix.

---

## **1 - Historique des commandes (via liste chaînée, pile ou file)**

Vous devez créer un système d'historique des commandes envoyées par les utilisateurs au bot.

### **Fonctionnalités attendues :**

- **La dernière commande rentrée.**
- **Toutes les commandes rentrée par un utilisateur depuis sa première connexion.**
- **Vider l'historique.**

---

## **2 - Système de discussion via un arbre (arbre binaire ou non)**

Vous devez créer un système de questionnaire / conversation avec l’utilisateur.

### **Fonctionnalités attendues :**

- **Une commande help qui lance la conversation.**
- **Le bot pose une série de questions prédéfinies, selon votre arbre.**
- **L’utilisateur suit le chemin en répondant.**
- **À la fin, le bot donne une conclusion (un résultat du questionnaire).**

Les sujets que devra aborder le bot sont libre.

### **Commandes supplémentaires :**

- **reset :** recommence la discussion depuis la racine de l’arbre.
- **speak about X :** permet de vérifier si le sujet X existe dans votre arbre :

    Le bot doit parcourir votre arbre pour répondre “oui” ou “non”.

---

## **3 - Sauvegarde persistante des données**

Lorsque le bot s’arrête, les différentes structures et collections disparaissent.

Pour éviter cela, implémentez un système de sauvegarde lorsque le bot s'arrête :

Vous pouvez utiliser :

- **Un fichier texte**
- **Un fichier JSON**
- **Une base de données**
- **etc**

---

## **4 - Fonctionnalités supplémentaires (3 obligatoires)**

3 fonctionnalités obligatoires sont attendues en plus de celles demandées, on vous laisse juste la possibilité de les choisir pour que vous puissiez vous appropriez le projet.

---

## Annexes :

Attention, Les listes chainées, les files, les arbres doivent être créés à la main et ne doivent pas venir de modules et packages python.  
Chaque journée de retard aura un malus de -1 points sur la note finale.
