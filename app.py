import os
from flask import Flask, render_template, request, redirect, url_for
import json

app = Flask(__name__)

# Carrega o roteiro do jogo (Correto)
with open('roteiro.json', encoding='utf-8') as f:
    roteiro = json.load(f)

# Estado inicial do jogador (Correto)
estado_jogador = {
    "personalidade_inicial": None,
    "pontos_pragmatico": 0,
    "pontos_idealista": 0,
    "pontos_equilibrado": 0,
    "direitos_digitais": 0,
    "seguranca_publica": 0,
    "confianca_comunitaria": 0,
    "caminho_secreto": 0,
    "decisoes": []
}

def reiniciar_jogo():
    """Função para resetar o estado do jogador para o padrão."""
    global estado_jogador
    estado_jogador = {
        "personalidade_inicial": None,
        "pontos_pragmatico": 0,
        "pontos_idealista": 0,
        "pontos_equilibrado": 0,
        "direitos_digitais": 0,
        "seguranca_publica": 0,
        "confianca_comunitaria": 0,
        "caminho_secreto": 0,
        "decisoes": []
    }

def avaliar_impacto():
    """Gera uma análise final com base nos pontos de impacto."""
    sp = estado_jogador["seguranca_publica"]
    dd = estado_jogador["direitos_digitais"]
    cc = estado_jogador["confianca_comunitaria"]
    resultado = []

    if sp >= 3:
        resultado.append("Você priorizou a segurança pública de forma agressiva, neutralizando ameaças com firmeza.")
    elif sp > 0:
        resultado.append("Suas ações fortaleceram a segurança pública.")
    elif sp < 0:
        resultado.append("A segurança pública ficou comprometida durante sua missão.")

    if dd >= 2:
        resultado.append("Você foi um defensor ferrenho dos direitos digitais e da privacidade.")
    elif dd > 0:
        resultado.append("Você demonstrou preocupação e protegeu os direitos digitais.")
    elif dd < 0:
        resultado.append("Os direitos digitais foram sacrificados em nome de outros objetivos.")

    if cc >= 2:
        resultado.append("A confiança das comunidades foi conquistada com respeito e diálogo exemplar.")
    elif cc > 0:
        resultado.append("Você construiu uma boa relação com as comunidades afetadas.")
    elif cc < 0:
        resultado.append("As comunidades se distanciaram após suas decisões controversas.")

    if not resultado:
        resultado.append("Você manteve um equilíbrio tênue entre todos os pilares.")

    return " ".join(resultado)

@app.route('/')
def index():
    reiniciar_jogo()
    return redirect(url_for('cena', cena_id="prologo"))

@app.route('/cena/<cena_id>', methods=['GET', 'POST'])
def cena(cena_id):
    if cena_id not in roteiro:
        return "Cena não encontrada!", 404

    cena_atual = roteiro[cena_id]

    if cena_atual.get("tipo") == "pdf":
        if request.method == 'POST':
            escolha = request.form['escolha']
            dados_escolha = cena_atual["escolhas"][escolha]
            proxima_cena = dados_escolha["proximo"]
            return redirect(url_for('cena', cena_id=proxima_cena))
        
        return render_template("cena_pdf.html", cena=cena_atual, cena_id=cena_id)
    
    elif cena_atual.get("tipo") == "txt":
            if request.method == 'POST':
                escolha = request.form['escolha']
                dados_escolha = cena_atual["escolhas"][escolha]
                proxima_cena = dados_escolha["proximo"]
                return redirect(url_for('cena', cena_id=proxima_cena))
            
            # Lógica para ler o arquivo de texto
            conteudo_do_arquivo = "Erro: Arquivo não encontrado."
            try:
                # Constrói o caminho completo para o arquivo
                caminho_arquivo = os.path.join(app.static_folder, 'textfiles', cena_atual['arquivo_txt'])
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    conteudo_do_arquivo = f.read()
            except Exception as e:
                print(f"Erro ao ler o arquivo: {e}")

            return render_template("cena_txt.html", cena=cena_atual, cena_id=cena_id, conteudo_arquivo=conteudo_do_arquivo)
    # Lógica do minigame de hacking
    if cena_atual.get("tipo") == "minigame":
        palavras = cena_atual["palavras"]
        senha_correta = cena_atual["senha_correta"]
        

        if request.method == 'POST':
            palpite = request.form["palpite"].upper()
            

            if palpite == senha_correta:
                resp = redirect(url_for('cena', cena_id=cena_atual["escolhas"]["sucesso"]["proximo"]))
                
                return resp
            else:
                # Calcula feedback: quantas letras na posição correta
                feedback = sum([1 for a, b in zip(palpite, senha_correta) if a == b])
            
                

                return render_template(
                    "minigame_hack.html", 
                    cena=cena_atual, 
                    palavras=palavras, 
                    feedback=feedback, 
                    ultimo_palpite=palpite
                )

        return render_template(
            "minigame_hack.html", 
            cena=cena_atual, 
            palavras=palavras, 
        )

    if "condicional" in cena_atual:
        cond = cena_atual["condicional"]
        if estado_jogador.get(cond["campo"]) == cond["valor"]:
            return redirect(url_for('cena', cena_id=cond["proximo_sucesso"]))
        else:
            return redirect(url_for('cena', cena_id=cond["proximo_falha"]))

    if request.method == 'POST':
        escolha = request.form['escolha']
        
        if escolha not in cena_atual["escolhas"]:
            return "Escolha inválida!", 400

        dados_escolha = cena_atual["escolhas"][escolha]

        if "set_estado" in dados_escolha:
            if cena_id == 'cena_3_2_dilema' and escolha == 'a' and estado_jogador.get('caminho_secreto') == 1:
                 estado_jogador['caminho_secreto'] = 2
            elif "caminho_secreto" in dados_escolha["set_estado"]:
                 estado_jogador['caminho_secreto'] = dados_escolha["set_estado"]["caminho_secreto"]

            for key, val in dados_escolha["set_estado"].items():
                if key != 'caminho_secreto':
                    estado_jogador[key] = val

        if "pontuacao" in dados_escolha:
            for perfil, valor in dados_escolha["pontuacao"].items():
                estado_jogador[f"pontos_{perfil}"] += valor

        if "impacto" in dados_escolha:
            for key, val in dados_escolha["impacto"].items():
                estado_jogador[key] += val

        estado_jogador["decisoes"].append({
            "cena": cena_id,
            "escolha": escolha,
            "texto": dados_escolha["texto"]
        })

        proxima_cena = dados_escolha["proximo"]
        return redirect(url_for('cena', cena_id=proxima_cena))
    
    impacto_atual = {
        "direitos_digitais": estado_jogador["direitos_digitais"],
        "seguranca_publica": estado_jogador["seguranca_publica"],
        "confianca_comunitaria": estado_jogador["confianca_comunitaria"]
    }

    mensagem_final = False 
    resumo_impacto = None

    # Uma cena final é aquela que não tem um dicionário de "escolhas".
    if not cena_atual.get("escolhas"): 
        mensagem_final = True  # Ativa o modo "tela final" no template.
        resumo_impacto = avaliar_impacto()

    return render_template(
        "escolha.html",
        cena=cena_atual,
        cena_id=cena_id,
        estado=estado_jogador,
        impacto=impacto_atual,
        mensagem_final=mensagem_final, # Agora envia True ou False
        resumo_impacto=resumo_impacto,
        decisoes=estado_jogador["decisoes"] if mensagem_final else None
    )

if __name__ == '__main__':
    app.run(debug=True)