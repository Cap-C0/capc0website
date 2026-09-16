Recently I was reading through the ISO specification of QR codes when I came across a chart that simultaneously confused me and piqued my interest.

![generator_polys](./generator_poly_sheet.png)

The introduction paragraph clearly states where the polynomials are derived from; $(x-2^0)(x-2^1)...(x-2^{n-1})$, and yet it just gives you all the expansions of that product immediately. The subtext here is clearly *"This is difficult, so don't bother"*. However, what the qr-code specification doesn't understand is both how unemployed I am, and my propensity to bother a lot.

This silly little chart -- that you are clearly supposed to just take at face value, manually enter into your code, and then move on with -- sent me down a week long rabbit hole exploring finite field arithmetic, Gaussian polynomials, q-analogs, and my own sanity.

I hope that I can introduce the concepts that lead to this chart being the way it is in an exploratory and thorough way. Many of the resources I found online are quite guilty of just "pulling formulas out of hats" and expecting you to accept them. That's fine for busy people and professionals who already know this stuff but my goal in this blog post is to convince you that this chart *really* is the expansions of the product of first degree polynomials $(x-2^0)(x-2^1)...(x-2^{n-1})$ by showing you how we can go about deriving each of the coefficients -- hopefully without too many formulas from hats.

When I went about researching this topic, I was often more confused why things *aren't* the way they are than why they *are* that way. I hope to make this topic more understandable by highlighting these mistakes.

Understanding these polynomials is just one part of understanding Reed-Solomon error correcting which in itself is just one part of QR codes themselves, but those are out of the scope of this post. I hope to make a post on them at a later date!

For now our motivation is to take the chart "in a vacuum" and ask **"Why is this chart the way it is?"**

This post will assume some understanding of group theory and discrete math for its explanations. (Especially proof by induction, my beloved)

## Exploring for ourselves.

To start we can try to do the simpler cases by hand to see if they make sense to us.

In the case that n=2, we have:
$$(x-2^0)(x-2^1)$$

With FOILing we can get:
$$x^2 + 2^1x + 2^0x + 2^1 * 2^0 = x^2 + (2^1 + 2^0)x + 2^1$$

It would appear we can simplify this to: $x^2 + 3x + 2$, but this is the most dangerous kind of mistake you can make: the one that yields the correct answer for the wrong reason! I will get in to why it is *correct* when I explain Galois fields, but for why is it wrong: Lets assume that the table is correct and compare our result with the table's:

For $n=2$ the corresponding generator polynomial is $x^2 + \\alpha^{25}x + \\alpha$. That would mean that $\\alpha=2$ and $\\alpha^{25}=(2^0+2^1)$. If we were to just assume that $2$ represents a real number, then by letting $\\alpha^{25}=3$ we get $2^{25} = 3$. This is clearly not the case in $\\mathbb{R}$. But then where is it the case that $2^1 + 2^0 = 2^{25}$?

The nature of the polynomials we are working with is explained in the table introduction; "In the table, $\alpha$ is the primitive element $2$ under $GF(2^{8})$". That confirms that $\alpha = 2$. If you are like me though, this explanation raises far more questions than it answers. Lets first look at what $GF$ means.

## Part 1: Galois Field.

### A nice motivating example that ended up less nice than the author hoped:

Without getting too much in to the nitty-gritty of error correcting, I will propose a (somewhat arbitrary) scenario of two communicating parties; a sender and a receiver. The sender chooses some data ($D=(d_1,d_2,...,d_n)\in S^n$)(arbitrary elements from an agreed upon set($S$)). We will assume the sender will perform some agreed upon arithmetic(+,-,*,/) operations($f: (S^n)\to(S^p)$) on the elements of the data, which yields the message to send($M=(m_1,m_2,...,m_p)\in S^p$), note that $m_x$ can be defined by any arithmetic combination of elements $d_t$ ie. $m\_2 = d\_1 * d\_2 + d\_1 / s$ for some $s \in S$. We will also enforce associativity and commutativity for these operations since they are nice to have :) (and this section is already getting too dense).

The receiver can get back the original data by doing the inverse of the operations($f^{-1}$) on the message. We will also restrict the parameters of $f$ to be in the agreed upon set. What we ultimately want is a set that is *closed* under operations defined, and therefore closed under $f$. We can also see that solving for $D$ is the same as solving a system of linear equations!

In order that the data should be recoverable, there are some restrictions on $f$, an exhaustive proof of these restrictions is beyond the scope of this post. Something to do with linear algebra probably.

From this scenario I will propose 2 heuristics: 
  1. "It is desirable that when a sender does an arithmetic operation on the data, the receiver can perfectly 'undo' that operation."
  2. "It is desirable that the size of the message sent is constrained in some way (ie. not infinitely large)."


