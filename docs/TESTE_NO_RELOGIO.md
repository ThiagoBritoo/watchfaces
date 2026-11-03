# Roteiro de teste no relógio (10 minutos por watchface)

Depois de instalar (ver `INSTALAR.md`), confira cada item e anote **OK / diferente / quebrado**. Se algo estiver
diferente do preview, tire uma foto ou print e me mande junto com o nome da watchface e do item.

## Para todas as watchfaces
- [ ] Aparece na lista de mostradores e abre sem travar.
- [ ] **Personalizar** abre; dá para trocar tema/cor/estilo e o mostrador muda na hora.
- [ ] As complicações mostram dados (passos, bateria...) e dá para trocar o provedor.
- [ ] Os ponteiros/horas estão certos (compare com a hora do relógio) e os segundos andam.
- [ ] **Modo ambiente**: baixe o braço ou cubra a tela. Deve ficar quase tudo preto, só contornos finos. Sem segundos.
- [ ] Textos legíveis ao sol e no escuro; nada cortado nas bordas redondas.
- [ ] Bateria: deixe uma hora com a watchface e veja quanto caiu (compare com o mostrador que você usa hoje).

## Específico de cada uma
**Cronos**
- [ ] Agulhas dos dois mostradores giram conforme o valor (bateria, passos) e marcam 0 a 100.
- [ ] Engrenagens do centro giram e parecem engrenadas.
- [ ] Os 5 temas e os 2 estilos de ponteiro; segundos "mecânico" dá o salto (ajustar `Tick` se ficar estranho).

**Aviador**
- [ ] Data na janela do 6h certa; complicação abaixo do triângulo legível.
- [ ] Os 3 mostradores; cor de destaque no ponteiro de segundos e na complicação.

**Terminal CRT** (maior risco: fonte pixel tingida)
- [ ] Texto e barra na cor escolhida (verde/âmbar/ciano/branco). Se ficar branco, é o `tintColor` na BitmapFont.
- [ ] Mascote alterna de pose a cada segundo; barra de bateria acompanha o %.
- [ ] Dia da semana em letras escuras sobre a caixa clara.

**Sol e Lua**
- [ ] Marcadores laranja (mês, dia, dia da semana) caem no mês, dia e dia da semana de hoje.
- [ ] Sol anda no arco durante o dia (6h a 18h); à noite aparece a lua com a fase certa. Se a fase estiver trocada, me diga a fase real.

**Linha**
- [ ] Hora fina grande centralizada (a fonte do relógio pode ser mais larga que a prévia).
- [ ] Estilo analógico/digital; anéis de passos e bateria; cápsulas com texto legível.

**Pura**
- [ ] Traços e ponteiros nítidos; segundos com bolinha de cor; data aparece e some na opção "Mostrar data".

**Painel**
- [ ] Clima aparece (precisa permitir clima no relógio); ícone, temperatura, máx/mín.
- [ ] Três mostradores circulares com arco de progresso; anel dos segundos na borda.

## Como me enviar o resultado
Uma lista simples por watchface já ajuda: `Cronos: tudo OK, engrenagens ok, tick estranho`. Prints do relógio
(captura de tela pelo app do relógio ou foto) com o item que ficou diferente.


## Faces abstratas (novas)
**Régua**: [ ] os dois anéis giram e a cápsula mostra o minuto e o segundo certos; [ ] hora grande legível.
**Fragmento**: [ ] a hora e o minuto atuais ficam sob a linha inclinada; [ ] o recorte não mostra bordas feias.
**Deslizante**: [ ] os números deslizam, o do meio é o maior e está certo; [ ] bordas esmaecem sem "pular".
**Matriz**: [ ] fonte de pontos nítida; [ ] 4 segmentos de anel crescem (passos, dia, segundos, bateria); [ ] cor de destaque.
**Montanha**: [ ] texto curvo no alto legível; [ ] régua de minutos no pé gira e o minuto certo fica sob a cápsula; [ ] textos laterais na vertical.
**Maré**: [ ] nível de água coerente com a hora; [ ] ondas suaves; [ ] o gasto de bateria não é alto (se for, avise).
**Anéis**: [ ] anéis crescem na hora/minuto/segundo/bateria; [ ] pontos luminosos nas pontas.

