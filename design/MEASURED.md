# Uppmätt, i webbläsare, 2026-08-29

Sektionshöjder och grunder lästa direkt ur `getBoundingClientRect` och
`getComputedStyle` på de faktiska sidorna. Inga uppskattningar.

## Grunder per sida

| Sida | Antal grunder | Värden |
|---|---|---|
| anthropic.com/company | 1 + fot | `#FAF9F5` · fot `#141413` |
| anthropic.com (start) | 1 + fot | `#F0EEE6` · fot `#141413` |
| x.ai/company | **1** | `#0A0A0A` rakt igenom |
| openai.com/about | **1** | `#000000` rakt igenom |

**Ingen av dem växlar grund mellan sektioner.** En sida har en botten.
Anthropic använder olika bottnar på *olika sidor* — elfenben på startsidan,
den ljusare på Company — men aldrig två på samma sida.

Det är den enskilt viktigaste iakttagelsen, och den förklarar varför vår
sajt läser som ett bildspel: ett bildspel byter grund. En sida gör det inte.

## Höjdvariation

| Sida | Kortast | Högst | Median | Kvot |
|---|---|---|---|---|
| anthropic.com/company | 258px | 1473px | 569px | **5,7×** |
| anthropic.com (start) | 68px | 928px | 610px | 13,6× |
| openai.com/about | 368px | 846px | 643px | 2,3× |

Anthropics Company-sida, sektion för sektion:

```
 258px  w=25    Making AI systems you can rely on
 569px  w=184   Our Purpose
1004px  w=168   The Team              ← 4 bilder, enda mediablocket
1473px  w=544   What we value         ← bär halva sidans text
 424px  w=82    Governance
 472px  w=12    (mörk avslutning)
```

Ordfördelningen är lika ojämn som höjden: 25 · 184 · 168 · **544** · 82 · 12.
En sektion bär hälften av sidan. Resten är korta.

## Vad detta betyder för oss

1. **En grund per sida.** Inte per sektion. Vill vi ha vitt är det en
   *sidas* botten, inte en zon i en sida.
2. **Variationen ligger i höjd och komposition**, inte i färg. Målet är en
   kvot kring 4–6× mellan kortaste och högsta sektion.
3. **Ojämn textfördelning är mönstret.** En bärande sektion, resten korta.
   Jämn fördelning är vad som får en sida att läsa som dokumentation.
4. **Media är sällsynt och samlad.** Anthropic har fyra bilder på hela
   Company-sidan, alla i ett block.

## Rutnätet (anthropic.com, uppmätt)

```
12 spår · 1278px innehållsbredd · 31,7px ränna · 77px per spår
huvuddelning:   span 7 / span 5     ← asymmetrisk, aldrig 6/6
kortrad:        4 spår à 214px
brödtextmått:   ~608px
sidospalt:      ~341px
```

Synligt bildar innehållet två eller fyra kolumner. Tolv spår är ställningen,
inte kompositionen.

## Fler sidor

| Sida | Grunder | Kortast | Högst | Kvot |
|---|---|---|---|---|
| anthropic.com/news | 1 (`#FAF9F5`) | 709px | 1873px | 2,6× |
| openai.com (start) | 1 (`#000000`) | 368px | 5651px | 15,4× |

OpenAI upprepar en kortrad tre gånger på exakt 614px — men bara som en
*serie*. Sidan i övrigt varierar 368 → 5651. Upprepning är tillåten inom ett
parallellt block, aldrig som sidans genomgående form.

## Palantir — närmast Daggs affär av alla fyra

| Sida | Grunder | Kortast | Högst | Kvot |
|---|---|---|---|---|
| palantir.com/platforms/foundry | **1** (`#FFFFFF`) | 120px | 1909px | stor |
| palantir.com/impact | **1** (`#FFFFFF`) | 740px | 2076px | 2,8× |

Rent vitt, hela vägen, 9757px utan en enda grundväxling. Regeln håller nu
hos fyra av fyra.

Foundry-sidans höjder: 120 · 141 · 175 · 611 · 613 · 632 · 636 · 791 · 1145
· 1520 · 1909. **Korta skiljesektioner på 120–175px** — något vi saknar helt.

### Tre grepp värda att ta

**Ontology är en egen flik.** WorkGraph-motsvarigheten får plats i navet, inte
inuti en metodsida. Det motsäger mitt tidigare beslut att degradera den.

**"Impact Studies", inte "Case Studies".** Ett namn som överlever att vara få,
och som pekar på utfallet i stället för på kunden.

**"In the Words of Our Customers".** Kunden talar i stället för att bolaget
beskriver. En sektion på 1225px med 649 ord och 34 mediaelement.

Deras Impact-sidas rubrik: *Enterprise Transformation – from Insight to
Impact.* Nära er positionering.

### Ett grepp att inte ta

Registret. *"Activate your data and analytics in a dynamic system for
closed-loop operations."* Det är precis den teknikbolagsröst som ska undvikas.
Palantirs struktur är värd att låna. Deras språk är det inte.

### Hero

740px, **21 ord.** Ingen bild ovanför vecket.
