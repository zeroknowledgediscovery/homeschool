from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from datetime import date
import random
import math

# -----------------------
# Settings
# -----------------------
pdf_path = "Math_Practice_Test_Age8.pdf"
ARITH_COL_CHARS = 8               # fixed digit columns for long lines
SEED = None                       # set to an int (e.g., 123) for reproducible randomness

# Difficulty knobs
ADD_TERMS = 4
ADD_MIN_DIGITS = 4
ADD_MAX_DIGITS = 5

SUB_MIN_DIGITS = 3
SUB_MAX_DIGITS = 4

MULT_TOP_DIGITS = 4               # e.g., 2378
MULT_BOTTOM_DIGITS = 2            # e.g., 99

DIV_PROBLEMS = 2
SIMPLIFY_FRACTIONS = 2
FRACTION_SUMS = 2
PRIME_FACTS = 3


PAGE2_MIXED_TO_IMPROPER = 5
PAGE2_IMPROPER_TO_MIXED = 5
PAGE2_HCF_LCM_PAIRS = 4

# -----------------------
# RNG
# -----------------------
rng = random.Random(SEED)
def rand_pm():
    return rng.choice(["+", "-"])

def rand_ndigit(n_digits: int) -> int:
    lo = 10 ** (n_digits - 1)
    hi = (10 ** n_digits) - 1
    return rng.randint(lo, hi)

def gcd(a, b):
    return math.gcd(a, b)

def make_addition():
    nums = []
    for _ in range(ADD_TERMS):
        d = rng.randint(ADD_MIN_DIGITS, ADD_MAX_DIGITS)
        nums.append(rand_ndigit(d))
    return nums

def make_subtraction():
    # ensure non-negative result and nice borrowing sometimes
    a = rand_ndigit(rng.randint(SUB_MIN_DIGITS, SUB_MAX_DIGITS))
    b = rand_ndigit(rng.randint(SUB_MIN_DIGITS, min(SUB_MAX_DIGITS, len(str(a)))))
    if b > a:
        a, b = b, a
    return a, b

def make_multiplication():
    top = rand_ndigit(MULT_TOP_DIGITS)
    bottom = rand_ndigit(MULT_BOTTOM_DIGITS)
    return top, bottom

def make_division_exact():
    # pick divisor and quotient, then multiply to get dividend (so it divides evenly)
    divisor = rng.choice([6, 8, 9, 10, 12, 15, 16, 18, 20, 24])
    quotient = rng.randint(12, 98)
    dividend = divisor * quotient
    return dividend, divisor

def make_simplify_fraction():
    # produce a reducible fraction, not already simplest
    base = rng.randint(2, 12)
    a = rng.randint(2, 25) * base
    b = rng.randint(2, 25) * base
    return a, b

def make_fraction_sum():
    # keep denominators modest
    d1 = rng.choice([3, 4, 5, 6, 8, 10, 12])
    d2 = rng.choice([3, 4, 5, 6, 8, 10, 12])
    n1 = rng.randint(1, d1 - 1)
    n2 = rng.randint(1, d2 - 1)
    return n1, d1, n2, d2

def make_fraction_sum():
    # keep denominators modest
    d1 = rng.choice([3, 4, 5, 6, 8, 10, 12])
    d2 = rng.choice([3, 4, 5, 6, 8, 10, 12])
    n1 = rng.randint(1, d1 - 1)
    n2 = rng.randint(1, d2 - 1)
    op = rand_pm()
    return n1, d1, op, n2, d2




def make_prime_factor_targets(k=PRIME_FACTS):
    # pick numbers with non-trivial factorization but not too huge
    pool = [120, 144, 180, 210, 240, 252, 270, 280, 300, 315, 336, 360, 420, 504]
    rng.shuffle(pool)
    return pool[:k]


# Add these helpers (do NOT remove anything else)
def make_mixed_number():
    d = rng.choice([2, 3, 4, 5, 6, 8, 10, 12])
    whole = rng.randint(1, 9)
    num = rng.randint(1, d - 1)
    return whole, num, d

def mixed_to_improper(whole, num, den):
    return whole * den + num, den

def make_improper_fraction():
    # make an improper fraction (not whole)
    den = rng.choice([2, 3, 4, 5, 6, 8, 10, 12])
    whole = rng.randint(1, 9)
    num = rng.randint(1, den - 1)
    n, d = mixed_to_improper(whole, num, den)
    return n, d

def lcm(a, b):
    return abs(a*b) // math.gcd(a, b)

def make_hcf_lcm_pair():
    # Keep values <= 3 digits, with shared factors (so not always trivial)
    base = rng.choice([2, 3, 4, 5, 6, 7, 8, 9, 10, 12])
    a = base * rng.randint(2, 20)
    b = base * rng.randint(2, 20)
    a = min(a, 999)
    b = min(b, 999)
    if a < 10: a += base
    if b < 10: b += base
    return a, b




