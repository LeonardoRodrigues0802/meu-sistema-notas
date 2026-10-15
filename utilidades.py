def calcular_media(nota1, nota2, nota3):
    return (float(nota1) + float(nota2) + float(nota3)) / 3


def verificar_situacao(media):
    media = float(media)
    if media >= 7:
        return "Aprovado"
    if media >= 4:
        return "Recuperação"
    return "Reprovado"
