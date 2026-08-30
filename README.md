Indroduction
------------

No one needs introductions, everyones hates them, so we leave it out

Running it
----------

Locally, without Docker:

```
pip install -r requirements.txt
uvicorn app.main:app --reload --port 3000
```

Then open `http://localhost:3000`.

With Docker, standalone (no reverse proxy):

```
docker compose -f docker-compose.local.yml up --build
```

`docker-compose.yml` is the production config (Traefik-routed, external network) used for the
`error.joni.science` deployment — you don't need it for local use.

Usage
-----

Type the formula you want the Gaussian error formula for into the first field. A live LaTeX preview
appears as you type.

![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_1.png?raw=true)

### Beware
DON'T write' E = (1)/(2)*m*v**2 ', but leave the "E = " out. So just write: (1)/(2)*m*v**2 into the Field!
The Format \*needs\* to be in the pythonian equation format (i dont know if that exists, but you get what i mean, when lookin at those examples):

Examples:

|     |     |     |
| --- | --- | --- |
| Formula | Latex | Python Equation Format |
| $(\\frac{1}{2}mv^2)$ | \\frac{1}{2}mv^2 | (1)/(2)\*m\*v\*\*2 |
| $(\\frac{1}{g^2})$ | \\frac{1}{g^2} | (1)/(g\*\*2) |
| denk dir selbst | ein | weites Beispiel aus |

#### Note:

|     |     |
| --- | --- |
| Addition | `a + b` |

|     |     |
| --- | --- |
| Subtraktion | `a - b` |

|     |     |
| --- | --- |
| Multiplikation | `a * b` |

|     |     |
| --- | --- |
| Division | `a / b` |

|     |     |
| --- | --- |
| Potenz | `a**n` |

Supported functions/constants: `sin cos tan asin acos atan atan2 sinh cosh tanh asinh acosh atanh exp
log sqrt Abs pi`.

Variables — no typing required
-------------------------------

The variable panel is generated automatically from whatever you typed above — you never type a
variable name yourself. Each detected variable gets a row with a **"fehlerbehaftet" checkbox**: tick it
if that quantity carries a measurement uncertainty. Fill in the value (and, if ticked, the error Δ)
right there — this is also where the numbers for the final calculation come from, so you only enter
each value once.

![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_2.png?raw=true)
![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_3.png?raw=true)

### Known constants

If a detected variable name is a mathematical or physical constant with an *exactly* known value
(`e`, `c`, `h`, `hbar`, `kB`, `NA`, `eps0`, `mu0`, `g`) it shows up as a locked constant chip with its
value filled in automatically, instead of an input row. If you actually wanted that letter as your own
variable (e.g. `c` for a heat capacity), click "als Variable verwenden" to turn it back into a normal
input row. `pi` is always the mathematical constant and never shows up as a variable at all.

### Note

Any variable name works now, including SymPy's historically-reserved single letters like `I` and `Q` —
older versions of this generator couldn't handle those.

On the other hand Phi would be recognized and afterwards be generated to \\Phi (except of in the Delta Phi term, but i am sure you will change the \\Phi into \\varphi )

Calculate the Errorformula
--------------------------

Press "Fehlerformel berechnen" to symbolically build the error formula from whichever variables you
ticked as fehlerbehaftet.

![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_4.png?raw=true)

You get the LaTeX-rendered formula, a "LaTeX kopieren" button that copies the raw `$$...$$`-wrapped LaTeX
source (paste straight into Overleaf, a Markdown doc, Jupyter, …), and a read-only, copyable Python-format
equation (handy for pasting into WolframAlpha or your own script) — the same LaTeX-copy button is also
available under the formula preview in step 1. The error formula is generated without the outer square
root, because that's easier to read/typeset for long formulas — the square root is applied when you
calculate a numeric result instead.

Error terms are shown as `\Delta m` (i.e. "Δm", read as "the uncertainty of m") rather than a subscript --
that's on purpose, since `\Delta_{m}` reads ambiguously once squared.

Calculate
---------

Everything needed is already filled in from the variable panel above — just press "Rechne, Computer!".

![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_5.png?raw=true)

The result is shown as `Wert ± Fehler`, rounded to a sensible number of digits — the square root has
already been applied here, you don't need to take it yourself.

### Note

Remeber to use a Point ‘ . ’ instead of commas, ‘ , ’

Dont: 0,005, but instead: 0.005 (otherwise the calculation will fail)

Expressions like 5\*10\*\*-3 are not permitted yet. Just write it out:

Dont: 5\*10\*\*-3 but instead: 0.005

*Update*: calculation now goes through SymPy/NumPy properly (instead of a hand-rolled string
substitution), so `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `exp`, `log`,
`sqrt`, `Abs` and `pi` all work out of the box — not just the handful that used to be special-cased.

Your last formula and every variable's value/error are remembered in the browser (localStorage) so a
refresh doesn't lose them.

Undefined
---------

If you encounter this, either you made a mistake, or you found another symbol that doens't work.
Text me, open an issue, or play with the generator until it works.

### Bugs

Known Bugs:

*   ~~sin, cos, tan not working~~ fixed
*   ~~Q and I not working as characters~~ fixed

Open an issue on GitHub if you find another one.