# -----------------------
# Generate randomized problems
# -----------------------
add_nums = make_addition()
sub_a, sub_b = make_subtraction()

m1_top, m1_bottom = make_multiplication()
m2_top, m2_bottom = make_multiplication()

divs = [make_division_exact() for _ in range(DIV_PROBLEMS)]
simp_fracs = [make_simplify_fraction() for _ in range(SIMPLIFY_FRACTIONS)]
frac_sums = [make_fraction_sum() for _ in range(FRACTION_SUMS)]

prime_targets = make_prime_factor_targets(PRIME_FACTS)

# Mixed decimal & fraction example (randomized but still friendly)
# keep it simple: 1 decimal + 1 small decimal + 1/2 or 1/4 or 3/4
dec1 = rng.choice([0.1, 0.2, 0.3, 0.4, 0.5])
dec2 = rng.choice([0.001, 0.002, 0.005, 0.01, 0.02])
frac_choice = rng.choice([(1, 2), (1, 4), (3, 4)])
op1 = rand_pm()
op2 = rand_pm()
mixed_expr = f"{dec1:g}  {op1}  {dec2:g}  {op2}  {frac_choice[0]}/{frac_choice[1]}"

# -----------------------
# PDF setup
# -----------------------
W, H = letter
margin = 0.6 * inch

c = canvas.Canvas(pdf_path, pagesize=letter)
c.setTitle("Math Test")

today_str = date.today().strftime("%B %d, %Y")

# Header
c.setFont("Helvetica-Bold", 18)
c.drawString(margin, H - margin, f"Math Test — {today_str}")
c.setFont("Helvetica", 11)
c.drawString(margin, H - margin - 20, "Name: ________________________________")
c.drawString(W - margin - 160, H - margin - 20, "Score: ______ / ______")
c.setStrokeColor(colors.black)
c.setLineWidth(1)

y = H - margin - 55

def draw_section(title, y):
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, title)
    c.setLineWidth(0.8)
    c.line(margin, y - 3, W - margin, y - 3)
    return y - 20

def draw_vertical_arithmetic(
    x, y_top, numbers, op=None, result_blanks=True,
    cell_h=18, mono_font="Courier", font_size=16
):
    max_len = max(max(len(str(n)) for n in numbers), ARITH_COL_CHARS)

    c.setFont(mono_font, font_size)
    y = y_top

    for i, n in enumerate(numbers):
        s = str(n).rjust(max_len)
        if op and i == len(numbers) - 1:
            c.drawString(x - 18, y, op)
        c.drawString(x, y, s)
        y -= cell_h

    underline_w = c.stringWidth("0" * max_len, mono_font, font_size)
    c.setLineWidth(1.2)
    c.line(x - 2, y + 8, x + underline_w + 2, y + 8)

    y -= 10
    if result_blanks:
        #c.drawString(x, y, "_" * max_len)
        y -= cell_h

    return y

def draw_long_multiplication_template(
    x, y_top, top, bottom,
    bottom_prefix="x", mono_font="Courier", font_size=16, cell_h=18
):
    max_len = max(len(str(top)), len(str(bottom)), ARITH_COL_CHARS)

    c.setFont(mono_font, font_size)
    c.drawString(x, y_top, str(top).rjust(max_len))

    c.drawString(x - 18, y_top - cell_h, bottom_prefix)
    c.drawString(x, y_top - cell_h, str(bottom).rjust(max_len))

    underline_w = c.stringWidth("0" * max_len, mono_font, font_size)
    c.setLineWidth(1.2)
    c.line(x - 2, y_top - cell_h - 6, x + underline_w + 2, y_top - cell_h - 6)

    # Partial product lines
    y = y_top - cell_h - 24
   # c.drawString(x, y, "_" * max_len)
    y -= cell_h
    #c.drawString(x, y, "_" * (max_len + 1))
    y -= cell_h

    # Final underline + answer
    c.setLineWidth(1.2)
    c.line(x - 2, y + 10, x + underline_w + 2, y + 10)
    y -= 10
    #c.drawString(x, y, "_" * (max_len + 2))

    return y - cell_h

# -------------------------
# A) Addition & Subtraction
# -------------------------
y = draw_section("A) Addition & Subtraction", y)
c.setFont("Helvetica", 11)
c.drawString(margin, y, "1) Add:")
y -= 14

y_after = draw_vertical_arithmetic(
    margin + 55, y,
    add_nums,
    op="+",
    result_blanks=True
)
y = y_after + 30

c.setFont("Helvetica", 11)
c.drawString(W/2, y + 60, "2) Subtract:")
draw_vertical_arithmetic(
    W/2 + 75, y + 44,
    [sub_a, sub_b],
    op="-",
    result_blanks=True
)
y -= 50

# -------------------------
# B) Long Multiplication
# -------------------------
y = draw_section("B) Long Multiplication", y)
c.setFont("Helvetica", 11)
c.drawString(margin, y, "3) Multiply:")
c.drawString(W/2, y, "4) Multiply:")
y -= 16

