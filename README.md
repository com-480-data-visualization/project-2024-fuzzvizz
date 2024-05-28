# Project of Data Visualization (COM-480)

| Student's name | SCIPER |
| -------------- | ------ |
| Chibin Zhang   | 355366 |
| Zurab Tsinadze | 351491 |
| Tao Lyu        | 335189 |

## Milestone 3

[Visualization website](https://com-480-data-visualization.github.io/project-2024-fuzzvizz/)

[Data](https://drive.google.com/file/d/1lZv5DLpj0dXu87sElGJx6JzsFVdsAFLA/view?usp=sharing)

[Screencast](./milestone3/fuzzvizz-screencast.mp4)

[Process book](./milestone3/process-book.pdf)

## Milestone 2

[Milestone 2 Report](./milestone2/milestone2.pdf)

[Website Prototype](https://com-480-data-visualization.github.io/project-2024-fuzzvizz/)

## Milestone 1

### Problematic

**Fuzz testing** or fuzzing is an effective software testing technique that repeatedly generates test cases (i.e., software inputs)
and feeds them to the software under testing to trigger bugs. As the key component of fuzz testing, the test case generator constructs
test cases that might reach potential bug-prone code using runtime feedback instead of blind generation. Code coverage is one such
critical runtime feedback. With the collected runtime code overage of each test case, fuzzing testing tools (also known as fuzzers)
select test cases that hit coverage and further modify/mutate them for continuous testing. The intuitions behind the design are that
(1) a test case hits new coverage is highly possible to trigger new coverage by slightly modifying it, and (2) maximizing the code
coverage improves the possibility of finding bugs as no one knows where bugs are hidden. Although fuzzers can achieve higher code
coverage by automatic mutations, they might fail in some complex functions or modules in programs under testing. **To know where
the fuzzers are stuck and why the fuzzers cannot saturate these modules, it would be helpful to develop a visualized and hierarchical
coverage plot that can offer a macro perspective while allowing detailed inspection at the module/function level.**

Further, bugs detected by fuzzers might be caused by the same root cause. Developers are burdened with an excessive manual effort
to address the numerous **duplicated bug reports** fuzzers generate. Instead of manually analyzing these reports, **we propose clustering
bugs semantically based on dimension-reduced embeddings to shed light on the characteristics and root causes of each bug cluster.**

We plan to achieve the following goals at the end of this project:

- Develop a tool, **FuzzVizz**, that can visually display hierarchical coverage and bug clusters.
- Apply FuzzVizz to real-world programs to show its flexibility.
- Conduct a preliminary evaluation with several fuzzing experts to demonstrate its practical utility.

### Dataset

For our study, we chose compilers/interpreters as the programs under testing because their bug reports often include both
root cause descriptions and proof-of-concept exploits, which helps us to fine-tune our visualization results. We scraped bug
issue trackers for nine real-world programs: Chakracore, CPython, Hermes, LuaJIT, MicroPython, MRuby, PHP, Ruby, and Webkit.
Coverage data was obtained by running state-of-the-art fuzzers and analyzing the input corpus on a coverage-instrumented binary.

| Target              | Crawled | Filtered (reports containing PoCs) |
| ------------------- | ------- | ---------------------------------- |
| ChakraCore (JS)     | 6924    | 1646                               |
| JavaScriptCore (JS) | 255143  | 1692                               |
| SpiderMonkey (JS)   | 163172  | 1358                               |
| Hermes (JS)         | 1252    | 329                                |
| LLVM (C)            | 51537   | 1615\*                             |
| GCC (C)             | 86773   | 3033\*                             |
| Lua                 | 189     | 189                                |
| LuaJIT              | 1132    | 364                                |
| CPython             | 114125  | 21226                              |
| MicroPython         | 10988   | 2622                               |
| Ruby                | 17530   | 3272                               |
| MRuby               | 6136    | 2184                               |

\*We haven’t done the PoC extraction and filtering for LLVM/GCC yet, an initial estimation is based on grep.

### Exploratory Data Analysis

Our pre-processing filtered out bug reports lacking proof-of-concept, deeming them either unreproducible
or unrelated to the core program (e.g., build system issues). We collected 229,231 viable bug reports across
the nine programs. Notably, the coverage achieved by cutting-edge fuzzers represented less than 20% of the
total possible coverage, underscoring the need for a tool like FuzzVizz for identifying underexplored code regions.
Because original bug reports may contain noisy information such as system configuration (CPU, OS, memory),
stack backtrace that is helpful for reproducing the bug but not necessarily pointing to the root cause. We use
prompting to obtain a summary of such a report, and then pass the summary together with the PoC to the embedding model.
The embedding obtained this way is cleaner, and empirically results in better semantic clustering.

Here’s the prompt we used for summarization and example output of a summarized report.

#### Prompt:

First, summarize the following bug report. Describe the reported buggy behavior, the expected behavior, and the root cause.
Then, try your best to extract a single self-contained reproducer (a piece of code for the interpreter/compiler). If there is no code at all, fill in the reproducer field with null.

#### Summary:

In ChakraCore version `e79d68a` on Ubuntu 16.04.6 (x86_64), when deleting the `length` property of a
function and then trying to set it as an `accessor` property, assigning a value to the `length` property
does not update it. Instead, the property remains 0, contradicting the expected behavior of updating the
value correctly. This issue has been reproduced by the developer `akroshg` and is due to an Assertion failure
in `ChakraCore/lib/Runtime/Language/CacheOperators.cpp line 178`

#### Reproducer:

```javascript
function testReconfigureAsAccessorProperty(f) {
  var length = 2;
  Object.defineProperty(f, 'length',
	get: function () {
  	return length;
	}
	set: function (v) {
  	length = v;
	}
  )
}
(function testSetOnInstance() {
  function f() {}
  delete f.length;
  testReconfigureAsAccessorProperty(f);
  Object.defineProperty(Function.prototype, 'length', {
	writable: true
  })
  f.length = 123;
  print(f.length); // It should print 123; but print 0
})()


```

### Related work

To the best of our knowledge, no existing works visualize coverage information in a fine-grained approach.
For example, VisFuzz [1] is designed to visualize the explored paths during testing. However, it doesn’t
show the concrete source code line numbers and control flow conditions. Moreover, no existing works tried
to cluster bug reports automatically to analyze their root causes. We took inspiration from BERTopic and a blog post [2].

[1] [VisFuzz](http://www.wingtecher.com/themes/WingTecherResearch/assets/papers/visfuzzASE19r.pdf)

[2] [Combing For Insight in 10,000 Hacker News Posts With Text Clustering](https://txt.cohere.com/combing-for-insight-in-10-000-hacker-news-posts-with-text-clustering/)

## Late policy

- < 24h: 80% of the grade for the milestone
- < 48h: 70% of the grade for the milestone
