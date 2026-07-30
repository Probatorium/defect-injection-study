# Text for the issue in codecheckers/register

Not sent. Alexis opens it. Two things to settle before sending are at the bottom.

---

## Title

```
CODECHECK request: defect injection study of the Stasis apparatus (+ its subject package)
```

## Body

```markdown
### What is being checked

Two small, self-contained repositories that are meant to be read together.

- **Primary: `defect-injection-study`**, the measuring instrument. It injects
  defects by rule into throwaway copies of its subject and measures what each of
  three oracles catches. Every empirical rate in the paper comes from here.
- **Secondary: `minimal-verified-paper`**, the subject. A two-page statistical
  analysis whose every published number is checked against a fresh computation.

Repositories:

- https://github.com/Probatorium/defect-injection-study
- https://github.com/Probatorium/minimal-verified-paper

Licence: MIT, covering code and data, in both repositories.

### Why we are asking

The finding that most needs an independent hand is plain, and we would rather
state it than have it found: **so far the only person who has recomputed these
detection rates is the author.** The predictions were preregistered in the
repository before the data existed, and the ones that failed are reported as
failed, but preregistration constrains the author and does not replace an
independent run. That gap is exactly what CODECHECK closes.

### Requirements

Both repositories:

- Python 3, **standard library only**. No third-party packages, no `pip install`.
- **No network access** at any point.
- No credentials, no data to download.

Run times: the subject package verifies in seconds. The study takes about ten
minutes on twelve cores.

### How to run

**Primary.** Clone the two as siblings, pin the subject to the commit the study
declares, then one command:

```
git clone https://github.com/Probatorium/minimal-verified-paper.git
git clone https://github.com/Probatorium/defect-injection-study.git
cd minimal-verified-paper && git checkout 2ae7cdd
cd ../defect-injection-study && python run_study.py
```

The study **refuses to run** against a different commit of the subject or
against a dirty worktree, and says so rather than proceeding. That is
deliberate: a measurement that silently drifts onto a different subject is worse
than one that stops.

**Secondary.** Note the difference in what is checked out. The study needs the
subject pinned at the commit it declares; the subject's own check runs on its
current head, because `codecheck_run.py` was added after that commit.

```
cd minimal-verified-paper && git checkout main && python codecheck_run.py
```

That asymmetry is deliberate and worth one line: the pin exists so the STUDY
cannot silently measure a different subject, not to freeze the subject itself.

### The manifest, and one thing worth flagging

The study writes its outputs to files, so its manifest is ordinary: two reports,
two raw tables and a comparison. Every published rate can be recomputed from
`results/raw_results.tsv` without rerunning the study.

The subject package is different, and we would rather explain it than have it
look like a workaround. One of its **published design properties is that
verification never writes**: `verify.py` reads the manuscript, compares every
published number against a fresh computation, prints a report and exits 0 or 1.
Taken literally that leaves an empty manifest.

We did not relax the property. `verify.py` is unchanged and still writes
nothing. A separate wrapper, `codecheck_run.py`, runs it as a subprocess and
records what it printed to `codecheck/report.txt`. The artifact in the manifest
is therefore **a transcript of the verification rather than an output of it**.
If you would prefer a different arrangement we are happy to change it; we did it
this way because quietly relaxing a published property is the specific failure
these repositories exist to make harder.

### What a check would establish

- that the reported detection rates are reproduced by someone who is not the author;
- that the checks are load-bearing rather than decorative, which `mutate.py`
  makes directly observable by reporting how many checks die under each mutant;
- that both repositories run from a clean clone with nothing installed.

Thank you for considering it, and for the time either way.
```

---

## Two things to settle before sending

**1. Can one issue cover the pair?** The register appears to work one artifact,
one certificate, one `AAAA-NNN` identifier. Two possibilities and we do not know
which the community prefers:

- **one issue, two certificates.** The two are separate artifacts and one is the
  subject of the other, so a codechecker who runs the study necessarily runs the
  subject as well.
- **two issues.** Cleaner against `register.csv`, at the cost of asking a
  volunteer twice.