draw_long_multiplication_template(margin + 70, y - 4, m1_top, m1_bottom)
draw_long_multiplication_template(W/2 + 70, y - 4, m2_top, m2_bottom)
y -= 150

# -------------------------
# C) Division & Fractions
# -------------------------
y = draw_section("C) Division & Fractions", y)
c.setFont("Helvetica", 11)

qnum = 5
for dividend, divisor in divs:
    c.drawString(margin, y, f"{qnum}) {dividend} ÷ {divisor} = __________")
    y -= 16
    qnum += 1

for a, b in simp_fracs:
    c.drawString(margin, y, f"{qnum}) {a}/{b} (simplify) = __________")
    y -= 16
    qnum += 1

y -= 4
c.setFont("Helvetica", 11)
c.drawString(margin, y, f"{qnum}) Add the fractions (show your work):")
y -= 16
qnum += 1

c.setFont("Helvetica", 12)
labels = ["a", "b", "c", "d"]
for i, (n1, d1, op, n2, d2) in enumerate(frac_sums):
    c.drawString(margin + 15, y, f"{labels[i]})  {n1}/{d1}  {op}  {n2}/{d2}  =  ____________________________")
    y -= 18

y -= 2
c.setFont("Helvetica", 11)
c.drawString(margin, y, f"{qnum}) Mixed decimal & fraction:")
y -= 16
c.setFont("Helvetica", 12)
c.drawString(margin + 15, y, f"{mixed_expr}  =  ____________________________")
y -= 35

# -------------------------
# D) Prime Factorization
# -------------------------
y = draw_section("D) Prime Factorization", y)
c.setFont("Helvetica", 11)
c.drawString(margin, y, f"{qnum+1}) Write each number as a product of prime factors:")
y -= 16
c.setFont("Helvetica", 12)

for i, n in enumerate(prime_targets):
    c.drawString(margin + 15, y, f"{labels[i]}) {n} = __________________________________________")
    y -= 18

# Footer
c.setFont("Helvetica-Oblique", 9)
c.drawString(margin, 0.30 * inch, "Tip: Work neatly and double-check your answers.")



# After you finish your existing Page 1 content but BEFORE:
# c.showPage(); c.save()
# insert this entire Page 2 block.

# -------------------------
# PAGE 2
# -------------------------
c.showPage()  # start a new page

# Header for page 2
today_str = date.today().strftime("%B %d, %Y")
c.setFont("Helvetica-Bold", 18)
c.drawString(margin, H - margin, f"Math Test — {today_str}  (Page 2)")
c.setFont("Helvetica", 11)
c.drawString(margin, H - margin - 20, "Name: ________________________________")
c.drawString(W - margin - 160, H - margin - 20, "Score: ______ / ______")
c.setStrokeColor(colors.black)
c.setLineWidth(1)

y = H - margin - 55

def draw_page2_section(title, y):
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y, title)
    c.setLineWidth(0.8)
    c.line(margin, y - 3, W - margin, y - 3)
    return y - 20

# A2) Mixed <-> Improper
y = draw_page2_section("A) Mixed Fractions and Improper Fractions", y)
c.setFont("Helvetica", 11)

# 1) Mixed -> Improper (5)
c.drawString(margin, y, "1) Convert mixed numbers to improper fractions:")
y -= 16
c.setFont("Helvetica", 12)
for i in range(PAGE2_MIXED_TO_IMPROPER):
    w, n, d = make_mixed_number()
    c.drawString(margin + 15, y, f"{chr(ord('a')+i)})  {w} {n}/{d}  =  __________ / __________")
    y -= 18

y -= 6
c.setFont("Helvetica", 11)

# 2) Improper -> Mixed (5)
c.drawString(margin, y, "2) Convert improper fractions to mixed numbers:")
y -= 16
c.setFont("Helvetica", 12)
for i in range(PAGE2_IMPROPER_TO_MIXED):
    n, d = make_improper_fraction()
    c.drawString(margin + 15, y, f"{chr(ord('a')+i)})  {n}/{d}  =  ______  ______/______")
    y -= 18

y -= 10

# B2) HCF/LCM
y = draw_page2_section("B) HCF (GCD) and LCM", y)
c.setFont("Helvetica", 11)
c.drawString(margin, y, "3) For each pair, find BOTH HCF and LCM:")
y -= 16
c.setFont("Helvetica", 12)

pairs = [make_hcf_lcm_pair() for _ in range(PAGE2_HCF_LCM_PAIRS)]
for i, (a, b) in enumerate(pairs):
    c.drawString(margin + 15, y, f"{chr(ord('a')+i)})  {a} and {b}    HCF: __________    LCM: __________")
    y -= 18

y -= 10

# C2) Area problems with drawings
y = draw_page2_section("C) Area", y)
c.setFont("Helvetica", 11)
c.drawString(margin, y, "4) Find the area of each shape (show your work):")





c.showPage()
c.save()