## Mais 10 faces
**Pêndulo**: [ ] balança de um lado a outro a cada segundo; [ ] hora no peso fica de pé. **Eclipse**: [ ] Lua cruza o Sol conforme o minuto.
**Céu do Dia**: [ ] cor do céu combina com a hora real; [ ] sol de dia, lua à noite. **Gigante**: [ ] números cabem sem cortar feio.
**Binário**: [ ] pontos acesos batem com o decimal embaixo. **Vinil**: [ ] disco gira, hora legível no rótulo.
**Bússola**: [ ] ponta colorida e cauda branca dos ponteiros alinhadas. **Constelação**: [ ] estrelas da hora/minuto nos lugares certos.
**Barras**: [ ] 4 barras com valores certos; [ ] rótulos legíveis. **Odômetro**: [ ] dígitos rolam nos últimos 10 s e o vai-um funciona (ex.: 19:59 -> 20:00).

## Mais 9 faces (lote 3)
**Radar**: [ ] varredura gira; [ ] alvos de hora e minuto nos lugares certos. **Mondrian**: [ ] linhas e blocos se movem sem artefatos; [ ] hora legível nas 3 paletas.
**Ampulheta**: [ ] areia de cima esvazia e a de baixo enche conforme o minuto. **24 Horas**: [ ] ponteiro de 24 h aponta a hora certa (12 no topo, 0 embaixo).
**Aurora**: [ ] bolhas se movem devagar; hora legível. **Moiré**: [ ] padrão muda com os minutos. **Engrenagens**: [ ] dentes encaixam e giram juntos.
**Osciloscópio**: [ ] onda desliza, leituras corretas. **Topo**: [ ] curvas de nível visíveis; pinos de hora/minuto certos.

## Mais 10 faces (lote 4)
**Calendário**: [ ] grade do mês certa (primeiro dia, nº de dias, hoje circulado). **Lua**: [ ] fase bate com a lua real (se trocada, me diga). **LCD**: [ ] dígitos de 7 segmentos e dia da semana destacado.
**Flip**: [ ] números cabem nos cartões. **Ondas**: [ ] ondulações suaves (bateria?). **Duo**: [ ] números não passam da metade de cada bloco.
**Sol de Pedra**: [ ] sombra aponta a linha da hora atual (6h a 18h). **Espectro**: [ ] cor muda ao longo do dia. **Pontilhado**: [ ] cometa de segundos e ponto do minuto.
**Palavras**: [ ] frase correta ("SÃO DEZ HORAS E VINTE E CINCO"; "É UMA HORA"; "EM PONTO").

## Mais 5 faces (lote 5)
**Neon**: [ ] tubos legíveis e com brilho; [ ] cor do neon trocável. **Pulsar**: [ ] linhas nítidas e hora legível no topo. **Velocímetro**: [ ] agulha marca o minuto (0 a 60).
**Terminal**: [ ] cursor pisca; barras de bateria e passos corretas. **Newton**: [ ] bolas das pontas alternam a cada segundo e nenhuma sai da tela.

## Mais 6 faces (lote 6)
**Synthwave**: [ ] sol, horizonte e grade nítidos; hora legível. **Energia**: [ ] anel vermelho abaixo de 20%; [ ] "CARREGANDO" só quando carrega.
**Sistema Solar**: [ ] planetas nas órbitas certas; lua gira em volta do planeta dos minutos. **Poligonal**: [ ] texto legível sobre o fundo.
**Bauhaus**: [ ] círculo anda com a hora, quadrado gira com os minutos, triângulo com os segundos. **Vidro**: [ ] cartões translúcidos e legíveis.

**Tourbillon**: [ ] gaiola gira e balancim oscila a cada segundo; [ ] ponteiros passam por cima da janela; [ ] 3 mostradores.

**Céu Pixel**: [ ] blocos nítidos e hora legível. **Sombra Longa**: [ ] sombra comprida alinhada (16 cópias de texto). **Mandala**: [ ] pétala da hora acesa certa e pontos orbitando. **Ponto**: [ ] ponto dos minutos e traço da hora.

**Horizonte**: [ ] ponto e linha acompanham os minutos. **Colmeia**: [ ] favo da hora certo e favos de minutos acendendo de 10 em 10. **Prisma**: [ ] anel gira e hora legível. **Chomp**: [ ] pontos somem conforme os minutos e a boca abre e fecha.

**Nível**: [ ] bolha se move ao inclinar (me diga se o sentido estiver invertido). **Parallax**: [ ] camadas deslizam com a inclinação sem sobrar borda preta. **Rádio**: [ ] agulha acompanha os minutos. **Placar**: [ ] números cabem nos blocos.
