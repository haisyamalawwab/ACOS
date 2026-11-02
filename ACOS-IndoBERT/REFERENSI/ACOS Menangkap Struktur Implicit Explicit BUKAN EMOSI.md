# The limitation is **real but narrower**: ACOS captures **implicit aspect/opinion structure**, not **emotion triggers or intensity**.

## 1. Introduction

Current ACOS-style fine-grained opinion mining systems do not simply fail at implicit sentiment; they were designed to recover structured aspect, category, opinion, and polarity information even when aspects or opinions are implicit (Cai et al., 2021; Jia et al., 2026). The core limitation is instead that their output schema usually stops at polarity and NULL-marked implicit elements, so they do not explicitly encode discrete emotions, emotional intensity, or the causal trigger spans behind those emotions (Zhang et al., 2024; Han et al., 2023; Mamta & Ekbal, 2023).

That distinction matters because marketing and service research consistently shows that negative valence alone is behaviorally incomplete. Anger, regret, frustration, disappointment, and worry predict different downstream behaviors such as complaining, switching, negative word of mouth, reconciliation, and reduced share of wallet (Harrison-Walker, 2019; Zeelenberg & Pieters, 2004; Nguyen et al., 2024; Le & Ho, 2020). Text-based service research further shows that arousal matters alongside valence: high-arousal complaints are harder to de-escalate and require different response strategies (Herhausen et al., 2022).

