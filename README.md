Indroduction
------------

No one needs introductions, everyones hates them, so we leave it out

Usage
-----

Plot the formula, that you want to calculate the Gaussian Errorformula for, in the first Input Field.

![](/pictues/pic_1.png)

### Beware

The Format \*needs\* to be in the pythonian equation format (i dont know if that exists, but you get what i mean, when lookin at those examples):

Examples:

|     |     |     |
| --- | --- | --- |
| Formula | Latex | Python Equation Format |
| \\(\\frac{1}{2}mv^2\\) | \\frac{1}{2}mv^2 | (1)/(2)\*m\*v\*\*2 |
| \\(\\frac{1}{g^2}\\) | \\frac{1}{g^2} | (1)/(g\*\*2) |
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

![](api/images/WkHI8NnxxtQx/grafik.png)

### Note

There are a lot of Variables like Capital I or Capital Q, which DO NOT WORK.  
You need to use dummy variables (like smal q and then change it afterwards).

|     |     |
| --- | --- |
| Doesnt | WORk |
| Capital Q | Q   |
| Capital I | I   |
|     |     |
|     |     |
|     |     |
|     |     |

This list ist constantly updated, help me expand it!

On the other hand Phi would be recognized and afterwards be generated to \\Phi (except of in the Delta Phi term, but i am sure you will change the \\Phi into \\varphi )

Check your formating
--------------------

You can check if you ploted the equation the right way, by pressing:

![](api/images/RlwHyi85XCxX/grafik.png)

![](api/images/hrvYEi8Kez1C/grafik.png)

Then your equation will be generated into Latex, so you can check for mistakes. (They happen often, so doublecheck)!

Calculate the Errorformula
--------------------------

By pressing this Button, the error Formula will be generated.

![](api/images/cGE49QI7MKxn/grafik.png)

And you will be promted with the output json, where you can extract the Latex Code of the Formula, the pythonian equation and the Latex Code Rendered, so you can check for errors again.

![](api/images/V7jJTQbjtysL/grafik.png)