**Ask in the issue rather than assume.** The draft above proposes the pair and
says which is primary, which lets the codechecker choose. If the answer is two
issues, split it and keep `defect-injection-study` first: it is the one carrying
the finding that needs an independent hand.

**2. The subject commit.** The issue pins `2ae7cdd`. **Verify that is still the
commit the study declares** before sending: `DECLARED_COMMIT` in `subject.py` is
the authority, and if the two disagree the codechecker hits the refusal on their
first run, which is a bad first impression of a mechanism that is working
correctly.

---

## What is NOT being submitted, and why it is worth saying

`stasis-antecedentes`, the prior-art survey, is **deliberately not submitted**,
and the reason is a result rather than an excuse.

That repository needs network access, and its outputs are **harvested figures**:
numbers obtained from bibliographic services at an instant. They do not
reproduce by construction. A codechecker running it next month would get
different counts **and would be right to**, because the databases will have
changed.

So the repository that documents the class of the harvested figure is the one
that cannot be codechecked. That is not a defect in CODECHECK and not a defect in
the survey: it is the distinction both are about. Worth a sentence in the paper.

---

## Anexo: el segundo punto ya se comprobo, y estaba mal

Al escribir esta nota se comprobo la advertencia en vez de dejarla escrita, y la
advertencia se cumplio.

| | |
|---|---|
| lo que declara `subject.py` | `a3390860c53290271b6d06745fe252bfa7200dac` |
| lo que mandaba hacer el README | checkout de `e6e4250` |

**Un codechecker siguiendo el README habria chocado con el rechazo del estudio en
su primer intento**, y habria concluido que el paquete no corre, cuando lo que
estaba fallando era la instruccion y no el mecanismo. El mecanismo, de hecho,
estaba haciendo exactamente su trabajo: negarse a medir un sujeto distinto del
declarado.

Es envejecimiento silencioso en un artefacto ya publicado. El README fue correcto
el dia que se escribio; el sujeto avanzo despues y **nada obligaba a la
instruccion a avanzar con el**. Ninguna comprobacion del paquete miraba su propio
README.

Corregido en los dos ficheros. Y queda una tarea que este hallazgo hace obvia:
**una comprobacion que compare el commit citado en el README con
`DECLARED_COMMIT`**, para que la instruccion no pueda volver a envejecer sola.
Va a la tanda 09.

---

## Anexo 2: la refijacion, medida en vez de supuesta, y un segundo valor duplicado

### La refijacion no rompio nada, y eso se midio

Mover el pin cambia el sujeto que el estudio declara haber medido, asi que el
estudio se **volvio a correr entero** en vez de razonar que las cifras
aguantarian.

| Fichero | Resultado |
|---|---|
| `results/raw_results.tsv` | **byte a byte identico** |
| `results/study_report.md` | difiere **solo en las dos lineas del commit** |

Los 411 mutantes, sus oraculos y sus muertes son los mismos. `SUBJECT_COMMIT_DECLARED`
y `SUBJECT_COMMIT_FOUND` son lo unico que cambia, que es exactamente lo que tiene
que cambiar.

**Una salvedad sobre el metodo, porque estuve a punto de equivocarme.** La primera
comparacion dio "identico" cuando el estudio **todavia no habia reescrito los
ficheros**. La comparacion era trivialmente cierta. Lo que la salvo fue mirar la
marca de tiempo antes de creerla: una comparacion entre dos cosas que no han
cambiado no dice nada, y se parece mucho a una que si dice algo.

### Y al mirar el log aparecio un segundo valor duplicado sin atar

| | |
|---|---:|
| lo que el README publicaba | **363** mutantes, **3640** ejecuciones |
| lo que el informe computa desde la evidencia | **411** mutantes, **4532** ejecuciones |

**Un codechecker lo habria encontrado en su primera corrida**, y con razon: es
justo lo que un codecheck existe para sacar a la luz. Misma clase que el commit,
distinto disfraz, y encontrado de la misma manera, mirando en vez de fiarse.

El README esta corregido, **nunca el informe**, y las dos cifras estan ahora
atadas por `check_declared_values.py`, que las compara contra el informe generado
desde la evidencia. Tres mutantes mas, tres cazados.
