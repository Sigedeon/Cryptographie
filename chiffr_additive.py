# Fonction de chiffrement
def chiffrement_additif(texte, k):
    msg_claire = ""
    for char in texte:
        position = ord(char) - ord('a')
        position_chiffree = (position + k) % 26
        char_chiffre = chr(position_chiffree + ord('a'))
        msg_claire += char_chiffre
    return msg_claire


# Fonction de déchiffrement
def dechiffrement_additif(texte, k):
    msg_claire = ""
    for char in texte:
        position = ord(char) - ord('a')
        position_chiffree = (position - k) % 26
        char_chiffre = chr(position_chiffree + ord('a'))
        msg_claire += char_chiffre
    return msg_claire


message_clair = "gedeon"
k = 5

# Chiffrement
message_chiffre = chiffrement_additif(message_clair, k)
print(f"Message clair chiffré : {message_chiffre}")

# Déchiffrement
message_dechiffre = dechiffrement_additif(message_chiffre, k)
print(f"Message en clair : {message_dechiffre}")
