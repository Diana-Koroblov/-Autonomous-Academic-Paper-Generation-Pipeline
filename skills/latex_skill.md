# LaTeX Production & Compilation Protocol (latex_skill.md)

## Objective and Role
The LaTeX Agent is tasked with compiling draft Hebrew Markdown documents into publishable, professional TeX source, and structuring its configurations to yield a flawless multi-page PDF output using LuaLaTeX.

## Core Mandates

### 1. Bidirectional (BiDi) Engine Packages
- **LuaLaTeX Target:** The document must use `LuaLaTeX` for native RTL (Right-to-Left) Hebrew and LTR (Left-to-Right) English bidirectional text mixing.
- **RTL Setup:** Explicitly import and configure standard packages:
  - `polyglossia` or `babel` with Hebrew as the primary language and English as a secondary language.
  - Correct bidirectional font configurations using `fontspec` (e.g., using a system Hebrew font like David CLM or Arial).
  - Explicit direction commands (`\setcode{utf8}`, `\setmainlanguage{hebrew}`, `\setotherlanguage{english}`).

### 2. Math Notation Layout
- **Academic Precision:** Format all math operators, equations, and expressions using standard TeX mathematical environments (`equation`, `align`, `gather`).
- **The Drake Equation:** Render the legendary Drake Equation with full elegance using nested math blocks, with each variable explicitly explained using standard LaTeX tables:
  $$N = R_* \cdot f_p \cdot n_e \cdot f_l \cdot f_i \cdot f_c \cdot L$$
- **Math Flow:** Ensure mathematical variables and inline formulas flow correctly inside RTL Hebrew sentences without getting reversed or broken.

### 3. Accurate TikZ Block Diagram Syntax
- **Valid Compilation:** All TikZ diagrams must contain syntactically flawless code. No missing semicolons, unmatched braces, or invalid node shapes.
- **Packages:** Ensure the document preamble includes `\usepackage{tikz}` and necessary TikZ libraries (e.g., `shapes.geometric`, `arrows.meta`, `positioning`).
- **Styling:** Use clean, professional styling (e.g., defined block styles, readable coordinates, clear arrow links) suitable for a scientific/engineering academic paper.
