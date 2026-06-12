# LaTeX Production & Compilation Protocol (latex_skill.md)

## Objective and Role
The LaTeX Agent structures a draft Hebrew academic paper as **document-body content only**. The pipeline's converter supplies the complete LuaLaTeX preamble (document class, BiDi engine, fonts, bibliography backend) and wraps your content automatically. Your job is the body between — never a whole document.

## Core Mandates

### 1. Emit BODY CONTENT ONLY — never a full document
- **NO preamble, NO document wrapper.** Do **not** emit `\documentclass`, `\usepackage`, `\begin{document}`, `\end{document}`, `\title`, `\author`, `\date`, `\maketitle`, `\tableofcontents` setup, `filecontents`, `\hypersetup`, `fancyhdr`, font, or language-setup commands. The pipeline already provides all of these. Emitting them produces a broken document with a duplicate preamble.
- **No direction wrappers.** Do **not** wrap text in `\RTL{...}`, `\LTR{...}`, `\setmainlanguage`, `\setcode`, or `\settextfont`. The preamble sets Hebrew as the main language with `babel` `bidi=basic`, so Hebrew is right-to-left automatically and embedded English flows left-to-right on its own. For an explicitly LTR English block use `\begin{otherlanguage}{english}...\end{otherlanguage}`.
- **Sectioning:** Use `\section{...}`, `\subsection{...}`, `\subsubsection{...}` (article class). Do **not** use `\chapter` — it does not exist here.

### 2. Math Notation Layout
- **Academic Precision:** Format all math operators, equations, and expressions using standard TeX mathematical environments (`equation`, `align`, `gather`).
- **The Drake Equation:** Render the legendary Drake Equation with full elegance using nested math blocks, with each variable explicitly explained using standard LaTeX tables:
  $$N = R_* \cdot f_p \cdot n_e \cdot f_l \cdot f_i \cdot f_c \cdot L$$
- **Math Flow:** Ensure mathematical variables and inline formulas flow correctly inside RTL Hebrew sentences without getting reversed or broken.

### 3. LaTeX Table Syntax
- **Column separator:** Inside every `tabular` environment, always use `&` (ampersand) to separate columns — NEVER use `|` (pipe). Pipe characters inside a data cell are ordinary text and will not create column breaks.
- **Row terminator:** Every data row must end with `\\`.
- **Correct example:**
  ```
  \begin{tabular}{|l|l|l|}
  \hline
  Column A & Column B & Column C \\
  \hline
  Cell 1   & Cell 2   & Cell 3   \\
  \hline
  \end{tabular}
  ```
- **References section:** Do NOT emit a raw reference list, a `filecontents` bib, or a `\printbibliography`. The bibliography is generated and printed automatically by the pipeline. Just write `\section{רשימת מקורות}` (or omit it entirely) and leave the rest to the pipeline. Cite sources inline with `\cite{key}` or numeric `[1]` markers.

### 5. Figures and Images
- Include at least one real figure via `\includegraphics{...}`. The pipeline generates topic-relevant figures into `assets/` (`assets/star_field.pdf`, `assets/uap_distribution.pdf`, `assets/belief_network.pdf`) — reference one of these. Do **not** use placeholder names like `example-image-a`.

### 4. Accurate TikZ Block Diagram Syntax
- **Valid Compilation:** All TikZ diagrams must contain syntactically flawless code. No missing semicolons, unmatched braces, or invalid node shapes.
- **Packages:** Ensure the document preamble includes `\usepackage{tikz}` and necessary TikZ libraries (e.g., `shapes.geometric`, `arrows.meta`, `positioning`).
- **Styling:** Use clean, professional styling (e.g., defined block styles, readable coordinates, clear arrow links) suitable for a scientific/engineering academic paper.
