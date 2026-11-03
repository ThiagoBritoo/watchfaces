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
