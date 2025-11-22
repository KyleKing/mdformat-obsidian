Custom Titles
.
> [!tip] Callouts can have custom titles
> Like this one.
.
<div>
<div data-callout-metadata="" data-callout-fold="" data-callout="tip" class="callout">
<div class="callout-title">
<div class="callout-title-inner">Callouts can have custom titles</div>
</div>
<div class="callout-content">
<p>Like this one.</p>
</div>
</div>
</div>
.

Foldable Callouts
.
> [!faq]- Are callouts foldable?
> Yes! In a foldable callout, the contents are hidden when the callout is collapsed.
.
<div>
<div data-callout-metadata="" data-callout-fold="-" data-callout="faq" class="callout is-collapsible is-collapsed">
<div class="callout-title">
<div class="callout-title-inner">Are callouts foldable?</div>
<div class="callout-fold is-collapsed"></div>
</div>
<div class="callout-content" style="display: none;">
<p>Yes! In a foldable callout, the contents are hidden when the callout is collapsed.</p>
</div>
</div>
</div>
.

Nested Callouts
.
> [!question] Can callouts be nested?
> > [!todo] Yes!, they can.
> > > [!example]  You can even use multiple layers of nesting.
.
<div>
<div data-callout-metadata="" data-callout-fold="" data-callout="question" class="callout">
<div class="callout-title">
<div class="callout-title-inner">Can callouts be nested?</div>
</div>
<div class="callout-content">
<div>
<div data-callout-metadata="" data-callout-fold="" data-callout="todo" class="callout">
<div class="callout-title">
<div class="callout-title-inner">Yes!, they can.</div>
</div>
<div class="callout-content">
<div>
<div data-callout-metadata="" data-callout-fold="" data-callout="example" class="callout">
<div class="callout-title">
<div class="callout-title-inner">You can even use multiple layers of nesting.</div>
</div>
<div class="callout-content"></div>
</div>
</div>
</div>
</div>
</div>
</div>
</div>
</div>
.

Callout with Code Block
.
> [!tip] Code in Callouts
> You can include code:
>
> ```python
> def hello():
>     print("world")
> ```
.
<div>
<div data-callout-metadata="" data-callout-fold="" data-callout="tip" class="callout">
<div class="callout-title">
<div class="callout-title-inner">Code in Callouts</div>
</div>
<div class="callout-content">
<p>You can include code:</p>
<pre><code class="language-python">def hello():
    print(&quot;world&quot;)
</code></pre>
</div>
</div>
</div>
.

Callout with Lists
.
> [!note] Lists work too
> - Item 1
> - Item 2
>   - Nested item
> - Item 3
.
<div>
<div data-callout-metadata="" data-callout-fold="" data-callout="note" class="callout">
<div class="callout-title">
<div class="callout-title-inner">Lists work too</div>
</div>
<div class="callout-content">
<ul>
<li>Item 1</li>
<li>Item 2
<ul>
<li>Nested item</li>
</ul>
</li>
<li>Item 3</li>
</ul>
</div>
</div>
</div>
.

Empty Callout
.
> [!info]
.
<div>
<div data-callout-metadata="" data-callout-fold="" data-callout="info" class="callout">
<div class="callout-title">
<div class="callout-title-inner"></div>
</div>
<div class="callout-content"></div>
</div>
</div>
.
