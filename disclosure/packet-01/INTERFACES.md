# Scorer interface inventory

Pinned source: inspect_evals `e3402e36c6c1c161797a8b8e7ebbffca05e47fea`.

Static extractor-level findings. The 36/68 count is not a live failure rate. Imported means the parser was executed directly; other rows use a source-checked equivalent. Paths beginning with inspect_ai refer to its separately pinned revision in interfaces.json.

| Package | Scorer | File and line | Selection | Static category | Direct import |
| --- | --- | --- | --- | --- | --- |
| mask | mask.scorer (honesty / accuracy), statements | inspect_evals/src/inspect_evals/mask/judge_estimate/parse.py:55-96 | first | earlier-quote override | True |
| mask | mask.scorer (honesty / accuracy), beliefs | inspect_evals/src/inspect_evals/mask/judge_estimate/parse.py:55-96 | first | earlier-quote override | True |
| mask | mask.scorer (honesty / accuracy), beliefs | inspect_evals/src/inspect_evals/mask/judge_estimate/parse.py:25-52 | first_valid | earlier-quote override | True |
| abstention_bench | abstention_bench_scorer | inspect_evals/src/inspect_evals/abstention_bench/utils.py:197-217 | last | terminal/last wins | False |
| air_bench | air_bench_scorer | inspect_evals/src/inspect_evals/air_bench/air_bench.py:123-188 | terminal_line | terminal/last wins | False |
| cyberseceval_2 | model_graded_qa(template=PROMPT_JUDGE_RESPONSE) | inspect_evals/src/inspect_evals/cyberseceval_2/interpreter_abuse/task.py:63-63 | last | terminal/last wins | False |
| cyberseceval_2 | model_graded_qa(template=PROMPT_JUDGE_RESPONSE) | inspect_evals/src/inspect_evals/cyberseceval_2/prompt_injection/task.py:61-61 | last | terminal/last wins | False |
| cyberseceval_3 | model_graded_qa(template=PROMPT_JUDGE_RESPONSE) | inspect_evals/src/inspect_evals/cyberseceval_3/visual_prompt_injection/task.py:68-68 | last | terminal/last wins | False |
| cyberseceval_4 | prompt_injection_scorer | inspect_evals/src/inspect_evals/cyberseceval_4/multilingual_prompt_injection/scorers.py:15-22 | last | terminal/last wins | False |
| fortress | fortress_scorer_benign | inspect_evals/src/inspect_evals/fortress/scorer.py:259-260 | last | terminal/last wins | False |
| frontierscience | frontierscience_scorer (olympic format) | inspect_evals/src/inspect_evals/frontierscience/frontierscience.py:122-125 | last | terminal/last wins | False |
| ipi_coding_agent | _check_detection (inside the ipi scorer) | inspect_evals/src/inspect_evals/ipi_coding_agent/scorer.py:194-213 | last | terminal/last wins | False |
| uccb | model_graded_qa(template=UCCB_GRADING_TEMPLATE) | inspect_evals/src/inspect_evals/uccb/uccb.py:110-113 | last | terminal/last wins | False |
| mmmu | model_graded_fact() | inspect_evals/src/inspect_evals/mmmu/mmmu.py:85-85 | last | terminal/last wins | False |
| anima | anima scorer (per dimension x variable set x grader) | inspect_evals/src/inspect_evals/anima/scorer.py:215-223 | last | terminal/last wins | False |
| moru | moru scorer (per dimension x grader) | inspect_evals/src/inspect_evals/moru/scorer.py:96-103 | last | terminal/last wins | False |
| sciknoweval | model_graded_fact (GEN_filling tasks) | inspect_evals/src/inspect_evals/sciknoweval/config.py:6-6 | last | terminal/last wins | False |
| xstest | model_graded_qa(template, instructions=scorer_instructions) | inspect_evals/src/inspect_evals/xstest/xstest.py:91-95 | last | terminal/last wins | False |
| coconot | model_graded_qa (grade_parse="strict", default) | inspect_evals/src/inspect_evals/coconot/scorer.py:28-29 | last | terminal/last wins | False |
| coconot | model_graded_qa (grade_parse="strict", default) | inspect_evals/src/inspect_evals/coconot/scorer.py:28-29 | last | terminal/last wins | False |
| coconot | coconot_paper_scorer (grade_parse="paper") | inspect_evals/src/inspect_evals/coconot/scorer.py:32-70 | first | earlier-quote override | True |
| coconot | coconot_paper_scorer (grade_parse="paper") | inspect_evals/src/inspect_evals/coconot/scorer.py:32-70 | first | earlier-quote override | True |
| fortress | fortress_scorer_adversarial (get_adversarial_scorer) | inspect_evals/src/inspect_evals/fortress/scorer.py:31-48 | first_valid | earlier-quote override | False |
| frontierscience | research_scorer | inspect_evals/src/inspect_evals/frontierscience/frontierscience.py:204-236 | first_valid | earlier-quote override | False |
| hle | regex_judge | inspect_evals/src/inspect_evals/hle/prompts.py:65-76 | last | terminal/last wins | False |
| hle | json_judge (default HLE judge) | inspect_evals/src/inspect_evals/hle/scorers.py:102-163 | whole_reply | structured/other | False |
| writingbench | multi_scorer_wrapper (5 x model_graded_qa) | inspect_evals/src/inspect_evals/writingbench/writingbench.py:121-136 | first_valid | earlier-quote override | False |
| niah | custom_model_graded_qa_with_history_scorer | inspect_evals/src/inspect_evals/niah/utils/scoring.py:183-199 | first_valid | earlier-quote override | False |
| sciknoweval | model_graded_mcq (GEN_MCQ tasks) | inspect_evals/src/inspect_evals/sciknoweval/scorer.py:72-94 | first_valid | earlier-quote override | False |
| sciknoweval | model_graded_score (GEN_SCORE tasks) | inspect_evals/src/inspect_evals/sciknoweval/scorer.py:116-135 | first | earlier-quote override | False |
| sciknoweval | model_graded_tf (GEN_TF tasks) | inspect_evals/src/inspect_evals/sciknoweval/scorer.py:158-173 | priority | earlier-quote override | False |
| agentharm | combined_scorer (RefusalJudgeLLM.check_refusal) | inspect_evals/src/inspect_evals/agentharm/scorer.py:49-67 | first | earlier-quote override | False |
| agentharm | grading functions via semantic_judge | inspect_evals/src/inspect_evals/agentharm/benchmark/grading_utils.py:19-35 | whole_reply | structured/other | False |
| agentic_misalignment | harmfulness_scorer (blackmail scenarios) | inspect_evals/src/inspect_evals/agentic_misalignment/classifiers/blackmail_classifier.py:70-97 | first | earlier-quote override | True |
| agentic_misalignment | harmfulness_scorer (leaking scenarios) | inspect_evals/src/inspect_evals/agentic_misalignment/classifiers/leak_classifier.py:85-114 | first | earlier-quote override | True |
| agentic_misalignment | harmfulness_scorer (murder scenarios) | inspect_evals/src/inspect_evals/agentic_misalignment/classifiers/murder_classifier.py:74-101 | first | earlier-quote override | True |
| agentic_misalignment | eval_awareness_scorer | inspect_evals/src/inspect_evals/agentic_misalignment/classifiers/deliberation_classifier.py:73-105 | first | earlier-quote override | True |
| b3 | judge defense guardrail (get_judge_cost), not a Scorer | inspect_evals/src/inspect_evals/b3/judge_defense.py:22-49 | single_marker | structured/other | False |
| b3 | sexual content metric (make_sexual_context_judge) | inspect_evals/src/inspect_evals/b3/metrics.py:441-465 | whole_reply | structured/other | False |
| browse_comp | browse_comp_scorer | inspect_evals/src/inspect_evals/browse_comp/browse_comp.py:214-249 | first_valid | earlier-quote override | False |
| cti_realm | cti_realm scorer (_score_sigma_rule) | inspect_evals/src/inspect_evals/cti_realm/core/scorer.py:169-203 | first_valid | earlier-quote override | False |
| cti_realm | cti_realm trajectory scorer (_score_cti_threat_alignment) | inspect_evals/src/inspect_evals/cti_realm/core/trajectory_scorer.py:241-252 | first_valid | earlier-quote override | True |
| cyberseceval_4 | mitre_scorer (judge after expansion) | inspect_evals/src/inspect_evals/cyberseceval_4/mitre/scorers.py:186-205 | priority | earlier-quote override | False |
| cyberseceval_4 | autopatching scorer | inspect_evals/src/inspect_evals/cyberseceval_4/autopatching/scorers.py:144-165 | structured | earlier-quote override | False |
| cyberseceval_4 | autonomous_uplift scorer | inspect_evals/src/inspect_evals/cyberseceval_4/autonomous_uplift/scorers.py:136-158 | structured | earlier-quote override | False |
| cyberseceval_4 | multiturn_phishing scorer (per attribute) | inspect_evals/src/inspect_evals/cyberseceval_4/multiturn_phishing/scorers.py:146-159 | structured | earlier-quote override | False |
| gdm_stealth | rater_lib.rate_and_parse_with_retry (checkers inside the environments) | inspect_evals/src/inspect_evals/gdm_stealth/rater_lib.py:13-31 | single_marker | structured/other | False |
| gdm_stealth | oversight ticket_review via llm_sample_dict | inspect_evals/src/inspect_evals/gdm_stealth/solver/strategic_rule_breaking/llm_sampling.py:26-70 | last | terminal/last wins | False |
| gdm_stealth | llm_sample_multiple_choice (user satisfaction, message classifiers) | inspect_evals/src/inspect_evals/gdm_stealth/solver/strategic_rule_breaking/llm_sampling.py:128-144 | first | earlier-quote override | False |
| healthbench | healthbench_scorer (_evaluate_criterion per rubric item) | inspect_evals/src/inspect_evals/healthbench/scorer.py:100-116 | whole_reply | structured/other | False |
| instrumentaleval | instrumentaleval_scorer | inspect_evals/src/inspect_evals/instrumentaleval/scorer.py:64-93 | last | terminal/last wins | True |
| math | math expression equivalence (grader model branch) | inspect_evals/src/inspect_evals/math/utils.py:94-102 | last | terminal/last wins | False |
| agieval | expression_equivalence | inspect_evals/src/inspect_evals/agieval/utils.py:236-247 | whole_reply | structured/other | False |
| persistbench | persistbench_judge | inspect_evals/src/inspect_evals/persistbench/scorers.py:82-106 | first | earlier-quote override | True |
| simpleqa | simpleqa_scorer(grade_parse="strict") | inspect_evals/src/inspect_evals/simpleqa/scorer.py:118-124 | first_valid | earlier-quote override | False |
| simpleqa | simpleqa_scorer(grade_parse="paper") | inspect_evals/src/inspect_evals/simpleqa/scorer.py:118-124 | first_valid | earlier-quote override | False |
| simpleqa | simpleqa_schema_tool_scorer (default) | inspect_evals/src/inspect_evals/simpleqa/scorer.py:141-167 | structured | structured/other | False |
| vqa_rad | vqa_rad scorer (open-ended questions) | inspect_evals/src/inspect_evals/vqa_rad/scorer.py:102-125 | structured | structured/other | False |
| sosbench | llm_judge_scorer | inspect_evals/src/inspect_evals/sosbench/sosbench.py:100-116 | whole_reply | structured/other | False |
| strong_reject | strong_reject_scorer | inspect_evals/src/inspect_evals/strong_reject/utils.py:48-74 | first | earlier-quote override | True |
| sycophancy | sycophancy_scorer (admit_mistake) | inspect_evals/src/inspect_evals/sycophancy/scorers.py:27-48 | priority | earlier-quote override | False |
| sycophancy | sycophancy_scorer (grade_freeform_question) | inspect_evals/src/inspect_evals/sycophancy/scorers.py:51-75 | priority | earlier-quote override | False |
| theagentcompany | _judge_one / run_llm_judge_items and four task evaluators | inspect_evals/src/inspect_evals/theagentcompany/common_evaluators.py:967-971 | first | earlier-quote override | False |
| theagentcompany | hr_create_employee_manual and ml_generate_gradcam evaluators | inspect_evals/src/inspect_evals/theagentcompany/tasks/hr_create_employee_manual/evaluator.py:80-81 | priority | earlier-quote override | False |
| makemesay | judge_user_awareness (game outcome) | inspect_evals/src/inspect_evals/makemesay/game.py:372-386 | first_valid | earlier-quote override | False |
| ape | ape_conversation evaluator turn (extract_rating) | inspect_evals/src/inspect_evals/ape/utils.py:16-16 | terminal_line | earlier-quote override | True |
| ape | ape_conversation StrongREJECT turn check | inspect_evals/src/inspect_evals/ape/utils.py:29-46 | first_valid | earlier-quote override | False |
| paperbench | SimpleJudge (_parse_response_by_llm) | inspect_evals/src/inspect_evals/paperbench/score/simple_judge.py:760-798 | whole_reply | not applicable | False |
