HEAD = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600&amp;family=Newsreader:opsz,wght@6..72,300..600&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap">
<link rel="stylesheet" href="style.css">{extra}
</head>
<body data-ground="{ground}">
<div class="progress" aria-hidden="true"></div>
<header class="nav"><div class="nav__in">
  <a href="index.html" aria-label="Dagg"><img class="nav__mark" src="../../assets/dagg-logotype-dark.png" alt="Dagg"></a>
  <button class="nav__toggle" aria-expanded="false" aria-controls="navlinks">Menu</button>
  <nav class="nav__links" id="navlinks">
    <a href="strategy.html"{s}>Strategy</a>
    <a href="implementation.html"{i}>Implementation</a>
    <a href="workgraph.html"{w}>WorkGraph</a>
    <a href="company.html"{c}>Company</a>
    <a class="cta" href="index.html#assessment">Book an assessment</a>
  </nav>
</div></header>
<main>
'''
FOOT = '''</main>
<footer class="foot"><div class="foot__in">
  <img class="foot__mark" src="../../assets/dagg-logotype-dark.png" alt="Dagg">
  <a href="strategy.html">Strategy</a>
  <a href="implementation.html">Implementation</a>
  <a href="workgraph.html">WorkGraph</a>
  <a href="company.html">Company</a>
  <a href="faq.html">FAQ</a>
  <a href="careers.html">Careers</a>
  <a href="mailto:hello@dagg.ai">hello@dagg.ai</a>
  <span class="foot__end">&copy; 2026 Dagg</span>
</div></footer>
<script src="site.js"></script>
</body>
</html>
'''
CUR = ' aria-current="page"'
def build(name, title, desc, ground, cur, body, extra=''):
    h = HEAD.format(title=title, desc=desc, ground=ground, extra=extra,
                    s=CUR if cur=='s' else '', i=CUR if cur=='i' else '',
                    w=CUR if cur=='w' else '', c=CUR if cur=='c' else '')
    open(name+'.html','w').write(h + body + FOOT)
    print(name+'.html')
