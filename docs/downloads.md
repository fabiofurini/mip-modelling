# Downloads

All the material of the course, in PDF, updated at every publication of the
site. Text, figures and data are under the
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) licence; the Python
scripts under the
[MIT](https://github.com/fabiofurini/mip-modelling/blob/main/LICENSE-CODE)
licence.

<div class="grid cards" markdown>

-   :material-book-open-variant: **The notes**

    ---

    The whole course: the six modelling chapters, the fifteen numerical models,
    the four families of problems with heuristics, duals and additional
    questions, and the organisation of the course.

    [:octicons-download-24: mip-notes.pdf](pdf/mip-notes.pdf)

-   :material-file-document-edit: **The collection of statements**

    ---

    The same problems, in the same order, with the texts only: to practise
    before reading the solution. Forty-two statements.

    [:octicons-download-24: statements-collection.pdf](pdf/statements-collection.pdf)

-   :material-presentation: **The slides**

    ---

    The course in forty-three slides: the method, the fourteen links, the
    sandwich of the bounds, the four families, the exam format.

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
