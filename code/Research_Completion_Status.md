# Research Completion Status — 2026-11-11

## Completed in this pass

- SEC availability refreshed for 582 mapped records: 536 checked, 46 without a verified CIK. Retrieved/reused 1,641 disclosure texts; 643 newly downloaded. All 1,641 retained text hashes checked.
- Incremental extraction/checklist pass covered all 38,859 canonical research profiles and all 32 general facet definitions. Source references passed structural checks. This is not semantic or factual certification.
- Original 560 targets: 13,387 of 17,920 general fields have retained evidence (74.70%). All research companies: 234,356 of 1,243,488 general fields (18.85%). No profile has all 32 general fields populated.
- Standard industry records cover 258,805 checklist slots, of which 2,319 have excerpts assigned by the limited explicit extraction rules. This denominator includes conditional fields whose applicability still needs review; it is raw checklist coverage, not a validated applicability-adjusted completion rate. Existing detailed/segment extensions remain separate and retained.
- Restricted pseudo-private input snapshot unchanged. No new similarity rankings computed. No training/test split created.
- Website source and a proposed scoring standard uploaded to Barbara069/private-company-comparables-research. The published Public Comps view now labels historical v2 scores and links the proposed method.

## Not complete

- Full cross-source semantic resolution, factual verification, current global-universe source collection and all industry/segment fields remain incomplete.
- LSEG desktop proxy was connection-refused during this pass. Retained LSEG/WRDS/Capital IQ text was reused; no new LSEG/WRDS/news/search batch is claimed.
- Standard extraction examined a bounded leading text window per SEC document (100,000 characters in the incremental pass; some resumed profiles were processed with the earlier 350,000-character window). Entire downloaded texts remain retained for future extraction. Unknown does not mean the rest of the filing contains no answer.
- Industry-specific field weights across all 83 SIC modules are not calibrated. Proposed general/block weights are not the algorithm behind historical scores.
- The 5,600 historical target-candidate pairs have maximum weighted evidence coverage of 75.22%; zero meet the legacy 80% overall threshold, before other review gates. None is certified as a final recommendation.

## Deliverables and publication scope

The updated complete local data remains in `Targets_560.csv.gz` and `Public_Companies.csv.gz`; new SEC full text, filing dates/periods, URLs and hashes are retained in their records. `Extraction_Completeness.csv` lists missing general fields for each company. `Similarity_Completeness_Review.csv` labels historical pairs and their evidence gates. `Similarity_Scoring_Standard.md` contains the proposed weights, formulas and scoring anchors.

Bulk updated company-data bundles from this pass have NOT been pushed to the public GitHub website. Its hosted company evidence remains the retained snapshot; source-code/method updates are published. This report must not be read as certification of live website data freshness.
