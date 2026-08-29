# Daggs sidmall

Byggd på mätningar av anthropic.com, openai.com och x.ai — inte på intryck.
Siffrorna står i [MEASURED.md](MEASURED.md).

## De fyra reglerna som avgör om det läser som en sida eller ett bildspel

### 1 · En grund per sida

Ingen av de tre växlar botten mellan sektioner. En sida har en botten, plus
möjligen en mörk avslutning.

Grunden varierar i stället **mellan sidor**. Anthropic kör elfenben på
startsidan och den ljusare på Company.

    Start            #F0EEE6   elfenben
    Strategy         #FAF9F5   den ljusa — här ligger den vita du efterlyste
    Implementation   #F0EEE6   elfenben
    Company          #FAF9F5
    FAQ · Careers    #FAF9F5

Mörkt förekommer en gång per sida, längst ned, som avslutning. Aldrig mitt i.

### 2 · Höjdkvot 4–6×

Anthropics Company-sida: kortast 258px, högst 1473px. **Kvot 5,7.**

Vår nuvarande sajt ligger nära 1,5 eftersom varje sektion har samma padding
och samma innehållsmängd. Det är den mekaniska orsaken till bildspelskänslan,
starkare än numren och starkare än railen.

### 3 · En bärande sektion, resten korta

Ordfördelningen på Anthropics Company-sida:

    25 · 184 · 168 · 544 · 82 · 12

En sektion bär hälften. Jämn fördelning är vad som får en sida att läsa som
dokumentation.

### 4 · Media sällsynt och samlad

Fyra bilder på hela Company-sidan, alla i ett block. Inte en figur per
sektion.

---

## Rutnätet

    12 spår · 1180px innehåll · 32px ränna
    huvuddelning     7 / 5      asymmetrisk, aldrig 6/6
    kortrad          3 eller 4 spår
    brödtextmått     max 620px
    sidospalt        340px

Tolv spår är ställningen. Synligt ska innehållet bilda två eller fyra
kolumner, aldrig fler.

---

## Sektionstyper — sju, inte en

Bildspelskänslan kommer av att varje avsnitt går genom samma behållare.
Sidan behöver flera former, och en sida använder fyra till fem av dem.

| Typ | Höjd | Vad den gör |
|---|---|---|
| **Öppning** | 420–560px | Rubrik och ingress. Ingen rail, ingen linje, ingen agenda. |
| **Bärare** | 1000–1500px | Sidans argument. Bär hälften av texten. |
| **Kort** | 550–700px | Tre eller fyra parallella saker. Får upprepas inom sig själv. |
| **Instrument** | 700–1000px | Ett diagram som gör något. Bryter textmåttet. |
| **Uttalande** | 260–420px | En mening. Nästan bara luft. |
| **Register** | 400–600px | Definitioner, frågor, en lista att slå i. |
| **Avslut** | 380–470px | Mörk. Nästa steg. |

Ingen sida använder alla sju, och ingen sida använder en enda typ två gånger
i rad.

---

## Vad som ryker ur nuvarande bygge

**Sidnumren.** De är deckets folio och hör inte hemma här.

**Rail per sektion.** Om railen överlever blir den *en* för hela sidan, och
visar vilket argument läsaren är i — något ett bildspel inte kan veta.

**Zonväxlingen.** Elfenben-varm-mörk nedför varje sida. Detta är det enskilt
viktigaste att ta bort.

**Den identiska sektionsformen.** Ögonbryn, rubrik, linje, innehåll — sex
gånger per sida.

**`.sec` som universalbehållare.** Varje typ ovan behöver bli sin egen sak.

---

## Vad som kommer tillbaka

Processen. Var arbetet börjar, hur det byggs, hur det ackumuleras. Det finns
på nuvarande sajt och i decket, och jag rensade bort det när jag rensade bort
påhittade siffror. Beskrivning av arbetssätt är inte påhitt.

---

## Vad de tre inte gör

Reglerna ovan är deras disciplin, och den är värd att ta. Men den gör oss i
bästa fall likvärdiga. Tre saker är öppna för Dagg och stängda för dem.

### Instrumentet som arbetar medan du läser

Alla tre illustrerar sin metod. Anthropics figurer är stillbilder av resultat.
OpenAI använder fotografi. x.ai kommer närmast med en panel som står still
medan texten passerar — men den visar en produkt, inte ett resonemang.

Ingen av dem visar en **mekanism i drift**. Dagg har en: samma post läses tre
gånger. Den kan byggas som ett instrument som byter tillstånd medan läsaren
passerar det — inte en animation som spelas upp, utan en figur vars tillstånd
är bunden till var i argumentet läsaren befinner sig. Bilden gör då samma sak
som texten säger, samtidigt.

Det är omöjligt i ett bildspel, och ingen av de tre gör det med ett argument.

### Artefakten som går att syna

De tre påstår. Läsaren får tro dem, för de har namn nog att tros.

Dagg har inte det, och kan därför inte påstå. Men sekretess förbjuder inte att
visa en artefakts **form** — bara dess innehåll. En maskad WorkGraph där
läsaren kan peka på en kant och se vad etiketten betyder är bevis som går att
undersöka, inte bevis man ombeds acceptera.

Ingen av de tre erbjuder något att undersöka. Deras diagram är att titta på.

### Varje påstående bär vad som skulle kullkasta det

Detta är den svåraste och den mest utmärkande. En rekommendation som anger
observationen som skulle få den att dras tillbaka är av en annan sort än en
som bara är välformulerad.

Ingen av de tre gör det någonstans på sina sajter. Det är inte ett förbiseende
— det är att de säljer förtroende och Dagg säljer omdöme, och omdöme syns
bara där någon kan ha fel.

---

## Måttstocken

En sajt är bäst i klassen när den gör något de andra måste kopiera för att
komma ikapp, och när kopian kostar dem något.

Disciplinen ovan kostar ingenting att kopiera. De tre greppen gör det: ett
instrument kräver en mekanism värd att visa, en synbar artefakt kräver att man
tål att bli synad, och en falsifierbar utsaga kräver att man har fel ibland
och står för det.

Det är den enda sortens försprång som håller.
