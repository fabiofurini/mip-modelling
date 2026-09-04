<h3 align="center">Teaching material by
<a href="https://sites.google.com/view/fabiofurini/home-page">Fabio Furini</a></h3>
<p align="center">
  Associate professor of Operations Research ·
  <a href="https://www.diag.uniroma1.it/">DIAG</a>, Sapienza University of Rome ·
  <a href="https://sites.google.com/view/fabiofurini/home-page">personal website</a>
</p>

# MIP Modelling

> **The author.** Since September 2021 Fabio Furini has been an associate
> professor at DIAG, Sapienza University of Rome. Ph.D. in Control Engineering
> and Operations Research at the University of Bologna (2011), research fellow
> there until 2012; postdoc at Université Paris-13 (2012–2013); from 2013 to 2019
> *Maître de Conférences* at Université Paris-Dauphine. *Habilitation à Diriger
> des Recherches* in France in 2017 and Italian National Scientific
> Qualification for Full Professor in Operations Research in 2019. In 2020 CNR
> researcher at IASI-CNR in Rome.
> Personal website: <https://sites.google.com/view/fabiofurini/home-page>

Mixed-integer linear models for Management Engineering — how to build a model
with binary and integer variables, how to *prove* it does what it should, how
to squeeze it with a dual bound and a heuristic, how to solve it with Gurobi.
The second course of the series that started with the
[Operations Research Lab](https://fabiofurini.github.io/operations-research-lab/).

**📖 Online lecture notes: [fabiofurini.github.io/mip-modelling](https://fabiofurini.github.io/mip-modelling/)**

**▶️ Runnable notebooks in Colab: [the list of chapters](https://fabiofurini.github.io/mip-modelling/notebooks/)** — they run in the browser, with nothing to install.

## Running the models

Every chapter has its own script in [`python/`](python/), with the data in [`data/`](data/):

```bash
python3 -m pip install gurobipy matplotlib pandas
python3 python/run_all.py     # all models: data, results, figures and notebooks
```

The `gurobipy` licence bundled with the pip package is enough for every instance of
the course; the free academic licence can be activated at
[portal.gurobi.com](https://portal.gurobi.com).

## Licence

- **Text, figures and data** (`docs/`, `data/`): [CC BY 4.0](LICENSE).
- **Python code** (`python/`): [MIT](LICENSE-CODE).

To cite the material see [`CITATION.cff`](CITATION.cff).

## Versione italiana

The whole course is also available in Italian:
**[fabiofurini.github.io/modellazione-mip](https://fabiofurini.github.io/modellazione-mip/)**
([repository](https://github.com/fabiofurini/modellazione-mip)).

---

Teaching material by **[Fabio Furini](https://sites.google.com/view/fabiofurini/home-page)** — [DIAG](https://www.diag.uniroma1.it/), Sapienza University of Rome.
