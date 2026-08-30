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

Plot the formula, that you want to calculate the Gaussian Errorformula for, in the first Input Field.

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

Decide for Variables
--------------------

For the Erroformula, the Program needs to know which Variables have Errors.  
Input the Variables (!!exactly like in the formula!!) into the second Field and seperate them via Kommas.  
It is fine, that the formula has more Variables that what you put in here.

![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_2.png?raw=true)

### Note

Older versions of this generator couldn't handle variables named `I` or `Q` (they collided with
SymPy's own reserved names). That's fixed now — any variable name works, including `I` and `Q`.

On the other hand Phi would be recognized and afterwards be generated to \\Phi (except of in the Delta Phi term, but i am sure you will change the \\Phi into \\varphi )

Check your formating
--------------------

You can check if you ploted the equation the right way, by pressing:

![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_3.png?raw=true)


![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_4.png?raw=true)

Then your equation will be generated into Latex, so you can check for mistakes. (They happen often, so doublecheck)!

Calculate the Errorformula
--------------------------

By pressing this Button, the error Formula will be generated.

![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_5.png?raw=true)

And you will be promted with the output json, where you can extract the Latex Code of the Formula, the pythonian equation and the Latex Code Rendered, so you can check for errors again. The error Formula will be generated without the square root, because for longer equations it is easier to tex. The calculated value below will be with the square root.

![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_6.png?raw=true)

Calculate
---------

If you want to calculate the Equation with the respective Error, you can now procced to the “Berechnen Section”

![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_7.png?raw=true)

In this field you will need to enter \*every\* Variable that is used in the Formula, since now the Calculater wants to calculate the eqautions numericaly. Seperate the Variables with kommas, like before.   
Everytime you click, or change/add a Variable in this field, new html input fields for the corresponding Variable will be generated.

![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_8.png?raw=true)

Plot in your Values for the Variables and their Error. If a Variable has no error, just type 0 (zero). (Every field must be filled out).

After that click on ‘Rechne,Computer!’ and recieve your Values:
Note that here the computation is done with the square root, so you dont have to take the square root of this value!

![alt text](https://github.com/captain-joni/errorformulagenerator/blob/main/pictures/pic_9.png?raw=true)

### Note

Remeber to use a Point ‘ . ’ instead of commas, ‘ , ’

Dont: 0,005, but instead: 0.005 (otherwise the calculation will fail)

Expressions like 5\*10\*\*-3 are not permitted yet. Just write it out:

Dont: 5\*10\*\*-3 but instead: 0.005

Some of the Calculation features do not work yet (will they ever?).   
For example, it is not yet possible to calculate a sin cos,tan etc.
*Update*: calculation now goes through SymPy/NumPy properly (instead of a hand-rolled string
substitution), so `sin`, `cos`, `tan`, `asin`, `acos`, `atan`, `sinh`, `cosh`, `tanh`, `exp`, `log`,
`sqrt`, `Abs` and `pi` all work out of the box — not just the handful that used to be special-cased.

You'll also get a live LaTeX preview as you type the formula, a "Kopieren" button next to the
Python-format equation (handy for pasting into WolframAlpha), and the result is now shown as
`Wert ± Fehler`, rounded to a sensible number of digits, instead of a raw JSON blob. Your last
formula/variables/values are remembered in the browser (localStorage) so a refresh doesn't lose them.

Undefined
---------

If you encounter this, either you made a mistake, or you found another symbol that doens't work.   
Text me, open an issue, or play with the generator until it works. 

### Bugs

Known Bugs:  
 

*   ~~sin, cos, tan not working~~ fixed
*   ~~Q and I not working as characters~~ fixed

Open an issue on GitHub if you find another one.


