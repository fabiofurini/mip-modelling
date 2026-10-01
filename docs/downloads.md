# Downloads

All the material of the course, in PDF, updated at every publication of the
site. Text, figures and data are under the
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) licence; the Python
scripts under the
[MIT](https://github.com/fabiofurini/mip-modelling/blob/main/LICENSE-CODE)
licence.

## The three sets of notes

If you want the whole course to read offline, start from these three PDFs: they
are the core of the material. What comes after is supplementary.

<div class="grid cards" markdown>

-   :material-book-open-variant: **Modelling**

    ---

    The methodological part: what a MIP model is, logic and binary variables,
    the fourteen links between variables with their proofs, relaxations, duality
    and bounds, constructive heuristics, and the step to Python/Gurobi.

    [:octicons-download-24: notes-1-modelling.pdf](pdf/notes-1-modelling.pdf)

-   :material-numeric: **Numerical problems**

    ---

    The fifteen numerical models, from EX 1 to EX 15: explicit data, few
    variables, one step per technique. They are read to get the measure of
    things before the general problems.

    [:octicons-download-24: notes-2-numerical.pdf](pdf/notes-2-numerical.pdf)

-   :material-function-variant: **Problems with a symbolic model**

    ---

    The twenty-three problems of the three families and the mixed problems: statement, symbolic model,
    instance, heuristic, dual of the relaxation, optimum, additional questions
    and one variant worked out in full.

    [:octicons-download-24: notes-3-symbolic.pdf](pdf/notes-3-symbolic.pdf)

</div>

## The other documents

<div class="grid cards" markdown>

-   :material-school-outline: **How to work with the course**

    ---

    How the course is built, how every exercise is built and how the exam is
    built: the path, the grading criteria, the typical discussion questions, the
    most common mistakes, and the reproducibility of the numbers.

    [:octicons-download-24: course-organization.pdf](pdf/course-organization.pdf)

-   :material-help-circle-outline: **Problems to model**

    ---

    *For practice — solutions reserved for instructors.*

    Forty problems presented as they would arise in practice, with no model
    written in advance: twenty with explicit numerical data and twenty in
    symbolic form.

    [:octicons-download-24: exercises.pdf](pdf/exercises.pdf)

-   :material-presentation: **The slides**

    ---

    The course in forty-three slides: the method, the fourteen links, the
    sandwich of the bounds, the three families and the mixed problems, the exam format.

    [:octicons-download-24: mip-slides.pdf](pdf/mip-slides.pdf)

-   :material-language-python: **The code**

    ---

    One script per model, the generated notebooks, the data in CSV. Everything
    is regenerated with one command and every number is checked by an `assert`.

    [:octicons-mark-github-16: mip-modelling](https://github.com/fabiofurini/mip-modelling)

</div>

## Regenerating everything

```bash
python3 -m pip install gurobipy pandas matplotlib mkdocs-material
python3 python/run_all.py            # data, figures, models and notebooks
python3 python/check_numbers.py      # every number quoted in the texts
python3 -m mkdocs build --strict     # the site
```

The licence shipped with the `gurobipy` pip package (2000 variables, 2000
constraints) is enough for every instance of the course.

## The Gurobi licence

```bash
python3 -m pip install gurobipy
```

The pip package ships a **demo licence** (up to 2000 variables and 2000
constraints): enough for every instance of this course. On startup the line
`Restricted license - for non-production use only` appears: that is normal.

**Full academic licence, free of charge:**

1. register at <https://portal.gurobi.com> with an institutional email;
2. request a *Named-User Academic License*;
3. run the `grbgetkey XXXXXXXX-...` command shown by the portal (it needs the
   university network or the VPN);
4. the licence lands in `~/gurobi.lic` and from then on there is no size limit.
