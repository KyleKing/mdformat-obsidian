Support dollarmath (Fixes: https://github.com/KyleKing/mdformat-obsidian/issues/2)
.
$$
\begin{vmatrix}a & b\\
c & d
\end{vmatrix}=ad-bc
$$
.
$$
\begin{vmatrix}a & b\\
c & d
\end{vmatrix}=ad-bc
$$
.

Math Role and Directives (https://myst-parser.readthedocs.io/en/latest/syntax/math.html#math-role-and-directive)
.
Since Pythagoras, we know that {math}`a^2 + b^2 = c^2`.

```{math}
:label: mymath
(a + b)^2 = a^2 + 2ab + b^2

(a + b)^2  &=  (a + b)(a + b) \\
           &=  a^2 + 2ab + b^2
```

The equation {eq}`mymath` is a quadratic equation.
.
Since Pythagoras, we know that {math}`a^2 + b^2 = c^2`.

```{math}
:label: mymath
(a + b)^2 = a^2 + 2ab + b^2

(a + b)^2  &=  (a + b)(a + b) \\
           &=  a^2 + 2ab + b^2
```

The equation {eq}`mymath` is a quadratic equation.
.

Dollar Math (https://myst-parser.readthedocs.io/en/latest/syntax/math.html#dollar-delimited-math)
.
$$
(a + b)^2  &=  (a + b)(a + b) \\
           &=  a^2 + 2ab + b^2
$$ (mymath2)

The equation {eq}`mymath2` is also a quadratic equation.
.
$$
(a + b)^2  &=  (a + b)(a + b) \\
           &=  a^2 + 2ab + b^2
$$ (mymath2)

The equation {eq}`mymath2` is also a quadratic equation.
.

(Unsupported) LaTeX Math (https://myst-parser.readthedocs.io/en/latest/syntax/math.html#direct-latex-math)
.
\begin{gather*}
a_1=b_1+c_1\\
a_2=b_2+c_2-d_2+e_2
\end{gather*}

\begin{align}
a_{11}& =b_{11}&
  a_{12}& =b_{12}\\
a_{21}& =b_{21}&
  a_{22}& =b_{22}+c_{22}
\end{align}
.
\\begin{gather\*}
a_1=b_1+c_1\\
a_2=b_2+c_2-d_2+e_2
\\end{gather\*}

\\begin{align}
a\_{11}& =b\_{11}&
a\_{12}& =b\_{12}\\
a\_{21}& =b\_{21}&
a\_{22}& =b\_{22}+c\_{22}
\\end{align}
.
