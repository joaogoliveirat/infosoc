from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# Carrega o roteiro
with open('roteiro.json', encoding='utf-8') as f:
    roteiro = json.load(f)

# Estado inicial do jogador
estado_jogador = {
    "etica": 0,
    "direitos_digitais": 0,
    "seguranca_publica": 0,
    "confianca_comunitaria": 0,
    "decisoes": []
}
def avaliar_impacto():
    sp = estado_jogador["seguranca_publica"]
    dd = estado_jogador["direitos_digitais"]
    cc = estado_jogador["confianca_comunitaria"]

    resultado = []

    if sp >= 1:
        resultado.append("Você priorizou a segurança pública, neutralizando ameaças com firmeza.")
    elif sp < 0:
        resultado.append("A segurança pública ficou comprometida durante sua missão.")

    if dd >= 1:
        resultado.append("Você defendeu fortemente os direitos digitais.")
    elif dd < 0:
        resultado.append("Os direitos digitais foram comprometidos.")

    if cc >= 1:
        resultado.append("A confiança das comunidades foi conquistada com respeito e diálogo.")
    elif cc < 0:
        resultado.append("As comunidades se distanciaram após suas decisões controversas.")

    if not resultado:
        resultado.append("Você manteve um equilíbrio tênue entre todos os pilares.")

    return " ".join(resultado)


@app.route('/')
def index():
    return redirect(url_for('cena', cena_id="inicio"))

@app.route('/cena/<cena_id>', methods=['GET', 'POST'])
def cena(cena_id):
    cena = roteiro[cena_id]
    
    if request.method == 'POST':
        escolha = request.form['escolha']
        dados = cena["escolhas"][escolha]

        # Atualiza ética
        estado_jogador["etica"] += dados.get("etica", 0)

        # Atualiza impacto (se existir)
        impacto = dados.get("impacto", {})
        for key, val in impacto.items():
            estado_jogador[key] += val

        # Registra a escolha feita
        estado_jogador["decisoes"].append({
            "cena": cena_id,
            "escolha": escolha,
            "texto": dados["texto"]
        })

        # Vai para a próxima cena
        proxima = dados["proximo"]
        return redirect(url_for('cena', cena_id=proxima))
    
    impacto = {
        "direitos_digitais": estado_jogador["direitos_digitais"],
        "seguranca_publica": estado_jogador["seguranca_publica"],
        "confianca_comunitaria": estado_jogador["confianca_comunitaria"]
    }

    mensagem_final = None
    if cena_id.startswith("final"):
        mensagem_final = avaliar_impacto()

    return render_template(
        "escolha.html",
        cena=cena,
        etica=estado_jogador["etica"],
        impacto=impacto,
        mensagem_final=mensagem_final,
        decisoes=estado_jogador["decisoes"] if mensagem_final else None
    )



    

if __name__ == '__main__':
    app.run(debug=True)