So the evidence supports a refined version of the claim: mainstream ABSA and ACOS systems are useful for identifying what is being discussed and whether it is broadly positive or negative, but organizations still lose important behavioral signal when systems omit emotion category, trigger, and intensity layers, especially in implicitly expressed feedback (D'Aniello & Gaeta, 2022; De Geyndt et al., 2022; Attri et al., 2025; Mamta & Ekbal, 2023).


**Figure 1:** Consensus on ACOS emotional coverage limits

## 2. Methods

This review synthesizes research retrieved through Consensus across more than 220 million papers indexed from Semantic Scholar, PubMed, and other scholarly sources. The corpus was screened to connect four literatures relevant to the claim: aspect-based sentiment and ACOS extraction, implicit sentiment and implicit aspect work, emotion-cause and trigger extraction, and customer-behavior studies linking discrete emotions to complaints, switching, and churn-related outcomes.

| Retrieved | Eligible | Included |
|-----------|----------|----------|
| 9.9M | 370 | 100 | 

**Figure 2:** Search funnel for included literature

The search combined ACOS, implicit sentiment, emotion-cause, intensity, complaint, and churn terms to test both the technical and behavioral halves of the claim.

## 3. Results

### 3.1 Key Papers

The corpus is anchored by the ACOS task paper that formalized quadruple extraction with implicit aspects and opinions, by surveys that clarified how underdeveloped implicit ABSA remains, and by customer-behavior studies showing why discrete emotions matter beyond polarity (Cai et al., 2021; Jia et al., 2026; Tubishat et al., 2018; Harrison-Walker, 2019; Zeelenberg & Pieters, 2004).

| Paper | Summary |
|---|---|
| (Cai et al., 2021) | Defines **ACOS** with implicit elements (Cai et al., 2021) |
| (Jia et al., 2026) | Reviews **implicit sentiment** gap in ABSA (Jia et al., 2026) |
| (Harrison-Walker, 2019) | Links **discrete emotions** to behaviors (Harrison-Walker, 2019) |

**Figure 3:** Foundational papers anchoring this review

### 3.2 ACOS Coverage Versus Emotional Coverage

ACOS was introduced to solve a real deficiency in earlier ABSA systems: many review sentences contain implicit aspects or implicit opinions, and standard tasks largely ignored them (Cai et al., 2021; Chaudhary & Neal, 2025). In the original ACOS datasets, 44% of laptop review sentences contained an implicit aspect or implicit opinion, and baseline performance remained modest, with best F1 scores of 0.446 on Restaurant-ACOS and 0.358 on Laptop-ACOS under exact-match evaluation (Cai et al., 2021).

Recent ACOS variants improve implicit extraction, but they still optimize structured sentiment elements rather than human emotion semantics. Prompted, generative, contrastive, distance-aware, and latent-structure models all report gains on implicit ACOS splits, yet their targets remain aspect, category, opinion, and polarity rather than anger, disappointment, arousal, or cause spans (Liu & Zhong, 2023; Li et al., 2023; Nie et al., 2024; Peper & Wang, 2022; Li et al., 2023; Xiong et al., 2023).

### 3.3 Emotion, Cause, and Intensity Alternatives

| Dimension | ABSA/ACOS | Emotion-Cause Work | Dimensional/Emotion ABSA | Citations |
|---|---|---|---|---|
| Primary target | Aspect-polarity structure | Emotion-cause pairs | Emotion class or intensity | (Zhang et al., 2024; Xia & Ding, 2019; Mamta & Ekbal, 2023) |
| Handles implicit emotion | Limited | Explicit goal | Often explicit + implicit | (Wu et al., 2022; Alswaidan & Menai, 2020; Khoshnam & Baraani-Dastjerdi, 2022) |
| Extracts triggers/causes | Usually no | Yes | Rarely | (Attri et al., 2025; Lee et al., 2010; Li et al., 2025) |
| Models intensity | Rarely | Rarely | Yes | (Mamta & Ekbal, 2023; Zhang et al., 2024; Chen et al., 2023) |
| Customer-review focus | Strong | Weak-moderate | Emerging | (Zhang et al., 2024; Guo et al., 2023; De Geyndt et al., 2022) |

The literature already contains partial solutions outside classic ACOS. Emotion-cause pair extraction removes the requirement to pre-annotate an emotion and directly models emotion-cause relations, while newer work extends this to implicit emotions, span-level triplets, conversations, and e-commerce opinion-trigger extraction (Xia & Ding, 2019; Wu et al., 2022; Poria et al., 2020; Attri et al., 2025; Li et al., 2025).

### 3.4 Behavioral Stakes

Discrete-emotion studies consistently reject a pure valence view of customer reactions. Dissatisfaction, disappointment, regret, anger, and frustration have direct and separable effects on customer behavior, above and beyond general dissatisfaction (Zeelenberg & Pieters, 2004; Bougie et al., 2003). Anger is especially consequential: in airline failure it predicts complaints, negative word of mouth, and switching, whereas worry and frustration in that study predicted only negative word of mouth (Nguyen et al., 2024).

High-arousal text also changes service recovery. Social-media complaint work found that more negative high-arousal words reduce the probability of gratitude after a firm response and motivate de-escalation tactics such as active listening and empathy (Herhausen et al., 2022). Churn studies likewise show that adding emotional text features improves prediction, though text alone is not enough and direct evidence for specific anger-versus-disappointment churn pipelines remains limited (Coussement & Van Den Poel, 2009; Coussement et al., 2019; Aljawazneh, 2026).

### Results Timeline

- **2004**
  - 1 paper: (Zeelenberg & Pieters, 2004)
- **2018**
  - 1 paper: (Tubishat et al., 2018)
- **2019**
  - 1 paper: (Harrison-Walker, 2019)
- **2020**
  - 1 paper: (Le & Ho, 2020)
- **2021**
  - 1 paper: (Cai et al., 2021)
- **2022**
  - 4 papers: (Herhausen et al., 2022; D'Aniello & Gaeta, 2022; De Geyndt et al., 2022; Peper & Wang, 2022)
- **2023**
  - 5 papers: (Han et al., 2023; Mamta & Ekbal, 2023; Liu & Zhong, 2023; Li et al., 2023)
- **2024**
  - 3 papers: (Zhang et al., 2024; Nguyen et al., 2024; Nie et al., 2024)
- **2025**
  - 2 papers: (Attri et al., 2025; Chaudhary & Neal, 2025)
- **2026**
  - 1 paper: (Jia et al., 2026)
**Figure 4:** Research timeline, larger markers indicate more citations

### Top Contributors

| Type | Name | Papers |
|------|------|--------|
| Author | Rui Xia | (Cai et al., 2021; Xia & Ding, 2019; Ding et al., 2020) |
| Author | Roman Klinger | (Troiano et al., 2022; Paramita, 2025) |
| Author | Kristof Coussement | (Coussement & Van Den Poel, 2009; Coussement et al., 2019) |
| Journal | *Expert Systems With Applications* | (H. et al., 2019; Li & Xu, 2014; Coussement & Van Den Poel, 2009) |
| Journal | *Journal of Business Research* | (Zeelenberg & Pieters, 2004; Das et al., 2026) |
| Journal | *IEEE Access* | (Maitama et al., 2020; Ahmad et al., 2025) |

**Figure 5:** Authors and journals appearing most frequently

## 4. Discussion

The evidence does not support the strongest version of the prompt. ACOS and related ABSA systems are not blind to implicit targets in general; implicit aspect and implicit opinion modeling is now a major subfield, with multiple dedicated datasets, surveys, and stronger end-to-end models (Jia et al., 2026; Li et al., 2021; Fu et al., 2024; Mar et al., 2023). What they usually remain blind to is the layer between polarity and behavior: appraisal, discrete emotion, trigger span, and intensity (D'Aniello & Gaeta, 2022; Troiano et al., 2022; Zhang et al., 2024).

That narrower critique is well supported. Several papers explicitly argue that sentiment, affect, emotion, and opinion are different constructs requiring different metrics, and customer-service systems such as SentEMO already treat emotion as an additional layer on top of aspect polarity because polarity alone is insufficient for timely intervention (D'Aniello & Gaeta, 2022; De Geyndt et al., 2022). Intensity research is thinner than polarity research, but it is no longer absent: aspect sentiment intensity analysis and dimensional ABSA now model graded valence and arousal at the aspect level (Mamta & Ekbal, 2023; Zhang et al., 2024).

The main weakness of the current literature is integration. The aspect literature, the emotion-cause literature, and the customer-behavior literature largely advance separately. As a result, there is still little direct evidence that a single system can infer an implicit aspect, assign a discrete emotion, recover its trigger, estimate arousal, and show that those outputs improve real decisions such as complaint routing or churn intervention (Attri et al., 2025; Chen et al., 2023; Labat et al., 2023).

| Claim | Evidence Strength | Reasoning | Papers |
|---|---|---|---|
| ACOS improves handling of implicit aspects and opinions relative to earlier ABSA. | Evidence strength: Strong (8/10) | Multiple benchmark papers and surveys agree, with dedicated datasets and repeated model gains. | (Cai et al., 2021; Jia et al., 2026; Chaudhary & Neal, 2025; Kabir et al., 2024) |
| Standard ACOS usually does not encode emotion triggers or intensity. | Evidence strength: Strong (8/10) | Task definitions center on aspect-category-opinion-polarity; separate literatures had to introduce cause and intensity tasks. | (Zhang et al., 2024; Mamta & Ekbal, 2023; Xia & Ding, 2019; Han et al., 2023) |
| Discrete emotions carry behaviorally useful information beyond negative valence. | Evidence strength: Strong (9/10) | Multiple customer-behavior studies show distinct links from anger, regret, frustration, disappointment, and worry to different outcomes. | (Harrison-Walker, 2019; Zeelenberg & Pieters, 2004; Nguyen et al., 2024; Le & Ho, 2020) |
| Text arousal is operationally important for complaint handling. | Evidence strength: Moderate (7/10) | Strong field and experimental complaint evidence, but concentrated in social-media service settings. | (Herhausen et al., 2022) |
| End-to-end systems that jointly model aspect, implicit emotion, cause, and business outcome remain scarce. | Evidence strength: Weak (3/10) | Emerging datasets and prototypes exist, but direct real-world validation across all layers is still sparse. | (Attri et al., 2025; Guo et al., 2023; Peper et al., 2024) |

**Figure 6:** Claims and evidence across the literature

## 5. Conclusion

The literature supports the concern that polarity-only fine-grained systems miss behaviorally meaningful emotional signal, but it does not support the broader claim that systems like ACOS cannot handle implicit content at all. The real gap is not implicit aspect extraction alone; it is the incomplete integration of aspect structure, discrete emotion, trigger/cause extraction, and intensity into decision-relevant customer models.

### Research Gaps

The most important unresolved problem is the gap between what ABSA extracts and what customer-behavior research says firms need. The matrix below maps where the literature concentrates and where it remains thin.

| | Polarity | Discrete Emotion | Cause Span | Arousal | Business Outcome |
|---|---|---|---|---|---|
| ACOS Extraction | 16 papers | No papers | No papers | No papers | No papers |
| Implicit Aspect | 25 papers | 5 papers | No papers | No papers | No papers |
| Emotion Cause | No papers | 12 papers | 18 papers | 1 paper | No papers |
| Customer Behavior | 2 papers | 12 papers | No papers | No papers | 15 papers |
| Intensity Modeling | 4 papers | 4 papers | No papers | 5 papers | 2 papers |

The sparsest area is the intersection of aspect-level extraction with both cause-span recovery and validated business outcomes. ACOS work is strong on structured polarity and implicit element recovery, but usually stops before emotion cause or escalation inference (Cai et al., 2021; Han et al., 2023). Emotion-cause research is technically mature enough to extract triggers, including implicit ones, yet it is rarely connected to product-review ABSA or to churn and support-routing endpoints (Wu et al., 2022; Ding et al., 2020; Poria et al., 2020). Intensity modeling is also emerging but fragmented across dimensional ABSA, service conversations, and helpfulness studies rather than linked to unified customer-risk systems (Mamta & Ekbal, 2023; Zhang et al., 2024; Chen et al., 2023; Li et al., 2020).

### Open Research Questions

Future progress depends less on another small F1 gain on ACOS and more on building validated multi-layer systems.

| Question | Why |
|---|---|
| **Can one model jointly extract aspect, discrete emotion, trigger span, and sentiment intensity from implicit customer feedback?** | This would connect currently separate ABSA, cause extraction, and intensity literatures into a single operational representation. |
| **Do emotion-trigger and arousal features improve complaint routing or churn prediction beyond aspect polarity alone?** | Behavioral studies imply they should, but direct end-to-end validation remains limited and mostly indirect. |
| **Which appraisal dimensions best distinguish support-seeking disappointment from retaliatory anger in service text?** | Appraisal theory offers interpretable structure that could map text to actions more reliably than polarity alone. |

**Figure 7:** Open research questions for next-generation systems

So, current fine-grained opinion mining systems do miss critical emotional triggers and intensity, but the frontier problem is **integration and validation**, not simple failure to process implicit feedback.
 
_These search results were found and analyzed using Consensus, an AI-powered search engine for research. Try it at https://consensus.app. © 2026 Consensus NLP, Inc. Personal, non-commercial use only; redistribution requires copyright holders’ consent._
 
## References
 
Ahmad, W., Khan, H. U., Alarfaj, F., & Alreshoodi, M. (2025). Aspect-Based Sentiment Analysis: A Comprehensive Review and Open Research Challenges. *IEEE Access, 13*, 65138-65182. https://doi.org/10.1109/access.2025.3555744
 
Aljawazneh, H. (2026). Enhancing Telecom Churn Prediction Using Emotion-Driven and Behavioral Engagement Features. *International Journal of Advanced Computer Science and Applications*. https://doi.org/10.14569/ijacsa.2026.0170284
 
Alswaidan, N., & Menai, M. E. B. (2020). A survey of state-of-the-art approaches for emotion recognition in text. *Knowledge and Information Systems, 62*, 2937-2987. https://doi.org/10.1007/s10115-020-01449-0
 
Attri, A., Attri, A., Bhattacharyya, P., Banerjee, S., Patil, A., Chelliah, M., & Garera, N. (2025). Why We Feel What We Feel: Joint Detection of Emotions and Their Opinion Triggers in E-commerce. *ArXiv, abs/2507.04708*. https://doi.org/10.48550/arxiv.2507.04708
 
Bougie, R., Pieters, R., & Zeelenberg, M. (2003). Angry customers don't come back, they get back: The experience and behavioral implications of anger and dissatisfaction in services. *Journal of the Academy of Marketing Science, 31*, 377-393. https://doi.org/10.1177/0092070303254412
 
Cai, H., Xia, R., & Yu, J.-F. (2021). Aspect-Category-Opinion-Sentiment Quadruple Extraction with Implicit Aspects and Opinions. 340-350. https://doi.org/10.18653/v1/2021.acl-long.29
 
Chaudhary, M., & Neal, T. J. (2025). Implicit Aspect Extraction: A Systematic Review. *ACM Computing Surveys, 58*, 1 - 36. https://doi.org/10.1145/3786590
 
Chen, D., Huang, Z.-W., Tan, Y., Min, J., & Khanal, R. (2023). Emotion and sentiment analysis for intelligent customer service conversation using a multi-task ensemble framework. *Cluster Computing, 27*, 2099-2115. https://doi.org/10.1007/s10586-023-04073-z
 
Coussement, K., & Van Den Poel, D. (2009). Improving customer attrition prediction by integrating emotions from client/company interaction emails and evaluating multiple classifiers. *Expert Syst. Appl., 36*, 6127-6134. https://doi.org/10.1016/j.eswa.2008.07.021
 
Coussement, K., De Bock, K. D., & Lessmann, S. (2019). Incorporating textual information in customer churn prediction models based on a convolutional neural network. *International Journal of Forecasting, 36*, 1563-1578. https://doi.org/10.1016/j.ijforecast.2019.03.029
 
D'Aniello, G., & Gaeta, M. (2022). KnowMIS-ABSA: an overview and a reference model for applications of sentiment analysis and aspect-based sentiment analysis. *Artificial Intelligence Review, 55*, 5543 - 5574. https://doi.org/10.1007/s10462-021-10134-9
 
Das, M., Jebarajarkirthy, C., Maseeh, H. I., Lim, W. M., & Shah, J. (2026). Online service failure and recovery: An integrated meta-analytic perspective of attribution and justice theories. *Journal of Business Research*. https://doi.org/10.1016/j.jbusres.2025.115752
 
De Geyndt, E., De Clercq, O., Van Hee, C., Lefever, E., Singh, P., Parent, O., & Hoste, V. (2022). SentEMO: A Multilingual Adaptive Platform for Aspect-based Sentiment and Emotion Analysis. 51-61. https://doi.org/10.18653/v1/2022.wassa-1.5
 
Ding, Z., Xia, R., & Yu, J.-F. (2020). ECPE-2D: Emotion-Cause Pair Extraction based on Joint Two-Dimensional Representation, Interaction and Prediction. 3161-3170. https://doi.org/10.18653/v1/2020.acl-main.288
 
Fu, J., Li, X.-Y., Zhu, Y., Du, Y.-J., Fan, Y., Chen, X.-L., Huang, D., & Wang, S. (2024). An implicit aspect-based sentiment analysis method using supervised contrastive learning and knowledge embedding. *Appl. Soft Comput., 167*, 112233. https://doi.org/10.1016/j.asoc.2024.112233
 
Guo, Q.-T., Yu, J., Zhang, Y., Jiang, H., Liu, W., & Yin, J. (2023). Discovery of Emotion Implicit Causes in Products Based on Commonsense Reasoning. 277-292. https://doi.org/10.1007/978-3-031-46661-8_19
 
H., H., Prasad, P., Maag, A., & Alsadoon, A. (2019). Deep Learning for Aspect-Based Sentiment Analysis: A Comparative Review. *Expert Syst. Appl., 118*, 272-299. https://doi.org/10.1016/j.eswa.2018.10.003
 
Han, Y., Bruggeman, R., Peper, J., Chehade, E. C., Marion, T., Ciuccarelli, P., & Moghaddam, M. (2023). EXTRACTING LATENT NEEDS FROM ONLINE REVIEWS THROUGH DEEP LEARNING BASED LANGUAGE MODEL. *Proceedings of the Design Society, 3*, 1855 - 1864. https://doi.org/10.1017/pds.2023.186
 
Harrison-Walker, L. J. (2019). The effect of consumer emotions on outcome behaviors following service failure. *Journal of Services Marketing*. https://doi.org/10.1108/jsm-04-2018-0124
 
Herhausen, D., Grewal, L., Cummings, K. H., Roggeveen, A. L., Ordenes, F. V., & Grewal, D. (2022). Complaint De-Escalation Strategies on Social Media. *Journal of Marketing, 87*, 210 - 231. https://doi.org/10.1177/00222429221119977
 
Jia, W., Jing, S., Wang, J., & Zhang, M. (2026). Implicit Aspect-Based Sentiment Analysis: A Systematic Review. *ACM Comput. Surv., 58*, 262:1-262:37. https://doi.org/10.1145/3799234
 
Kabir, M. M., Othman, Z., & Yaakub, M. R. (2024). A Hybrid Frequency Based, Syntax, and Conditional Random Field Method for Implicit and Explicit Aspect Extraction. *IEEE Access, 12*, 72361-72373. https://doi.org/10.1109/access.2024.3403479
 
Khoshnam, F., & Baraani-Dastjerdi, A. (2022). A dual framework for implicit and explicit emotion recognition: An ensemble of language models and computational linguistics. *Expert Syst. Appl., 198*, 116686. https://doi.org/10.1016/j.eswa.2022.116686
 
Labat, S., Demeester, T., & Hoste, V. (2023). EmoTwiCS: a corpus for modelling emotion trajectories in Dutch customer service dialogues on Twitter. *Language Resources and Evaluation*, 1-42. https://doi.org/10.1007/s10579-023-09700-0
 
Le, A., & Ho, H. (2020). The Behavioral Consequences of Regret, Anger, and Frustration in Service Settings. *Journal of Global Marketing, 33*, 102 - 84. https://doi.org/10.1080/08911762.2019.1628330
 
Lee, S., Chen, Y., & Huang, C.-R. (2010). A Text-driven Rule-based System for Emotion Cause Detection. 45-53.
 
Li, S., Zhang, Y.-Q., Lan, Y., Zhao, H., & Zhao, G. (2023). From Implicit to Explicit: A Simple Generative Method for Aspect-Category-Opinion-Sentiment Quadruple Extraction. *2023 International Joint Conference on Neural Networks (IJCNN)*, 1-8. https://doi.org/10.1109/ijcnn54540.2023.10191098
 
Li, J., Li, X.-Y., Du, Y.-J., Fan, Y., Chen, X.-L., & Huang, D. (2023). An Aspect-Category-Opinion-Sentiment Quadruple Extraction with Distance Information for Implicit Sentiment Analysis. *Inf. Technol. Control., 52*, 445-456. https://doi.org/10.5755/j01.itc.52.2.32903
 
Li, X., Yang, D., Zhu, X.-G., Huang, F., Zhang, P., & Zhao, Z. (2025). Span-level Emotion-Cause-Category Triplet Extraction with Instruction Tuning LLMs and Data Augmentation. *Appl. Soft Comput., 185*, 113938. https://doi.org/10.48550/arxiv.2504.12331
 
Li, Z., Zou, Y., Zhang, C., Zhang, Q., & Wei, Z.-Y. (2021). Learning Implicit Sentiment in Aspect-based Sentiment Analysis with Supervised Contrastive Pre-Training. 246-256. https://doi.org/10.18653/v1/2021.emnlp-main.22
 
Li, H.-Y., Liu, H., & Zhang, Z.-L. (2020). Online persuasion of review emotional intensity: A text mining analysis of restaurant reviews. *International Journal of Hospitality Management, 89*, 102558. https://doi.org/10.1016/j.ijhm.2020.102558
 
Li, W., & Xu, H. (2014). Text-based emotion classification using emotion cause extraction. *Expert Syst. Appl., 41*, 1742-1749. https://doi.org/10.1016/j.eswa.2013.08.073
 
Liu, Y., & Zhong, J. (2023). Implicit Sentiment Extraction Using Structure Generation with Sentiment Instructor Prompt Template. 94-108. https://doi.org/10.1007/978-3-031-46674-8_7
 
Maitama, J. Z., Idris, N., Abdi, A., Shuib, L., & Fauzi, R. (2020). A Systematic Review on Implicit and Explicit Aspect Extraction in Sentiment Analysis. *IEEE Access, 8*, 194166-194191. https://doi.org/10.1109/access.2020.3031217
 
Mamta, M., & Ekbal, A. (2023). Service Is Good, Very Good or Excellent? Towards Aspect Based Sentiment Intensity Analysis. 685-700. https://doi.org/10.1007/978-3-031-28244-7_43
 
Mar, A. A., Shirai, K., & Kertkeidkachorn, N. (2023). Weakly Supervised Learning Approach for Implicit Aspect Extraction. *Inf., 14*, 612. https://doi.org/10.3390/info14110612
 
Nguyen, H. N., Nguyen, L. T., Vo, L., & Luu, D. X. (2024). Customer Responses to Airline Service Failure: Perspectives from Expectation Disconfirmation Theory. *SAGE Open, 14*. https://doi.org/10.1177/21582440241248334
 
Nie, Y., Fu, J., Zhang, Y.-L., & Li, C. (2024). Modeling implicit variable and latent structure for aspect-based sentiment quadruple extraction. *Neurocomputing, 586*, 127642. https://doi.org/10.1016/j.neucom.2024.127642
 
Paramita, A. (2025). Fine-Grained Sentiment Analysis Approach on Customer Reviews Based on Aspect-Level Emotion Detection. *Journal of Applied Data Sciences*. https://doi.org/10.47738/jads.v6i3.964
 
Peper, J., & Wang, L. (2022). Generative Aspect-Based Sentiment Analysis with Contrastive Learning and Expressive Structure. *ArXiv, abs/2211.07743*. https://doi.org/10.48550/arxiv.2211.07743
 
Peper, J., Qiu, W., Bruggeman, R., Han, Y., Chehade, E., & Wang, L. (2024). Shoes-ACOSI: A Dataset for Aspect-Based Sentiment Analysis with Implicit Opinion Extraction. 15477-15490. https://doi.org/10.18653/v1/2024.findings-emnlp.907
 
Poria, S., Majumder, N., Hazarika, D., Ghosal, D., Bhardwaj, R., Yu, S., Hong, P., Ghosh, R., Chhaya, N., Gelbukh, A., & Mihalcea, R. (2020). Recognizing Emotion Cause in Conversations. *Cognitive Computation, 13*, 1317 - 1332. https://doi.org/10.1007/s12559-021-09925-7
 
Troiano, E., Oberländer, L., & Klinger, R. (2022). Dimensional Modeling of Emotions in Text with Appraisal Theories: Corpus Creation, Annotation Reliability, and Prediction. *Computational Linguistics, 49*, 1-72. https://doi.org/10.1162/coli_a_00461
 
Tubishat, M., Idris, N., & Abushariah, M. (2018). Implicit aspect extraction in sentiment analysis: Review, taxonomy, oppportunities, and open challenges. *Inf. Process. Manag., 54*, 545-563. https://doi.org/10.1016/j.ipm.2018.03.008
 
Wu, C.-H., Shi, S.-M., Hu, J., & Huang, H.-Y. (2022). Knowledge-enriched joint-learning model for implicit emotion cause extraction. *CAAI Trans. Intell. Technol., 8*, 118-128. https://doi.org/10.1049/cit2.12099
 
Xia, R., & Ding, Z. (2019). Emotion-Cause Pair Extraction: A New Task to Emotion Analysis in Texts. 1003-1012. https://doi.org/10.18653/v1/p19-1096
 
Xiong, H., Yan, Z., Wu, C., Lu, G., Pang, S., Xue, Y., & Cai, Q. (2023). BART-based contrastive and retrospective network for aspect-category-opinion-sentiment quadruple extraction. *International Journal of Machine Learning and Cybernetics, 14*, 3243-3255. https://doi.org/10.1007/s13042-023-01831-8
 
Zeelenberg, M., & Pieters, R. (2004). Beyond valence in customer dissatisfaction: A review and new findings on behavioral responses to regret and disappointment in failed services. *Journal of Business Research, 57*, 445-455. https://doi.org/10.1016/s0148-2963(02)00278-3
 
Zhang, H., Cheah, Y., Alyasiri, O. M., & An, J.-Y. (2024). Exploring aspect-based sentiment quadruple extraction with implicit aspects, opinions, and ChatGPT: a comprehensive survey. *Artificial Intelligence Review, 57*. https://doi.org/10.1007/s10462-023-10633-x
 
Zhang, Y., Wang, J., Xu, D., & Zhang, X.-J. (2024). YNU-HPCC at SIGHAN-2024 dimABSA Task: Using PLMs with a Joint Learning Strategy for Dimensional Intensity Prediction. *Proceedings of the 10th SIGHAN Workshop on Chinese Language Processing (SIGHAN-10)*. https://doi.org/10.18653/v1/2024.sighan-1.11
 
