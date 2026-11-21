
# Project Instructions

## 1. General Context and Required Updates

The following instructions define the required updates and tasks for the project. All tasks must be evaluated and implemented accordingly.

### Nihat – Sionna PRS Configuration

"Şu ana kadar biraz farklı işler yapılmış olsa da bunların toparlanması gerekiyor. Nihat'ın Sionna üzerinde kullandığı PRS sinyali n78 bandında değildi. Ancak Türkiye'deki baz istasyonlarında 5G yayınları genel olarak n78 bandında gerçekleştiriliyor. Bu nedenle kullanılan frekans bandının n78'e göre güncellenmesi gerekiyor.

Bant genişliği de olması gerekenden düşük seçilmiş. Daha önce 15 kHz SCS kullanılmıştı. Türkiye'deki 5G konfigürasyonuna uygun olacak şekilde 100 MHz bant genişliği ve 30 kHz SCS kullanılmalı.

Birkaç farklı PRS konfigürasyonu da denenmeli. Ayrıca PRS kaynakları konumlandırılırken arada bırakılan boş resource block'lar üzerinden veri haberleşmesi yapılabildiği görülüyor. Bu yaklaşım araştırılmalı ve mümkünse simülasyona dahil edilmeli. Bu kaynakların veri haberleşmesinde kullanılmasıyla elde edilen throughput iyileşmesi hesaplanmalı. Gerçek sistem performansını temsil eden throughput değeri bu şekilde elde edilmeli."

### Nihat – Radar Configuration

"Nihat'ın radar kodlarında hedefin radar kesit alanı (RCS) daha önce 3GPP standartlarına uygun olarak belirlenmemişti. Bu değer güncellendi.

Bunun dışında bant genişliği ve PRF/periyot radar performansını etkileyen önemli parametrelerdir. Mevcut kodda 30 MHz bant genişliği kullanılmıştı. Bant genişliği 100 MHz'e çıkarıldığında menzil çözünürlüğünün önemli ölçüde iyileşmesi bekleniyor. Bu değişiklik uygulanmalı ve elde edilen çözünürlük sonuçları karşılaştırılmalı."

## 2. Task Management and Reporting

"Şu anda aklıma gelen başka bir görev bulunmuyor. Öncelikle mevcut görevlerin hızlıca tamamlanmasına odaklanalım. Herkes kendi görevini ne zaman tamamlayabileceğini bildirsin.

Daha sonra tüm çalışmalar birleştirilerek ara rapor hazırlanacak. Eğer yeterli zaman kalırsa ek bir görev daha üstlenilebilecek şekilde çalışmaların mümkün olduğunca hızlı tamamlanması gerekiyor."

## 3. Mandatory Instructions for Claude

### Language and Writing Style

- All generated outputs, including reports, explanations, documentation, comments, and summaries, MUST be written in Turkish.
- An academic and technical writing style MUST be used.
- Passive voice MUST be preferred throughout all generated Turkish text.
- First-person expressions and informal conversational language MUST be avoided.
- Technical terminology, abbreviations, and standard names may remain in English where appropriate.
- Technical explanations MUST be precise, consistent, and supported by relevant calculations or references when necessary.

### Task-Specific Context

- Nihat's tasks MUST be treated as separate but related paragraphs in the project documentation.
- When generating, modifying, or analyzing any output related to Nihat's tasks, the `fatih_task_result/` directory MUST be used as a reference.
- The contents of `fatih_task_result/` MUST be examined before generating Nihat-related outputs.
- Relevant methodologies, assumptions, simulation configurations, results, and naming conventions from Fatih's work MUST be considered to maintain consistency.
- Existing project files and implementations MUST be examined before making modifications.
- Previously completed work MUST NOT be unnecessarily duplicated or overwritten.

### Technical Requirements

- All simulation parameters MUST be explicitly documented.
- Changes in bandwidth, SCS, PRS configuration, resource allocation, and radar parameters MUST be reflected in the relevant simulations.
- Comparisons with previous configurations MUST be provided wherever applicable.
- Throughput, range resolution, and other performance metrics MUST be calculated using technically valid methods.
- Relevant 3GPP specifications MUST be consulted when standard-compliant configurations or parameter values are required.
- Assumptions that are not explicitly defined by a standard MUST be clearly identified.

### Reporting Requirements

- Results MUST be presented in a clear and structured manner.
- Tables, equations, and figures SHOULD be used when they improve technical clarity.
- Simulation results MUST NOT be presented as measured real-world results.
- All generated reports MUST be written in Turkish using passive academic language.
- The final intermediate report MUST integrate the contributions of all tasks while preserving the distinction between Nihat's and Fatih's work.


### Screenshot and Visual Evidence Requirements

- If screenshots, plots, figures, or other visual evidence are required, the exact outputs that need to be captured MUST be explicitly specified.
- The exact commands, scripts, or procedures required to generate each requested output MUST be provided.
- Screenshots MUST NOT be assumed to be captured automatically.
- The user will manually capture the requested screenshots and place them in the appropriate project directory.
- The expected screenshot filenames, output formats, and target directory MUST be specified whenever possible.
- Each requested screenshot MUST be associated with the relevant task, simulation configuration, or result.
- If multiple screenshots are required, they MUST be listed individually with a brief explanation of what each screenshot should demonstrate.