With these heuristics in mind, we can begin to understand why we can't use real numbers, or any infinite set for the "number" we send.
If we were to try to use real numbers, there may be cases where the sender sends an irrational number, in which case its size can't be bounded. Even if we restrict our numbers to rational numbers, there may be cases where the agreed upon operation yields infinitely large rational numbers. We can't use floating point numbers either because they are not associative or distributive and plain integers are out the door because you can't define division precisely. (if the sender had $d=5$ and $f(x)=x/2$, then $m=2$, but the receiver doesn't know if that means $d=4$ or $d=5$!)

So from this impromptu poll of common sets of numbers mathemeticians and programmers use, we come up short for our desired traits. This makes us wonder: **Wouldn't it be nice if there was some kind of numbers that had these traits?!**

To help us find what these kind of numbers look like, we must first precisely define what our arithmetic is.

So lets start with the loosest definition of a set closed under this arithmetic that meets our desired traits and see where it gets us. Because the goal of our communication is for the receiver to "undo" the operations of the sender, we can start simply with:
  1. Addition is the *inverse* of subtraction. ie. $a + b - b = a$. Equivalently, for all $b$ there is some $-b$ s.t. $a + b + (-b) = a$
  2. Multiplication is the *inverse* of division. ie. $a * b / b = a$.Equivalently, for all $b$ there is some $b^{-1}$ s.t. $a * b *b^{-1} = a$. There is an important caveat to this, more on that in a bit.
  3. Multiplication is different than addition (otherwise why bother defining both?)

Because the operations close the set, and are commutative and transitive we can suppose at least 2 elements that must be in the set, they are:
  - Some additive identity $O$ where $\forall a \in S | O=a-a$, consequently $a+O=a$.
  - Some multiplicative identity $I$ where $\forall a \in S | I=a/a$, consequently $a*I=a$.
  - Letters $O$ and $I$ are *very* suggestively chosen. (ponder what these identities are when we are talking about real numbers!)

The ultimate goal is that the receiver can invert $f$, and this actually leads to further restrictions of how we are allowed to define our operations! We are allowing the equation that defines $m\in M$ to take *any* form, and so consequently there must be an "inverting" rule for *all* forms of equations! 

For example, lets assume that $d_1$ has been solved for and the only equation we have that contains $d_2$ is $m\_1 = d\_2 + d_1 * d_2$. With just the rules defined above, it is impossible to solve this equation!

As it turns out, distribution is the rule that lets us do this!
$$
a * (b + c) = (a * b) + (a * c)
$$

Up until this point, multiplication and addition were effectively identical, but in defining this rule, we have made a(n arbitrary) decision on what differentiates them.

We can further explore what this implies for the identity elements as well.
- $O = O + O \to a * O = a * (O + O) \to a * O = a * O + a * O \to a * 0 - a * O = a * 0 + a * O - a * O \to O = a * O$
- But since $a$ could be any number, clearly $a/O$ can't be well defined!  We must disallow division by $O$!
- Suppose there is some $a,b\neq O$ s.t. $a\*b=O$. Then $(a\*I) + (a\*b) = (a\*I) + O = a \neq O$ but $(a\*I) + (a\*b) = a \* (b+I) = a$ which implies $(b+I) = I$ so $b=O$ which contradicts the supposition $a,b \neq O$ and shows us that for all tuples $(a,b) | a\*b=O\to a=O \lor b=O$. In other words, if the product of two numbers is zero, one of those numbers must be zero. 

Looking at our example, this allows us to rewrite $d_2 + d_1 * d_2$ as $d_2 *(d_1 + 1)$ so $d_2 = m_1/(d_1 + I)$ (A further restriction would be that $d_1 + 1$ can't be $O$ in this operation, as stated, I won't be going in to the thorough description.)

In fact, what these rules define is precisely a field! Look at these definitions and think about what sets of numbers you use in your life are fields. Rational numbers? Real numbers? Complex Numbers? Integers? Integers mod n?

We can clearly see all these definitions are just part of how we define these operations on the numbers we use in everyday life, but I want to ask you to take a moment to reflect on how these definitions **differ** from how they are defined on the numbers we use in everyday life. Most importantly, we have divorced multiplication from *necessarily* being defined by repeated addition ie $4 * 2 = 2 +2+2+2$. In fact, because we are just defining these operations on abstract "sets" there is no guarantee that elements of a set will correspond to some real number for which you could "apply addition that many times (plus a fraction)". 

> At this point I want to make a quick comment on pedagogy; I think any introduction to topics in abstract algebra has to tread the line between expressing precise abstract definitions and helping the reader bridge their understanding with examples they are already familiar with. If you lean too much on the arcane abstract definitions, the reader will feel lost and unable to follow. If you are too up front with examples the reader is already familiar with, you risk the reader bringing the "baggage" of their intuition about those examples that may not actually apply to the structure (In the case of a field, Real Numbers are a field, but we *can't* bring intuition related to square roots or transcendentals into a general understanding of fields). 

### Ok, we have defined x
